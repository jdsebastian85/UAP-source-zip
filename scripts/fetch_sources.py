#!/usr/bin/env python3
"""Pull source files from the shared Drive folder, skipping anything already ingested.
Usage: python3 scripts/fetch_sources.py [--media|--docs|--all] [--dry-run]
Idempotent: diffs the folder listing against manifest.csv + media.csv first."""
import csv, os, subprocess, sys
FOLDER = "https://drive.google.com/drive/folders/1Z8_NzOrfjXiQTsxkj0GEbUdr1SI5LjWM"
SPINE = os.environ.get("SPINE", "spine")
MEDIA_DIR, PDF_DIR = "sources/media", "sources/pdf"
VID = (".mp4", ".mov", ".avi", ".mkv")

def ingested():
    have = set()
    for name, col in (("manifest.csv","source_file"), ("media.csv","source_file"), ("images.csv","source_file")):
        p = os.path.join(SPINE, name)
        if os.path.exists(p):
            have |= {r[col] for r in csv.DictReader(open(p))}
    return have

def main():
    import gdown
    mode = next((a for a in sys.argv[1:] if a.startswith("--") and a != "--dry-run"), "--all")
    dry = "--dry-run" in sys.argv
    files = gdown.download_folder(url=FOLDER, skip_download=True, quiet=True) or []
    have = ingested()
    os.makedirs(MEDIA_DIR, exist_ok=True); os.makedirs(PDF_DIR, exist_ok=True)
    todo = []
    for f in files:
        isvid = f.path.lower().endswith(VID)
        if mode == "--media" and not isvid: continue
        if mode == "--docs" and isvid: continue
        dest = os.path.join(MEDIA_DIR if isvid else PDF_DIR, f.path)
        if os.path.exists(dest): continue
        todo.append((f, dest, f.path in have))
    print(f"folder has {len(files)} files; {len(todo)} not on local disk")
    for f, dest, already in todo:
        tag = "(already in spine, re-pull for source access)" if already else "(NEW)"
        print(("would pull " if dry else "pulling ") + f.path, tag)
        if not dry:
            subprocess.run(["gdown","-q",f"https://drive.google.com/uc?id={f.id}","-O",dest])

if __name__ == "__main__":
    main()
