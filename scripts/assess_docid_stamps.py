#!/usr/bin/env python3
"""T3b.4: assess DocId stamp truncation against pages.jsonl, the file where
doc_id_stamp actually lives (the T3 check ran against entities.csv, which has
no DocId rows, and its "nothing found" result is superseded).

Mechanical rules, per release:
  DOCID_STAMP_TRUNCATED  stamp is a proper prefix of a longer stamp appearing
                         on another page of the same release
  DOCID_STAMP_ANOMALOUS  stamp is shorter than the longest stamp of the same
                         release but is not a prefix of any longer stamp

Both are recorded as cited gap rows in gaps.csv with the verbatim stamp values
in detail. Re-running replaces prior rows of these two types, so the pass is
idempotent. Nothing else in gaps.csv is touched; pages.jsonl is read-only.
"""
import csv, json, os
from collections import defaultdict

SP = os.environ.get("SPINE", "spine")
GAPS = os.path.join(SP, "gaps.csv")
TYPES = ("DOCID_STAMP_TRUNCATED", "DOCID_STAMP_ANOMALOUS")

def main():
    by_release = defaultdict(list)
    for line in open(os.path.join(SP, "pages.jsonl")):
        rec = json.loads(line)
        s = rec.get("doc_id_stamp")
        if s:
            by_release[rec["release_id"]].append((rec["pdf_page"], str(s)))

    new_rows = []
    n_full = 0
    for rid, pages in by_release.items():
        stamps = [s for _, s in pages]
        longest = max(len(s) for s in stamps)
        for page, s in pages:
            if len(s) == longest:
                n_full += 1
                continue
            longer = sorted({t for t in stamps if len(t) > len(s)})
            prefix_of = [t for t in longer if t.startswith(s)]
            if prefix_of:
                new_rows.append({"release_id": rid, "pdf_page": page,
                                 "gap_type": "DOCID_STAMP_TRUNCATED",
                                 "detail": f"doc_id_stamp '{s}' is a proper prefix of "
                                           f"'{max(prefix_of, key=len)}' on other pages of this release; "
                                           f"source pages.jsonl, not evaluated by the T3 "
                                           f"entities.csv check"})
            else:
                new_rows.append({"release_id": rid, "pdf_page": page,
                                 "gap_type": "DOCID_STAMP_ANOMALOUS",
                                 "detail": f"doc_id_stamp '{s}' shorter than longest stamp "
                                           f"'{max(longer, key=len)}' of this release but not a "
                                           f"prefix of any; source pages.jsonl"})

    with open(GAPS) as f:
        rdr = csv.DictReader(f)
        fields = rdr.fieldnames
        kept = [r for r in rdr if r["gap_type"] not in TYPES]
    with open(GAPS, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(kept + sorted(new_rows, key=lambda r: (r["release_id"], int(r["pdf_page"]))))

    from collections import Counter
    c = Counter(r["gap_type"] for r in new_rows)
    print(f"releases with doc_id_stamp: {len(by_release)}; "
          f"stamped pages: {sum(len(v) for v in by_release.values())}; "
          f"full-length: {n_full}")
    print(f"gap rows written: {dict(c)}")

if __name__ == "__main__":
    main()
