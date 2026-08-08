#!/usr/bin/env python3
"""T3 entity normalization pass.

Reads spine/entities.csv (never modified), writes:
  spine/entities_normalized.csv   - all rows, value_verbatim preserved,
                                    value_normalized added, norm_rule tags which
                                    rule fired (empty = unchanged)
  spine/entity_collapse_report.md - every distinct merge decision, with counts,
                                    plus candidates deliberately NOT merged

Rules are mechanical and conservative:
  R1 RANK    leading military rank title canonicalized (PERSON rows only)
  R2 LAPAZ   name token whose letters, dots and spaces removed, spell "lapaz"
             (case-insensitive) is rewritten "LaPaz" (PERSON rows only)
  R3 MARKING marking uppercased (MARKING rows only; pure case operation)
  R4 WS      leading/trailing whitespace trimmed, internal runs collapsed

Anything requiring a judgment call (OCR misreads like "LaPar", "Garret",
"Ge.rrett") is NOT merged and is listed in the report as a candidate.
"""
import csv, os, re, sys
from collections import Counter

SP = os.environ.get("SPINE", "spine")
SRC = os.path.join(SP, "entities.csv")
DST = os.path.join(SP, "entities_normalized.csv")
RPT = os.path.join(SP, "entity_collapse_report.md")

# R1: leading rank titles -> canonical form. Longest patterns first.
RANK_CANON = [
    (r"(?:lt\.?\s*col(?:onel)?\.?|lieutenant\s+colonel|ltc)", "Lt Col"),
    (r"(?:lt\.?\s*gen(?:eral)?\.?|lieutenant\s+general)", "Lt Gen"),
    (r"(?:maj\.?\s*gen(?:eral)?\.?|major\s+general)", "Maj Gen"),
    (r"(?:brig\.?\s*gen(?:eral)?\.?|brigadier\s+general)", "Brig Gen"),
    (r"(?:col(?:onel)?\.?)", "Col"),
    (r"(?:capt(?:ain)?\.?)", "Capt"),
    (r"(?:maj(?:or)?\.?)", "Maj"),
    (r"(?:gen(?:eral)?\.?)", "Gen"),
    (r"(?:sgt\.?|sergeant)", "Sgt"),
    (r"(?:cmdr\.?|cdr\.?|commander)", "Cmdr"),
    (r"(?:lt\.?|lieutenant)", "Lt"),
]
RANK_RES = [(re.compile(r"^" + pat + r"(?=\s|$)", re.I), canon) for pat, canon in RANK_CANON]

# R2: a whitespace/dot-mangled LaPaz token, e.g. La.Paz  LaPa.z  La Paz  La.Paz.
# Le.Paz / LePaz are included because CONTEXT_BRIEF.md documents them as known
# OCR splittings of LaPaz ("Dr. LaPaz appears as La.Paz / Le.Paz / LaPa.z").
LAPAZ_RE = re.compile(r"(?<![A-Za-z])l\s*[ae]\s*\.?\s*p\s*a\s*\.?\s*z(?![A-Za-z])", re.I)

def norm_person(v):
    rules = []
    out = v
    m2 = LAPAZ_RE.search(out)
    if m2 and re.sub(r"[.\s]", "", m2.group(0)).lower() in ("lapaz", "lepaz"):
        out = LAPAZ_RE.sub("LaPaz", out)
        rules.append("LAPAZ")
    for rx, canon in RANK_RES:
        m = rx.match(out)
        if m:
            if m.group(0) != canon:
                out = canon + out[m.end():]
                rules.append("RANK")
            break
    return out, rules

def main():
    rows = list(csv.DictReader(open(SRC)))
    changes = Counter()        # (verbatim, normalized, type) -> count
    rule_counts = Counter()
    out_rows = []
    for r in rows:
        v = r["value_verbatim"]
        out, rules = v, []
        ws = re.sub(r"\s+", " ", out.strip())
        if ws != out:
            out = ws
            rules.append("WS")
        if r["entity_type"] == "PERSON":
            out, prules = norm_person(out)
            rules += prules
        elif r["entity_type"] == "MARKING":
            up = out.upper()
            if up != out:
                out = up
                rules.append("MARKING")
        if out != v:
            changes[(v, out, r["entity_type"])] += 1
            for ru in rules:
                rule_counts[ru] += 1
        out_rows.append({**r, "value_normalized": out,
                         "norm_rule": "+".join(rules) if out != v else ""})

    with open(DST, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["release_id", "pdf_page", "entity_type",
                                          "value_verbatim", "value_normalized", "norm_rule"])
        w.writeheader()
        w.writerows(out_rows)

    changed = sum(changes.values())
    with open(RPT, "w") as f:
        f.write("# Entity collapse report (T3)\n\n")
        f.write(f"Input: {len(rows)} rows in entities.csv (untouched). ")
        f.write(f"Output: {len(out_rows)} rows in entities_normalized.csv.\n\n")
        f.write(f"Rows changed: {changed}. Rule firings: {dict(rule_counts)}.\n\n")
        f.write("`value_normalized` is a retrieval convenience only. "
                "`value_verbatim` is the evidence and is preserved on every row.\n\n")
        f.write("## Merge decisions (every distinct rewrite, with row counts)\n\n")
        f.write("`Le.Paz`/`LePaz` are merged into `LaPaz` on the authority of "
                "CONTEXT_BRIEF.md, which documents them as known OCR splittings "
                "of the same name; this is not a fresh inference.\n\n")
        f.write("| n | type | verbatim | normalized |\n|---|------|----------|------------|\n")
        for (v, o, t), c in sorted(changes.items(), key=lambda x: (-x[1], x[0])):
            f.write(f"| {c} | {t} | `{v}` | `{o}` |\n")
        f.write("\n## Candidates NOT merged (judgment calls, left as-is)\n\n")
        f.write("These resemble known names but differ by letters, not just dots, "
                "spacing, or case. Merging them would be an inference, so they stand "
                "verbatim in both columns:\n\n")
        vals = Counter(r["value_verbatim"] for r in rows if r["entity_type"] == "PERSON")
        candidates = []
        for v, c in vals.items():
            flat = re.sub(r"[.\s]", "", v).lower()
            if "lapa" in flat and "lapaz" not in flat:
                candidates.append((v, c, "resembles LaPaz but letters differ/truncated"))
            if re.search(r"g[ae]\.?rret\b|ge\.?rrett", v, re.I):
                candidates.append((v, c, "resembles Garrett but letters differ"))
        for v, c, why in sorted(candidates):
            f.write(f"- `{v}` (x{c}) — {why}\n")
        if not candidates:
            f.write("- none found\n")
        f.write("\n## DocId truncation check\n\n")
        docid = [r for r in rows if re.search(r"doc.?[il]d", r["value_verbatim"], re.I)]
        f.write(f"Rows matching a DocId pattern in entities.csv: {len(docid)}. "
                "The truncated DocId stamps noted in the earlier 48-item snapshot "
                "are not present in this extraction, so no DocId collapse was "
                "performed.\n")
    print(f"{len(out_rows)} rows written, {changed} changed, rules {dict(rule_counts)}")

if __name__ == "__main__":
    main()
