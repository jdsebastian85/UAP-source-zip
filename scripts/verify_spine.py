#!/usr/bin/env python3
"""Integrity check for the spine. Run after every task.
Checks schema, cite presence, orphan rows, and cross-file consistency.
Exits nonzero on any error so it can gate a commit hook."""
import csv, json, os, sys
from collections import Counter

SP = os.environ.get("SPINE", "spine")
errs, warns = [], []

def load_csv(name, required):
    p = os.path.join(SP, name)
    if not os.path.exists(p):
        errs.append(f"{name}: missing"); return []
    rows = list(csv.DictReader(open(p)))
    if rows:
        missing = required - set(rows[0].keys())
        if missing: errs.append(f"{name}: missing columns {sorted(missing)}")
    return rows

man = load_csv("manifest.csv", {"release_id","source_file","pages","sha256","mean_ocr_quality"})
med = load_csv("media.csv", {"release_id","source_file","duration_s","sha256_16"})
seg = load_csv("segments.csv", {"release_id","segment_no","start_page","end_page"})
ent = load_csv("entities.csv", {"release_id","pdf_page","entity_type","value_verbatim"})
gap = load_csv("gaps.csv", {"release_id","pdf_page","gap_type"})
lnk = load_csv("media_links.csv", {"release_id","spine_status","drive_file_id",
                                   "working_view_url","source_url","mirror_url"}) \
      if os.path.exists(os.path.join(SP, "media_links.csv")) else []

ids = {r["release_id"] for r in man}
pagecount = {r["release_id"]: int(r["pages"]) for r in man}

# every row cites a known release
for name, rows in (("segments",seg), ("entities",ent), ("gaps",gap)):
    orphans = {r["release_id"] for r in rows} - ids
    if orphans: errs.append(f"{name}: {len(orphans)} release_ids not in manifest: {sorted(orphans)[:5]}")

# no uncited rows
for name, rows in (("entities",ent), ("gaps",gap)):
    n = sum(1 for r in rows if not str(r.get("pdf_page","")).strip())
    if n: errs.append(f"{name}: {n} rows with no page cite")

# page numbers within range
for r in ent:
    try:
        p, rid = int(r["pdf_page"]), r["release_id"]
        if rid in pagecount and not (1 <= p <= pagecount[rid]):
            errs.append(f"entities: {rid} page {p} out of range (1..{pagecount[rid]})"); break
    except ValueError:
        errs.append(f"entities: non-numeric page {r['pdf_page']!r}"); break

# pages.jsonl parses and matches manifest counts
pj = os.path.join(SP, "pages.jsonl")
if os.path.exists(pj):
    seen = Counter()
    for i, line in enumerate(open(pj), 1):
        try: rec = json.loads(line)
        except Exception as e: errs.append(f"pages.jsonl:{i} bad JSON: {e}"); break
        seen[rec["release_id"]] += 1
    for rid, n in pagecount.items():
        if rid in seen and seen[rid] != n:
            warns.append(f"pages.jsonl: {rid} has {seen[rid]} page records, manifest says {n}")
else:
    errs.append("pages.jsonl: missing")

# duplicate hashes = duplicate ingest
dupe = [h for h,c in Counter(r["sha256"] for r in man).items() if c > 1]
if dupe: warns.append(f"manifest: {len(dupe)} duplicate sha256 (same file ingested twice?)")

# media_links.csv is a Layer 0 sidecar keyed on media.csv release_ids
if lnk:
    mids = {m["release_id"] for m in med}
    lids = [r["release_id"] for r in lnk]
    d = [k for k,c in Counter(lids).items() if c > 1]
    if d: errs.append(f"media_links: duplicate release_ids {d[:5]}")
    bad = {r["release_id"] for r in lnk if r["spine_status"] == "INDEXED"} - mids
    if bad: errs.append(f"media_links: {len(bad)} INDEXED rows not in media.csv: {sorted(bad)[:5]}")
    nolink = mids - set(lids)
    if nolink: errs.append(f"media_links: {len(nolink)} media.csv rows have no link row: {sorted(nolink)[:5]}")
    for r in lnk:
        if not r["drive_file_id"].strip() or not r["working_view_url"].strip():
            errs.append(f"media_links: {r['release_id']} has an empty working link"); break

# Layer 5 must never be persisted
for forbidden in ("relations.csv","edges.csv","cooccurrence.csv","layer5.csv"):
    if os.path.exists(os.path.join(SP, forbidden)):
        errs.append(f"{forbidden} exists — Layer 5 is derived at query time and must not be stored")

print(f"documents {len(man)}  pages {sum(pagecount.values())}  media {len(med)} "
      f"({round(sum(float(m['duration_s']) for m in med)/3600,2)} h)")
print(f"segments {len(seg)}  entities {len(ent)}  gaps {len(gap)} {dict(Counter(g['gap_type'] for g in gap))}")
if lnk:
    print(f"media_links {len(lnk)} {dict(Counter(r['spine_status'] for r in lnk))}  "
          f"mirrored {sum(1 for r in lnk if r['mirror_url'].strip())}")
for w in warns: print("WARN:", w)
for e in errs: print("ERROR:", e)
print("FAIL" if errs else "OK")
sys.exit(1 if errs else 0)
