#!/usr/bin/env python3
"""Map release_id -> the page-image folder name actually used on the host.

manifest.csv records source_file as it was catalogued. The folder that page
images were rendered into, and therefore the key they carry on Internet
Archive, is the real filename from the source drop. For 90 of 211 releases
those two strings differ: the catalogued name has had spaces, underscores and
dots flattened to hyphens. Addressing IA with the catalogued name 404s.

This resolves the two by normalising both sides down to a separator-insensitive
key and joining on it. The result is written to site/page_images.json under
"folders", which the investigator consults ahead of the manifest value.

The mapping is hosting bookkeeping, not evidence, so it lives in site/ and the
manifest's source_file is left exactly as catalogued.

An ambiguous match is never resolved by guessing: it is reported and omitted,
so the page simply reports no image rather than showing the wrong page.
"""
import argparse, csv, json, os, re, sys, unicodedata
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_RENDER = r"C:\Users\bashs\page_images_rendered"


def key(s):
    """Separator-insensitive form. Both sides of the join get the same treatment."""
    s = unicodedata.normalize("NFKC", s).lower()
    s = s.replace("\u2013", "-").replace("\u2014", "-")
    s = re.sub(r"[_ \-.]+", "-", s)
    return s.strip("-")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--render-dir", default=DEFAULT_RENDER,
                    help="directory holding one folder of page images per source PDF")
    ap.add_argument("--write", action="store_true",
                    help="write the mapping into site/page_images.json")
    a = ap.parse_args()

    if not os.path.isdir(a.render_dir):
        sys.exit("render dir not found: %s" % a.render_dir)

    dirs = [d for d in os.listdir(a.render_dir)
            if os.path.isdir(os.path.join(a.render_dir, d))]
    idx = defaultdict(list)
    for d in dirs:
        idx[key(d)].append(d)

    manifest = os.path.join(ROOT, "spine", "manifest.csv")
    rows = list(csv.DictReader(open(manifest, encoding="utf-8")))

    folders, same, ambiguous, missing = {}, 0, [], []
    for r in rows:
        rid, sf = r["release_id"], r["source_file"]
        cand = idx.get(key(sf), [])
        if len(cand) > 1:
            ambiguous.append((rid, sf, cand))
        elif not cand:
            missing.append((rid, sf))
        else:
            folders[rid] = cand[0]
            if cand[0] == sf:
                same += 1

    print("releases in manifest : %d" % len(rows))
    print("page-image folders   : %d" % len(dirs))
    print("resolved             : %d  (%d already identical, %d renamed)"
          % (len(folders), same, len(folders) - same))
    print("ambiguous (omitted)  : %d" % len(ambiguous))
    for rid, sf, cand in ambiguous:
        print("    %s\n      sf=%s\n      candidates=%s" % (rid, sf, cand))
    print("no folder rendered   : %d" % len(missing))
    for rid, sf in missing:
        print("    %s  sf=%s" % (rid, sf))

    orphan = sorted(set(dirs) - set(folders.values()))
    print("folders with no release row : %d" % len(orphan))
    for o in orphan[:10]:
        print("    %s" % o)
    if len(orphan) > 10:
        print("    ... and %d more" % (len(orphan) - 10))

    if not a.write:
        print("\n(dry run; pass --write to update site/page_images.json)")
        return

    cfg = os.path.join(ROOT, "site", "page_images.json")
    doc = json.load(open(cfg, encoding="utf-8")) if os.path.exists(cfg) else {}
    doc["folders"] = dict(sorted(folders.items()))
    with open(cfg, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=1, ensure_ascii=False)
        f.write("\n")
    print("\nwrote %d folder mappings to site/page_images.json" % len(folders))


if __name__ == "__main__":
    main()
