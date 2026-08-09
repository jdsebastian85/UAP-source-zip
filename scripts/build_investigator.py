#!/usr/bin/env python3
"""Build the investigator tool: a single-file working app over the spine.

Usage: python3 scripts/build_investigator.py [--out investigate.html]

Distinct from build_site.py. That one builds the public credibility artifact and
must never carry a Drive link. This one is the owner's working tool and leads
with them, because its job is to open a file in one tap.

Page text is not embedded. The text layer is 27 MB and would make the app
unusable on a phone, so the build emits a byte-offset index into
spine/pages.jsonl and the app pulls one page at a time with an HTTP Range
request. The index is validated at read time against the release and page it
claims to point at, so a stale index reports itself rather than showing text
from the wrong page.

Every displayed value traces to a spine row. Nothing is derived or inferred.

CONFIDENCE FLOOR: 60 (tesseract word confidence, 0-100).

That number is published, not tuned in private. Words scoring below it are kept
in ocr_recovered.csv with their score and are rendered as [unclear] rather than
as confident-looking text. The OCR pass that writes the file must use the same
floor for its entity-extraction cutoff: per T2.3, only words at or above the
floor may reach Layer 3, because low-confidence OCR fed into the entity index
manufactures names that were never on the page.

ocr_recovered.csv is read in either shape:
  page-per-row  release_id, pdf_page, ocr_text, ocr_char_count      (current)
  word-per-row  release_id, pdf_page, word_no, word_verbatim, conf,
                bbox, source_tag                                    (T2.3)
Word rows are not embedded — at 2,537 pages they are the same order of size as
the text layer. They are byte-indexed and fetched a page at a time, exactly
like pages.jsonl.
"""
import argparse, csv, json, os, re, glob, subprocess
from collections import defaultdict
from datetime import date

SPINE = os.environ.get("SPINE", "spine")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CONF_FLOOR = 60          # see module docstring; published, not private
REDACTION_TOKEN = "[REDACTED]"


def year(*s):
    m = re.findall(r"(19[4-9]\d|20[0-2]\d)", " ".join(s))
    return m[0] if m else ""


def family(rid):
    if rid.startswith("video_2605"):
        return "video_2605 — edited presentation products"
    for k, lab in (("111830", "DOD_111830 — sensor / FLIR"),
                   ("111887", "DOD_111887 — optical scope"),
                   ("111764", "DOD_111764 — handheld"),
                   ("111688", "DOD_111688 — ISR"),
                   ("111689", "DOD_111689 — ISR")):
        if k in rid:
            return lab
    return "other"


def sp(name):
    return os.path.join(SPINE, name)


def git_build():
    """Stamp the corpus state the marks were made against.

    `commit` is HEAD at build time, so a build run before committing its own
    changes points at the parent commit; `dirty` says whether the tree had
    uncommitted changes. Together they answer the only question that matters
    on import six months later: did the corpus move under these notes.
    """
    def run(*a):
        try:
            return subprocess.run(a, cwd=ROOT, capture_output=True,
                                  text=True, timeout=10).stdout.strip()
        except Exception:
            return ""
    return {"commit": run("git", "rev-parse", "--short", "HEAD") or "unknown",
            "dirty": bool(run("git", "status", "--porcelain")),
            "built": date.today().isoformat()}


