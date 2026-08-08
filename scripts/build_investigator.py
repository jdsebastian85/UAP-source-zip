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
"""
import argparse, csv, json, os, re, glob, subprocess
from collections import defaultdict
from datetime import date

SPINE = os.environ.get("SPINE", "spine")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


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

    ocr = defaultdict(dict)
    if os.path.exists(sp("ocr_recovered.csv")):
        for r in csv.DictReader(open(sp("ocr_recovered.csv"))):
            ocr[r["release_id"]][int(r["pdf_page"])] = r["ocr_text"]

    pidx, npages = build_page_index()

    build = git_build()
    data = {"built": build["built"], "build": build, "docs": docs, "segs": segs, "media": media,
            "ents": ents, "etotal": n_ment, "ocr": ocr, "pidx": pidx, "npages": npages}

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
    print(f"wrote {out}: {len(html)/1e6:.2f} MB  "
          f"{len(docs)} documents / {npages} pages, "
          f"{len(media)} media ({n_link} indexed, {len(media)-n_link} awaiting ingest), "
          f"{n_ment} mentions in {len(ents)} groups, {sum(len(v) for v in ocr.values())} OCR pages")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="investigate.html")
    main(ap.parse_args().out)
