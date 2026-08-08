#!/usr/bin/env python3
"""Query-time entity search with alias expansion (T3b.2) and disclosed
filtering (T3b.1 flags).

Usage: python3 scripts/search_entities.py QUERY [--all]

Matches QUERY case-insensitively against value_verbatim and value_normalized
in spine/entities_normalized.csv. If QUERY names an alias cluster or matches
one of its members, the search also returns rows matching the cluster's other
members, labeled as alias matches with the cluster's confidence. Alias
expansion is a retrieval hint: "also matches", never "same as".

By default rows whose candidate_flags are not CLEAN are hidden, and the count
of hidden rows is always printed. --all shows them. No file is modified.
"""
import csv, json, os, sys

SP = os.environ.get("SPINE", "spine")

def load_aliases(path):
    """Parse the restricted YAML shape used by spine/aliases.yml.
    Falls back gracefully if PyYAML is absent; flow lists are JSON-compatible."""
    try:
        import yaml
        with open(path) as f:
            return yaml.safe_load(f) or []
    except ImportError:
        clusters, cur = [], None
        for line in open(path):
            s = line.rstrip("\n")
            if not s.strip() or s.strip().startswith("#"):
                continue
            if s.startswith("- cluster:"):
                cur = {"cluster": s.split(":", 1)[1].strip()}
                clusters.append(cur)
            elif cur is not None and ":" in s:
                k, v = s.strip().split(":", 1)
                v = v.strip()
                cur[k.strip()] = json.loads(v) if v.startswith("[") else v
        return clusters

def main():
    args = [a for a in sys.argv[1:] if a != "--all"]
    show_all = "--all" in sys.argv[1:]
    if not args:
        sys.exit("usage: search_entities.py QUERY [--all]")
    q = " ".join(args).lower()

    aliases = load_aliases(os.path.join(SP, "aliases.yml"))
    active = [c for c in aliases
              if q == c["cluster"].lower()
              or any(q in m.lower() or m.lower() in q for m in c["members"])]
    expansion = {}  # member(lower) -> cluster dict
    for c in active:
        for m in c["members"]:
            expansion[m.lower()] = c

    rows = list(csv.DictReader(open(os.path.join(SP, "entities_normalized.csv"))))
    direct, alias_hits = [], []
    for r in rows:
        vv, vn = r["value_verbatim"].lower(), r["value_normalized"].lower()
        if q in vv or q in vn:
            direct.append((r, None))
        else:
            for m, c in expansion.items():
                if m in vv or m in vn:
                    alias_hits.append((r, c))
                    break

    hits = direct + alias_hits
    flagged = [(r, c) for r, c in hits if r["candidate_flags"] != "CLEAN"]
    shown = hits if show_all else [(r, c) for r, c in hits if r["candidate_flags"] == "CLEAN"]

    for r, c in shown:
        cite = f"{r['release_id']}:{r['pdf_page']}"
        label = ""
        if c is not None:
            label = f"  [also matches via cluster '{c['cluster']}' — {c.get('confidence','unreviewed')}]"
        flg = f"  [{r['candidate_flags']}]" if r["candidate_flags"] != "CLEAN" else ""
        print(f"{cite:55} {r['entity_type']:8} {r['value_verbatim']!r}{flg}{label}")

    print(f"\nshowing {len(shown)} of {len(hits)} candidate mentions matching {q!r}"
          f" — {len(flagged)} flagged as fragments or over-captures"
          f"{' (shown)' if show_all else ' (hidden; pass --all to show)'}")
    for c in active:
        n_members = len(c["members"])
        print(f"alias cluster '{c['cluster']}' expanded the search across "
              f"{n_members} spelling{'s' if n_members != 1 else ''} "
              f"— confidence: {c.get('confidence', 'unreviewed')}"
              + (" (no human has reviewed the cited pages yet)"
                 if c.get("confidence") == "unreviewed" else ""))
    print("entity rows are regex candidates, not a verified roster; "
          "alias expansion is a retrieval hint, not an identity claim")

if __name__ == "__main__":
    main()
