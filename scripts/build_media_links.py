#!/usr/bin/env python3
"""Derive spine/media_links.csv from a raw Google Drive listing.

Layer 0 sidecar. It does not modify media.csv: the join key is release_id and the
two files stay separable, so a re-listing of Drive never touches ingest output.

Input  : spine/drive_listing_<date>.tsv  (drive_file_id, drive_title, drive_parent_id)
         Captured verbatim from the Drive API. Nothing in it is inferred.
Output : spine/media_links.csv

Every URL column is a mechanical expansion of drive_file_id into a documented Google
Drive URL template. No URL is guessed and none is verified by fetching.

Link tiers (see spine/SPINE.md):
  source_url   war.gov      primary provenance, may vanish        (not yet populated)
  mirror_url   archive.org  permanent public citation             (not yet populated)
  working_url  Drive        immediate access, not a citation      (populated here)
"""
import csv, os, sys, glob

SP = os.environ.get("SPINE", "spine")

VIEW = "https://drive.google.com/file/d/{id}/view"
EMBED = "https://drive.google.com/file/d/{id}/preview"
# usercontent form rather than /uc?export=download: most of these files are over the
# ~100 MB threshold where the /uc endpoint returns a virus-scan interstitial page
# instead of the file.
DIRECT = "https://drive.usercontent.google.com/download?id={id}&export=download&confirm=t"

COLS = ["release_id", "spine_status", "drive_file_id", "drive_parent_id",
        "working_view_url", "working_embed_url", "working_direct_url",
        "listed_utc", "source_url", "mirror_url"]


def main():
    listings = sorted(glob.glob(os.path.join(SP, "drive_listing_*.tsv")))
    if not listings:
        sys.exit(f"no {SP}/drive_listing_*.tsv found")
    path = listings[-1]
    listed = os.path.basename(path).removeprefix("drive_listing_").removesuffix(".tsv")

    media = {r["release_id"] for r in csv.DictReader(open(os.path.join(SP, "media.csv")))}

    rows, seen = [], set()
    for r in csv.DictReader(open(path), delimiter="\t"):
        title = r["drive_title"]
        rid = title[:-4] if title.endswith(".mp4") else title
        if rid in seen:
            sys.exit(f"duplicate release_id in listing: {rid}")
        seen.add(rid)
        fid = r["drive_file_id"]
        rows.append({
            "release_id": rid,
            "spine_status": "INDEXED" if rid in media else "NOT_INGESTED",
            "drive_file_id": fid,
            "drive_parent_id": r["drive_parent_id"],
            "working_view_url": VIEW.format(id=fid),
            "working_embed_url": EMBED.format(id=fid),
            "working_direct_url": DIRECT.format(id=fid),
            "listed_utc": listed,
            "source_url": "",
            "mirror_url": "",
        })

    missing = sorted(media - seen)
    if missing:
        print(f"WARN: {len(missing)} media.csv rows have no Drive file: {missing[:5]}")

    rows.sort(key=lambda r: r["release_id"])
    out = os.path.join(SP, "media_links.csv")
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        w.writerows(rows)

    n_idx = sum(1 for r in rows if r["spine_status"] == "INDEXED")
    print(f"{out}: {len(rows)} rows  INDEXED {n_idx}  NOT_INGESTED {len(rows)-n_idx}")


if __name__ == "__main__":
    main()
