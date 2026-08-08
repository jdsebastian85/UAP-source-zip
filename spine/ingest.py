#!/usr/bin/env python3
"""
UAP release-dump ingest spine.
Usage:  python3 ingest.py <file.pdf> [more.pdf ...]
Idempotent: re-running on the same release ID overwrites that release's rows.

Outputs (all under OUT):
  manifest.csv        one row per release PDF   (Layer 0)
  pages.jsonl         one record per page       (Layer 1)
  segments.csv        one row per record-within-release (Layer 2)
  entities.csv        verbatim strings + page cite (Layer 3)
  gaps.csv            redactions / illegible / missing (Layer 6)
Nothing in these files is inferred. Every row carries a page cite.
"""
import csv, hashlib, json, os, re, subprocess, sys

OUT = os.environ.get("SPINE_OUT", "/mnt/user-data/outputs/spine")
os.makedirs(OUT, exist_ok=True)

# ---------- deterministic patterns (extraction only, no interpretation) ----------
P = {
    "release_stamp":  re.compile(r"\bNW\s*\d{4,6}\b"),
    "docid":          re.compile(r"\bDoc\s*[Il1]d\s*[:;]?\s*(\d{3,12})", re.I),
    "page_stamp":     re.compile(r"\bPage\s+(\d{1,4})\b"),
    # classification / handling markings, verbatim
    "marking":        re.compile(r"\b(TOP SECRET|SECRET|CONFIDENTIAL|UNCLASSIFIED|FOR OFFICIAL USE ONLY|NOFORN|RESTRICTED|EYES ONLY|DECLASSIFIED)\b", re.I),
    # redaction / withholding language and FOIA exemption cites
    "redaction":      re.compile(r"\b(b\(\s*[1-9]\s*\)|\(b\)\([1-9]\)|REDACT\w*|WITHHELD|EXEMPT\w*|DELETED|SANITIZ\w*)\b", re.I),
    # dates: 17 April 1967 | April 17, 1967 | 4/17/67 | 17 Apr 67
    "date": re.compile(
        r"\b(?:\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{2,4}"
        r"|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4}"
        r"|\d{1,2}/\d{1,2}/\d{2,4})\b"),
    # military / civil rank-titles preceding a name
    "person": re.compile(
        r"\b(?:Lt\.?\s*Col\.?|Maj\.?\s*Gen\.?|Brig\.?\s*Gen\.?|Gen\.?|Col\.?|Maj\.?|Capt\.?|Lt\.?|"
        r"Cmdr\.?|Cdr\.?|Adm\.?|Sgt\.?|Dr\.?|Mr\.?|Mrs\.?|Ms\.?|Prof\.?|Hon\.?)"
        r"\s+([A-Z][A-Za-z.'\-]+(?:\s+[A-Z][A-Za-z.'\-]+){0,3})"),
    # USAF/DoD office symbols and agency acronyms
    "org": re.compile(
        r"\b(?:SAF[A-Z\-]{2,8}|AFOSR|AFSC|ATIC|FTD|OAR|ONR|NASA|CIA|FBI|NSA|USAF|"
        r"AFCRL|ARPA|IDA|NORAD|SAC|ADC|OSI|AFSAB|NICAP|APRO|Project\s+(?:Blue\s*Book|Bluebook|Sign|Grudge|Twinkle|Moon\s*Dust))"
        r"(?:\s*\([A-Z0-9\-]{2,8}\))?"),
    "room_phone": re.compile(r"\b(?:Room\s+[A-Z0-9\-]{2,8}|Tele\.?\s*\d{3}[- ]?\d{4}|Code\s+\d{2}[- ]\d{5,6})"),
    "subject_line": re.compile(r"^\s*(?:SUBJECT|Subject|SUBJ|RE|Re)\s*[:.]\s*(.+)$", re.M),
    "to_from": re.compile(r"^\s*(TO|FROM|THRU|MEMORANDUM FOR|FOR)\s*[:.]\s*(.+)$", re.M),
    "enclosure": re.compile(r"\b(?:Encl(?:osure)?s?|Atch|Attachment|Incl|Tab)\b[:.\s]", re.I),
}
# a page that starts a new record inside the release PDF
SEG_START = re.compile(
    r"(DEPARTMENT OF THE AIR FORCE|DEPARTMENT OF THE AlR FORCE|MEMORANDUM FOR|"
    r"^\s*(?:SUBJECT|Subject)\s*[:.]|HEADQUARTERS|UNIVERSITY OF|Dear (?:Dr|Mr|Mrs|Ms|Col|Gen)\b)", re.M)