def build_ocr_index():
    """Byte-index ocr_recovered.csv by (release_id, pdf_page).

    Returns (fmt, header_line, index) where index maps release_id to
    [pdf_page, byte_offset, byte_length, mean_conf_or_None, low_word_count].

    Rows for a page must be contiguous. If a page's rows are split by another
    page's rows the file cannot be range-fetched a page at a time, and this
    raises rather than indexing a fragment and calling it the page.
    """
    path = sp("ocr_recovered.csv")
    if not os.path.exists(path):
        return "none", "", {}

    data = open(path, "rb").read()
    records = list(iter_records(data))
    if not records:
        return "none", "", {}

    hoff, hlen = records[0]
    header = data[hoff:hoff + hlen].decode("utf-8")
    cols = next(csv.reader([header]))
    fmt = "word" if "word_verbatim" in cols else "page"
    i_rid, i_pg = cols.index("release_id"), cols.index("pdf_page")
    i_word = cols.index("word_verbatim") if fmt == "word" else None
    i_conf = cols.index("conf") if fmt == "word" else None

    idx, seen, cur = defaultdict(list), set(), None
    for off, ln in records[1:]:
        raw = data[off:off + ln].decode("utf-8")
        if not raw.strip():
            continue
        row = next(csv.reader([raw]))
        key = (row[i_rid], int(row[i_pg]))
        if cur is None or key != cur["key"]:
            if cur:
                idx[cur["key"][0]].append(flush(cur))
            if key in seen:
                raise SystemExit(f"ocr_recovered.csv: rows for {key} are not contiguous; "
                                 "sort the file by release_id, pdf_page before building")
            seen.add(key)
            cur = {"key": key, "off": off, "len": 0, "confs": [], "low": 0}
        cur["len"] = off + ln - cur["off"]
        if fmt == "word":
            try:
                c = float(row[i_conf])
            except (ValueError, IndexError):
                c = None
            if c is not None and row[i_word] != REDACTION_TOKEN:
                cur["confs"].append(c)
                if c < CONF_FLOOR:
                    cur["low"] += 1
    if cur:
        idx[cur["key"][0]].append(flush(cur))
    return fmt, header.rstrip("\r\n"), dict(idx)


def iter_records(data: bytes):
    """Yield (offset, length) per CSV record, honouring quoted fields.

    ocr_text holds multi-line page text, so a record is not a line. Splitting
    on newlines would cut records in half and index fragments of a page as if
    they were the page.
    """
    start, i, n, q = 0, 0, len(data), False
    while i < n:
        c = data[i]
        if q:
            if c == 0x22:
                if i + 1 < n and data[i + 1] == 0x22:
                    i += 1
                else:
                    q = False
        elif c == 0x22:
            q = True
        elif c == 0x0A:
            yield start, i - start + 1
            start = i + 1
        i += 1
    if start < n:
        yield start, n - start


def flush(cur):
    mean = round(sum(cur["confs"]) / len(cur["confs"]), 1) if cur["confs"] else None
    return [cur["key"][1], cur["off"], cur["len"], mean, cur["low"]]


def build_page_index():
    """release_id -> [[pdf_page, byte_offset, byte_length], ...] into pages.jsonl."""
    idx = defaultdict(list)
    npages = 0
    with open(sp("pages.jsonl"), "rb") as f:
        off = 0
        for raw in f:
            n = len(raw)
            rec = json.loads(raw)
            idx[rec["release_id"]].append([rec["pdf_page"], off, len(raw.rstrip(b"\n"))])
            off += n
            npages += 1
    return idx, npages


