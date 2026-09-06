#!/usr/bin/env python3
"""Build one readable transcript of the whole corpus, cited page by page.

Usage:
  py -3.11 scripts/build_transcript.py --out C:\\Users\\bashs\\pursue-transcript.txt
  py -3.11 scripts/build_transcript.py --out DIR --split      (one file per release)

This is a reading and drafting artifact, not a spine file. Nothing here is
written back into spine/ and nothing is corrected, normalised or merged.

Why it is not a plain text dump
-------------------------------
1,719 of 8,661 pages carry no text layer. Concatenating only the pages that
have text would produce a file that reads as though the corpus were complete,
and a reader drafting from it would have no way to tell a subject that is
absent from the record apart from a subject sitting on a page nobody has read.
So every page appears, in order, and a page with no text appears as an explicit
gap. Absence is recorded, never assumed.

The same applies to the 818 pages whose shipped text scores below the 0.90
page-level legibility proxy. Their text is present and is reproduced verbatim,
but the header says the machine read it poorly, because a garbled line quoted
as though it were clean is the failure mode this whole corpus exists to avoid.

Text sources are tagged and never merged, per CLAUDE.md:
  TEXT_LAYER      the publisher's own OCR, shipped inside the PDF
  OCR_RECOVERED   produced locally, currently 61 pages

The released documents are US Government works in the public domain
(17 U.S.C. section 105). The index built over them is CC BY 4.0 — see
CITATION.cff.
"""
import argparse, csv, json, os, sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SP = os.path.join(ROOT, "spine")
QUALITY_FLOOR = 0.90
BAR = "=" * 78
RULE = "#" * 78


def sp(name):
    return os.path.join(SP, name)


def load_manifest():
    rows = list(csv.DictReader(open(sp("manifest.csv"), encoding="utf-8")))
    return {r["release_id"]: r for r in rows}, [r["release_id"] for r in rows]


def load_recovered():
    """(release_id, page) -> locally recovered text, where a pass has run."""
    path = sp("ocr_recovered.csv")
    if not os.path.exists(path):
        return {}
    out = {}
    rdr = csv.DictReader(open(path, encoding="utf-8"))
    if "ocr_text" not in (rdr.fieldnames or []):
        return {}          # word-per-row schema (T2.3); not assembled here
    for r in rdr:
        try:
            out[(r["release_id"], int(r["pdf_page"]))] = r["ocr_text"]
        except (ValueError, KeyError):
            continue
    return out


def load_gaps():
    low, other = {}, defaultdict(lambda: defaultdict(list))
    for r in csv.DictReader(open(sp("gaps.csv"), encoding="utf-8")):
        try:
            pg = int(r["pdf_page"])
        except ValueError:
            continue
        if r["gap_type"] == "LOW_OCR_QUALITY":
            low[(r["release_id"], pg)] = r.get("detail", "")
        elif r["gap_type"] != "NO_TEXT_LAYER":
            other[r["release_id"]][pg].append(r["gap_type"])
    return low, other