NOISE = re.compile(r"(NW\s*\d{4,6}|Doc\s*[Il1]d\s*[:;]?\s*\d+|Page\s+\d+|[\s\"'])")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def pdfinfo(path):
    raw = subprocess.run(["pdfinfo", path], capture_output=True, text=True).stdout
    d = {}
    for line in raw.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            d[k.strip()] = v.strip()
    return d


def ocr_quality(text):
    """Deterministic legibility proxy: share of alnum chars in recognized words."""
    body = NOISE.sub("", text)
    if not body:
        return 0.0, 0
    good = sum(c.isalnum() or c in " .,;:()-/" for c in body)
    return round(good / len(body), 3), len(body)


def uniq(seq):
    seen, out = set(), []
    for x in seq:
        x = re.sub(r"\s+", " ", x).strip(" .,;:")
        if x and x.lower() not in seen:
            seen.add(x.lower())
            out.append(x)
    return out


def process(pdf_path):
    base = os.path.basename(pdf_path)
    release_id = base.split("_")[0]
    info = pdfinfo(pdf_path)
    txt = subprocess.run(["pdftotext", "-layout", pdf_path, "-"],
                         capture_output=True, text=True, errors="ignore").stdout
    pages = txt.split("\f")
    if pages and not pages[-1].strip():
        pages.pop()

    page_rows, seg_rows, ent_rows, gap_rows = [], [], [], []
    seg_no, seg_open = 0, None

    for i, ptxt in enumerate(pages, start=1):
        q, blen = ocr_quality(ptxt)
        stamps = uniq(P["release_stamp"].findall(ptxt))
        docids = uniq(P["docid"].findall(ptxt))
        low = blen < 40

        rec = {
            "release_id": release_id,
            "source_file": base,
            "pdf_page": i,
            "release_stamp": stamps[0] if stamps else "",
            "doc_id_stamp": max(docids, key=len) if docids else "",
            "char_count": blen,
            "ocr_quality": q,
            "no_text_layer": low,
            "markings": uniq(P["marking"].findall(ptxt)),
            "dates_verbatim": uniq(P["date"].findall(ptxt)),
            "persons_verbatim": uniq(m.group(0) for m in P["person"].finditer(ptxt)),
            "orgs_verbatim": uniq(P["org"].findall(ptxt)),
            "locators": uniq(P["room_phone"].findall(ptxt)),
            "subject_lines": uniq(P["subject_line"].findall(ptxt)),
            "routing": [f"{a}: {b.strip()}" for a, b in P["to_from"].findall(ptxt)],
            "redaction_markers": uniq(P["redaction"].findall(ptxt)),
            "text": ptxt,
        }
        page_rows.append(rec)

        # Layer 6 — gaps
        if low:
            gap_rows.append([release_id, i, "NO_TEXT_LAYER",
                             "page yields <40 chars; requires raster/OCR pass"])
        elif q < 0.90:
            gap_rows.append([release_id, i, "LOW_OCR_QUALITY", f"quality={q}"])
        for r in rec["redaction_markers"]:
            gap_rows.append([release_id, i, "REDACTION_MARKER", r])
        if P["enclosure"].search(ptxt):
            gap_rows.append([release_id, i, "ENCLOSURE_REFERENCED",
                             "enclosure/attachment cited; verify presence in dump"])

        # Layer 2 — segmentation
        if SEG_START.search(ptxt) or (seg_open is None):
            if seg_open:
                seg_open["end_page"] = i - 1
                seg_rows.append(seg_open)
            seg_no += 1
            seg_open = {
                "release_id": release_id, "segment_no": seg_no, "start_page": i,
                "end_page": i,
                "subject_line": (rec["subject_lines"] or [""])[0],
                "routing": " | ".join(rec["routing"]),
                "first_date_verbatim": (rec["dates_verbatim"] or [""])[0],
                "doc_id_stamp": rec["doc_id_stamp"],
            }

        # Layer 3 — entity rows
        for kind, key in (("PERSON", "persons_verbatim"), ("ORG", "orgs_verbatim"),
                          ("DATE", "dates_verbatim"), ("LOCATOR", "locators"),
                          ("MARKING", "markings")):
            for v in rec[key]:
                ent_rows.append([release_id, i, kind, v])

    if seg_open:
        seg_open["end_page"] = len(pages)
        seg_rows.append(seg_open)

    manifest = {
        "release_id": release_id, "source_file": base,
        "title_meta": info.get("Title", ""), "subject_meta": info.get("Subject", ""),
        "author_meta": info.get("Author", ""), "producer": info.get("Producer", ""),
        "pdf_created": info.get("CreationDate", ""), "pdf_modified": info.get("ModDate", ""),
        "pages": len(pages), "file_bytes": os.path.getsize(pdf_path),
        "sha256": sha256(pdf_path),
        "pages_no_text_layer": sum(p["no_text_layer"] for p in page_rows),
        "mean_ocr_quality": round(sum(p["ocr_quality"] for p in page_rows) / max(len(page_rows), 1), 3),
        "segments": len(seg_rows),
        "release_stamps": ";".join(uniq([p["release_stamp"] for p in page_rows if p["release_stamp"]])),
        "doc_id_stamps": ";".join(uniq([p["doc_id_stamp"] for p in page_rows if p["doc_id_stamp"]])),
    }
    return manifest, page_rows, seg_rows, ent_rows, gap_rows