def main(out):
    gaps = defaultdict(lambda: defaultdict(int))
    for r in csv.DictReader(open(sp("gaps.csv"))):
        gaps[r["release_id"]][r["gap_type"]] += 1

    docs = []
    for r in csv.DictReader(open(sp("manifest.csv"))):
        g = dict(gaps.get(r["release_id"], {}))
        docs.append({
            "id": r["release_id"], "s": r["subject_meta"][:120],
            "p": int(r["pages"]), "q": round(float(r["mean_ocr_quality"] or 0), 2),
            "y": year(r["release_id"], r["subject_meta"]),
            "gaps": g, "gnt": g.get("NO_TEXT_LAYER", 0), "gr": g.get("REDACTION_MARKER", 0),
        })

    segs = defaultdict(list)
    for r in csv.DictReader(open(sp("segments.csv"))):
        segs[r["release_id"]].append({
            "a": int(r["start_page"]), "b": int(r["end_page"]),
            "sub": r["subject_line"][:120], "d": r["first_date_verbatim"],
            "r": r["routing"][:80],
        })

    # media.csv carries the measurements; media_links.csv carries the URLs and
    # the files that are in Drive with no spine row. Joined on release_id, never merged.
    meas = {r["release_id"]: r for r in csv.DictReader(open(sp("media.csv")))}
    thumbs = {os.path.basename(p) for p in glob.glob(sp("*.jpg"))}

    def thumb(rid):
        for cand in (rid + ".jpg", rid + "_contact.jpg"):
            if cand in thumbs:
                return cand
        return ""

    media = []
    for r in csv.DictReader(open(sp("media_links.csv"))):
        rid = r["release_id"]
        m = meas.get(rid)
        row = {"id": rid, "st": r["spine_status"], "fam": family(rid), "th": thumb(rid),
               "v": r["working_view_url"], "e": r["working_embed_url"], "dl": r["working_direct_url"]}
        if m:
            row.update({"d": float(m["duration_s"]), "res": m["resolution"],
                        "fps": m["fps"].split("/")[0], "b": int(m["file_bytes"]),
                        "ct": m["creation_time"][:10]})
        media.append(row)
    media.sort(key=lambda x: (x["fam"], x["id"]))

    groups, n_ment = {}, 0
    for r in csv.DictReader(open(sp("entities_normalized.csv"))):
        n_ment += 1
        key = (r["value_normalized"], r["entity_type"])
        g = groups.setdefault(key, {"v": r["value_normalized"], "t": r["entity_type"],
                                    "f": r["candidate_flags"], "vv": [], "c": []})
        if r["value_verbatim"] not in g["vv"]:
            g["vv"].append(r["value_verbatim"])
        g["c"].append(f"{r['release_id']}:{r['pdf_page']}")
    ents = sorted(groups.values(), key=lambda g: -len(g["c"]))
    for i, g in enumerate(ents):
        g["n"] = len(g["c"])
        g["i"] = i

    ocr_fmt, ocr_hdr, oidx = build_ocr_index()

    # Detected redaction blocks, counted per page. Kept apart from the
    # REDACTION_MARKER gap rows, which catch textual markers only. A drawn
    # block and a typed marker are different observations.
    red = defaultdict(dict)
    if os.path.exists(sp("redactions.csv")):
        for r in csv.DictReader(open(sp("redactions.csv"))):
            k = int(r["pdf_page"])
            red[r["release_id"]][k] = red[r["release_id"]].get(k, 0) + 1

    pidx, npages = build_page_index()

    build = git_build()
    data = {"built": build["built"], "build": build, "docs": docs, "segs": segs, "media": media,
            "ents": ents, "etotal": n_ment, "pidx": pidx, "npages": npages,
            "oidx": oidx, "ocr_fmt": ocr_fmt, "ocr_hdr": ocr_hdr,
            "conf_floor": CONF_FLOOR, "red": red}

    tpl = open(os.path.join(ROOT, "site", "investigator.html")).read()
    payload = json.dumps(data, separators=(",", ":"))
    # The payload sits inside a <script>; a literal </script> in any corpus string
    # would close it early. Nothing else about the JSON changes.
    payload = payload.replace("</", "<\\/")
    html = tpl.replace("__DATA__", payload)
    if os.path.dirname(out):
        os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w").write(html)

    n_link = sum(1 for m in media if m["st"] == "INDEXED")
    n_ocr = sum(len(v) for v in oidx.values())
    print(f"wrote {out}: {len(html)/1e6:.2f} MB  "
          f"{len(docs)} documents / {npages} pages, "
          f"{len(media)} media ({n_link} indexed, {len(media)-n_link} awaiting ingest), "
          f"{n_ment} mentions in {len(ents)} groups\n"
          f"  OCR: {n_ocr} recovered pages, schema '{ocr_fmt}', confidence floor {CONF_FLOOR}"
          + ("  (page-per-row: no per-word scores yet, so nothing is dimmed)"
             if ocr_fmt == "page" else "")
          + f"\n  redaction blocks: {sum(sum(v.values()) for v in red.values())} across "
            f"{sum(len(v) for v in red.values())} pages")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="investigate.html")
    main(ap.parse_args().out)
