#!/usr/bin/env python3
"""Raster+OCR pass for pages flagged NO_TEXT_LAYER/LOW_OCR_QUALITY.
Usage: python3 ocr_fallback.py <file.pdf>
Writes ocr_recovered.csv (release_id, pdf_page, ocr_text, ocr_char_count) into the spine dir.
Recovered text is tagged OCR_RECOVERED and must be cited as such, not as source text layer."""
import csv, os, subprocess, sys, tempfile

OUT = os.environ.get("SPINE_OUT", "/mnt/user-data/outputs/spine")
pdf = sys.argv[1]; rid = os.path.basename(pdf).split("_")[0]
flagged = sorted({int(r["pdf_page"]) for r in csv.DictReader(open(f"{OUT}/gaps.csv"))
                  if r["release_id"] == rid and r["gap_type"] in ("NO_TEXT_LAYER", "LOW_OCR_QUALITY")})
rows = []
with tempfile.TemporaryDirectory() as td:
    for p in flagged:
        subprocess.run(["pdftoppm", "-r", "150", "-gray", "-png", "-f", str(p), "-l", str(p), pdf, f"{td}/p"], check=True)
        img = [f for f in os.listdir(td) if f.endswith(".png")][0]
        t = subprocess.run(["tesseract", f"{td}/{img}", "-", "--psm", "6"],
                           capture_output=True, text=True).stdout.strip()
        os.remove(f"{td}/{img}")
        rows.append([rid, p, t, len(t)])
        print(f"p{p}: {len(t)} chars recovered", flush=True)
new = not os.path.exists(f"{OUT}/ocr_recovered.csv")
with open(f"{OUT}/ocr_recovered.csv", "a", newline="") as f:
    w = csv.writer(f)
    if new: w.writerow(["release_id", "pdf_page", "ocr_text", "ocr_char_count"])
    w.writerows(rows)
