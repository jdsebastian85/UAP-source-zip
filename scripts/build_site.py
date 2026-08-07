#!/usr/bin/env python3
"""Regenerate the single-file corpus reader from current spine CSVs.
Usage: python3 scripts/build_site.py [--out site/pursue_corpus_reader.html]
Every displayed value must trace to a CSV row. No derived or inferred values."""
import argparse, csv, json, os, re
SPINE = os.environ.get("SPINE", "spine")

def year(*s):
    m = re.findall(r"(19[4-9]\d|20[0-2]\d)", " ".join(s))
    return m[0] if m else ""

def family(rid):
    if rid.startswith("video_2605"): return "v2605 edited"
    for k, lab in (("111830","111830 sensor"),("111887","111887 scope"),
                   ("111764","111764 handheld"),("111688","111688 ISR"),("111689","111689 ISR")):
        if k in rid: return lab
    return "other"

def main(out):
    docs = [{"id":r["release_id"], "s":r["subject_meta"][:90], "a":r["release_id"].split("-")[0],
             "p":int(r["pages"]), "q":round(float(r["mean_ocr_quality"] or 0),2),
             "y":year(r["release_id"], r["subject_meta"])}
            for r in csv.DictReader(open(os.path.join(SPINE,"manifest.csv")))]
    media = [{"id":r["release_id"], "d":float(r["duration_s"]), "res":r["resolution"],
              "fps":r["fps"].split("/")[0], "ct":r["creation_time"][:10],
              "b":int(r["file_bytes"]), "fam":family(r["release_id"])}
             for r in csv.DictReader(open(os.path.join(SPINE,"media.csv")))]
    tpl = open(os.path.join(os.path.dirname(__file__), "..", "site", "template.html")).read()
    html = tpl.replace("__DATA__", json.dumps({"docs":docs,"media":media}, separators=(",",":")))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out,"w").write(html)
    print(f"wrote {out}: {len(docs)} documents, {len(media)} media rows, "
          f"{round(sum(m['d'] for m in media)/3600,2)} hours")

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--out", default="site/pursue_corpus_reader.html")
    main(ap.parse_args().out)