def append_csv(path, header, rows):
    new = not os.path.exists(path)
    with open(path, "a", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(header)
        w.writerows(rows)


def main(paths):
    for p in paths:
        man, pages, segs, ents, gaps = process(p)
        rid = man["release_id"]

        # drop prior rows for this release (idempotent re-run)
        for fn in ("manifest.csv", "segments.csv", "entities.csv", "gaps.csv"):
            fp = os.path.join(OUT, fn)
            if os.path.exists(fp):
                with open(fp) as f:
                    rows = list(csv.reader(f))
                head, body = rows[0], [r for r in rows[1:] if r and r[0] != rid]
                with open(fp, "w", newline="") as f:
                    csv.writer(f).writerows([head] + body)
        jl = os.path.join(OUT, "pages.jsonl")
        if os.path.exists(jl):
            keep = [l for l in open(jl) if json.loads(l)["release_id"] != rid]
            open(jl, "w").writelines(keep)

        append_csv(os.path.join(OUT, "manifest.csv"), list(man), [list(man.values())])
        append_csv(os.path.join(OUT, "segments.csv"),
                   ["release_id", "segment_no", "start_page", "end_page",
                    "subject_line", "routing", "first_date_verbatim", "doc_id_stamp"],
                   [[s["release_id"], s["segment_no"], s["start_page"], s["end_page"],
                     s["subject_line"], s["routing"], s["first_date_verbatim"],
                     s["doc_id_stamp"]] for s in segs])
        append_csv(os.path.join(OUT, "entities.csv"),
                   ["release_id", "pdf_page", "entity_type", "value_verbatim"], ents)
        append_csv(os.path.join(OUT, "gaps.csv"),
                   ["release_id", "pdf_page", "gap_type", "detail"], gaps)
        with open(jl, "a") as f:
            for r in pages:
                f.write(json.dumps(r) + "\n")

        print(f"{rid}: {man['pages']}p  segments={man['segments']}  "
              f"no-text={man['pages_no_text_layer']}  entities={len(ents)}  gaps={len(gaps)}")


if __name__ == "__main__":
    main(sys.argv[1:])