def page_header(rid, pg, tag, extra=""):
    head = "--- [%s p.%d] %s%s " % (rid, pg, tag, (" \u00b7 " + extra) if extra else "")
    return head + "-" * max(3, 78 - len(head))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True,
                    help="output file, or output directory when --split is given")
    ap.add_argument("--split", action="store_true",
                    help="write one file per release instead of one combined file")
    a = ap.parse_args()

    man, order = load_manifest()
    recovered = load_recovered()
    low, other_gaps = load_gaps()

    # Group page records by release without holding the whole 32 MB in memory
    # as parsed objects any longer than necessary.
    pages = defaultdict(list)
    with open(sp("pages.jsonl"), encoding="utf-8") as f:
        for line in f:
            rec = json.loads(line)
            pages[rec["release_id"]].append(rec)
    for rid in pages:
        pages[rid].sort(key=lambda r: r["pdf_page"])

    n_text = n_low = n_none = n_rec = 0
    for rid in order:
        for rec in pages.get(rid, []):
            key = (rid, rec["pdf_page"])
            if rec.get("no_text_layer"):
                n_none += 1
                if key in recovered:
                    n_rec += 1
            elif key in low:
                n_low += 1
            else:
                n_text += 1
    total = n_text + n_low + n_none

    def release_block(rid):
        r = man[rid]
        recs = pages.get(rid, [])
        out = []
        subject = (r.get("subject_meta") or "").strip() or "no subject in metadata"
        nnt = sum(1 for x in recs if x.get("no_text_layer"))
        out.append(RULE)
        out.append("# %s" % rid)
        out.append("# %s" % subject)
        out.append("# %s pages \u00b7 mean text-layer legibility %s%s" % (
            r.get("pages", "?"), r.get("mean_ocr_quality", "?"),
            " \u00b7 %d with NO text layer" % nnt if nnt else ""))
        out.append("# source file: %s" % r.get("source_file", ""))
        out.append(RULE)
        out.append("")
        for rec in recs:
            pg = rec["pdf_page"]
            key = (rid, pg)
            flags = other_gaps.get(rid, {}).get(pg, [])
            extra = " \u00b7 ".join(flags)
            if rec.get("no_text_layer"):
                if key in recovered:
                    out.append(page_header(rid, pg, "OCR_RECOVERED",
                                           ("no shipped text layer" +
                                            (" \u00b7 " + extra if extra else ""))))
                    out.append("*** No text layer shipped with this page. The text below was")
                    out.append("*** recovered locally by OCR and is NOT the publisher's text.")
                    out.append("")
                    out.append((recovered[key] or "").rstrip())
                else:
                    out.append(page_header(rid, pg, "NO TEXT LAYER", extra))
                    out.append("*** This page yielded no text and has not been read by")
                    out.append("*** anything. It is a gap in this transcript, not a blank")
                    out.append("*** page in the release.")
            else:
                if key in low:
                    q = low[key].replace("quality=", "")
                    out.append(page_header(rid, pg, "TEXT_LAYER",
                                           "READ POORLY, legibility %s (floor %.2f)%s"
                                           % (q, QUALITY_FLOOR,
                                              " \u00b7 " + extra if extra else "")))
                    out.append("*** The machine read this page poorly. The text is verbatim")
                    out.append("*** but may be garbled; check it against the scan before")
                    out.append("*** quoting it.")
                    out.append("")
                else:
                    out.append(page_header(rid, pg, "TEXT_LAYER", extra))
                body = (rec.get("text") or "").rstrip()
                out.append(body if body else "*** (the text layer for this page is empty)")
            out.append("")
        return "\n".join(out)

    preamble = "\n".join([
        BAR,
        "PURSUE UAP Release Corpus \u2014 full transcript",
        BAR,
        "",
        "%d releases \u00b7 %d pages" % (len(order), total),
        "",
        "  %5d  pages carry the publisher's shipped text layer" % n_text,
        "  %5d  carry one the machine read poorly (below the %.2f legibility proxy);"
        % (n_low, QUALITY_FLOOR),
        "         their text is here verbatim and may be garbled",
        "  %5d  carry NO text layer at all%s" % (
            n_none, " (%d of those recovered locally by OCR)" % n_rec if n_rec else ""),
        "",
        "Every page in the corpus appears below, in order, whether or not it has",
        "text. A page with no text appears as an explicit gap rather than being",
        "left out, because a transcript that silently omits unread pages cannot be",
        "told apart from one where those pages were blank.",
        "",
        "Every page is cited as [release_id p.N]. Search that pattern to jump.",
        "Text is verbatim. Nothing here is corrected, normalised, or merged, and",
        "the publisher's text (TEXT_LAYER) is never mixed with locally recovered",
        "OCR (OCR_RECOVERED).",
        "",
        "The released documents are US Government works in the public domain",
        "(17 U.S.C. \u00a7 105). The index built over them is CC BY 4.0 \u2014 if you",
        "publish from this, cite it: Sebastian, J. D. (2026). PURSUE UAP Release",
        "Corpus [Data set]. anthro-tech.org.",
        "",
        BAR,
        "CONTENTS",
        BAR,
        ""])
    toc = []
    for i, rid in enumerate(order, 1):
        r = man[rid]
        subj = (r.get("subject_meta") or "").strip()[:58] or "no subject in metadata"
        toc.append("%4d. %-46s %5s pp  %s" % (i, rid[:46], r.get("pages", "?"), subj))
    preamble += "\n".join(toc) + "\n"

    if a.split:
        os.makedirs(a.out, exist_ok=True)
        for rid in order:
            safe = "".join(c if c.isalnum() or c in "-_." else "_" for c in rid)
            with open(os.path.join(a.out, safe + ".txt"), "w", encoding="utf-8") as f:
                f.write(release_block(rid))
        print("wrote %d files to %s" % (len(order), a.out))
        return

    if os.path.dirname(a.out):
        os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w", encoding="utf-8") as f:
        f.write(preamble)
        f.write("\n")
        for rid in order:
            f.write(release_block(rid))
            f.write("\n")
    size = os.path.getsize(a.out)
    print("wrote %s" % a.out)
    print("  %.1f MB \u00b7 %d releases \u00b7 %d pages" % (size / 1e6, len(order), total))
    print("  %d text layer / %d read poorly / %d no text layer%s"
          % (n_text, n_low, n_none,
             " (%d recovered)" % n_rec if n_rec else ""))
    if total != 8661:
        print("  NOTE: expected 8,661 pages; the corpus has changed.", file=sys.stderr)


if __name__ == "__main__":
    main()
