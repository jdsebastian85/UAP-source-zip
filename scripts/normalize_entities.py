#!/usr/bin/env python3
"""T3 + T3b entity normalization and candidate-flag pass.

Reads spine/entities.csv (never modified), writes:
  spine/entities_normalized.csv   - all rows, value_verbatim preserved,
                                    value_normalized + norm_rule + candidate_flags
  spine/entity_collapse_report.md - every distinct merge decision with counts,
                                    flag rule definitions and counts, and
                                    candidates deliberately NOT merged

Rules are mechanical and conservative. Re-running produces identical output.

Normalization (T3, T3b.3):
  R1 RANK    successive leading military rank tokens canonicalized (PERSON rows).
             Applied in secondary position too, so "Lt. Cdr." / "Lt. Comdr." /
             "Lt. Commander" all normalize to "Lt Cmdr" (T3b.3).
  R2 LAPAZ   name token whose letters, dots and spaces removed, spell "lapaz" or
             "lepaz" is rewritten "LaPaz" (Le.Paz/LePaz merged on the authority
             of CONTEXT_BRIEF.md, which documents them as OCR splittings).
  R3 MARKING marking uppercased (MARKING rows only; pure case operation).
  R4 WS      leading/trailing whitespace trimmed, internal runs collapsed.

Candidate flags (T3b.1) - measurements of the normalized string, PERSON rows
only; every non-PERSON row is marked CLEAN because no flag rule targets it:
  TRUNCATED       ends in a hyphen, or final token is 1-3 chars after stripping
                  trailing punctuation and is not a single-letter initial with a
                  period nor a generational suffix (Jr, Sr, II, III, IV)
  MULTI_RANK      two or more successive rank units at the start of the value
                  (compound ranks like "Lt Col", "Maj Gen", "Lt Cmdr" count as
                  one unit)
  FORM_LABEL      contains an all-caps administrative boilerplate word:
                  SURNAME, COORDINATING, DISTRIBUTION, ORIGINAL, FILE
  TRAILING_PROSE  a period followed by a sentence-starter word from the closed
                  list: But He She It The They This That We And So His Her Who
                  When Then There
  CLEAN           none of the above

Anything requiring a judgment call (OCR misreads like "LaPar", "Garret",
"Ge.rrett") is NOT merged; those live in spine/aliases.yml as unreviewed
retrieval hints, never in this file's normalized values.
"""
import csv, os, re, sys
from collections import Counter

SP = os.environ.get("SPINE", "spine")
SRC = os.path.join(SP, "entities.csv")
DST = os.path.join(SP, "entities_normalized.csv")
RPT = os.path.join(SP, "entity_collapse_report.md")

# R1: rank tokens -> canonical form. Longest/compound patterns first.
RANK_CANON = [
    (r"(?:lt\.?\s*col(?:onel)?\.?|lieutenant\s+colonel|ltc)", "Lt Col"),
    (r"(?:lt\.?\s*gen(?:eral)?\.?|lieutenant\s+general)", "Lt Gen"),
    (r"(?:lt\.?\s*(?:cmdr|cdr|comdr)\.?|lt\.?\s*commander|lieutenant\s+commander)", "Lt Cmdr"),
    (r"(?:maj\.?\s*gen(?:eral)?\.?|major\s+general)", "Maj Gen"),
    (r"(?:brig\.?\s*gen(?:eral)?\.?|brigadier\s+general)", "Brig Gen"),
    (r"(?:col(?:onel)?\.?)", "Col"),
    (r"(?:capt(?:ain)?\.?)", "Capt"),
    (r"(?:maj(?:or)?\.?)", "Maj"),
    (r"(?:gen(?:eral)?\.?)", "Gen"),
    (r"(?:sgt\.?|sergeant)", "Sgt"),
    (r"(?:cmdr\.?|cdr\.?|comdr\.?|commander)", "Cmdr"),
    (r"(?:lt\.?|lieutenant)", "Lt"),
]
RANK_RES = [(re.compile(r"^" + pat + r"(?=\s|$)", re.I), canon) for pat, canon in RANK_CANON]

# R2: a whitespace/dot-mangled LaPaz token, e.g. La.Paz  LaPa.z  La Paz  Le.Paz
LAPAZ_RE = re.compile(r"(?<![A-Za-z])l\s*[ae]\s*\.?\s*p\s*a\s*\.?\s*z(?![A-Za-z])", re.I)

SUFFIX_OK = {"Jr", "Sr", "II", "III", "IV"}
PROSE_RE = re.compile(r"\.\s+(?:But|He|She|It|The|They|This|That|We|And|So|His|Her|Who|When|Then|There)\b")
FORM_RE = re.compile(r"\b(?:SURNAME|COORDINATING|DISTRIBUTION|ORIGINAL|FILE)\b")

def norm_ranks(s):
    """Consume successive rank units from the front. Returns (string, n_units)."""
    parts, rest = [], s
    while True:
        for rx, canon in RANK_RES:
            m = rx.match(rest)
            if m:
                parts.append(canon)
                rest = rest[m.end():].lstrip()
                break
        else:
            break
    if not parts:
        return s, 0
    return " ".join(parts) + ((" " + rest) if rest else ""), len(parts)

def norm_person(v):
    rules, out = [], v
    m = LAPAZ_RE.search(out)
    if m and re.sub(r"[.\s]", "", m.group(0)).lower() in ("lapaz", "lepaz"):
        out = LAPAZ_RE.sub("LaPaz", out)
        rules.append("LAPAZ")
    ranked, n_units = norm_ranks(out)
    if ranked != out:
        out = ranked
        rules.append("RANK")
    return out, rules, n_units

def person_flags(norm, n_units):
    f = []
    if norm.endswith("-"):
        f.append("TRUNCATED")
    else:
        toks = norm.split()
        if toks:
            last = toks[-1]
            if not re.fullmatch(r"[A-Z]\.", last):
                bare = last.rstrip(".,;:")
                if 1 <= len(bare) <= 3 and bare not in SUFFIX_OK:
                    f.append("TRUNCATED")
    if n_units >= 2:
        f.append("MULTI_RANK")
    if FORM_RE.search(norm):
        f.append("FORM_LABEL")
    if PROSE_RE.search(norm):
        f.append("TRAILING_PROSE")
    return ";".join(f) if f else "CLEAN"

def main():
    rows = list(csv.DictReader(open(SRC)))
    changes = Counter()
    rule_counts = Counter()
    flag_counts = Counter()
    out_rows = []
    for r in rows:
        v = r["value_verbatim"]
        out, rules = v, []
        ws = re.sub(r"\s+", " ", out.strip())
        if ws != out:
            out = ws
            rules.append("WS")
        n_units = 0
        if r["entity_type"] == "PERSON":
            out, prules, n_units = norm_person(out)
            rules += prules
        elif r["entity_type"] == "MARKING":
            up = out.upper()
            if up != out:
                out = up
                rules.append("MARKING")
        flags = person_flags(out, n_units) if r["entity_type"] == "PERSON" else "CLEAN"
        for fl in flags.split(";"):
            flag_counts[fl] += 1
        if out != v:
            changes[(v, out, r["entity_type"])] += 1
            for ru in rules:
                rule_counts[ru] += 1
        out_rows.append({**r, "value_normalized": out,
                         "norm_rule": "+".join(rules) if out != v else "",
                         "candidate_flags": flags})

    with open(DST, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["release_id", "pdf_page", "entity_type",
                                          "value_verbatim", "value_normalized",
                                          "norm_rule", "candidate_flags"])
        w.writeheader()
        w.writerows(out_rows)

    changed = sum(changes.values())
    clean = flag_counts.get("CLEAN", 0)
    with open(RPT, "w") as f:
        f.write("# Entity collapse report (T3 + T3b)\n\n")
        f.write(f"Input: {len(rows)} rows in entities.csv (untouched). ")
        f.write(f"Output: {len(out_rows)} rows in entities_normalized.csv.\n\n")
        f.write(f"Rows changed: {changed}. Rule firings: {dict(rule_counts)}.\n\n")
        f.write("`value_normalized` is a retrieval convenience only. "
                "`value_verbatim` is the evidence and is preserved on every row.\n\n")
        f.write("## Candidate flags (T3b.1)\n\n")
        f.write("Flags are measurements of the normalized string, not judgments "
                "about the person. Rules are defined in the header of "
                "`scripts/normalize_entities.py` and are reproducible by "
                "re-running it. Flag rules target PERSON capture defects; "
                "non-PERSON rows are marked CLEAN because no rule addresses "
                "them.\n\n")
        f.write("| flag | rows |\n|---|---|\n")
        for fl, c in sorted(flag_counts.items(), key=lambda x: -x[1]):
            f.write(f"| {fl} | {c} |\n")
        f.write(f"\nCLEAN rows: {clean} of {len(out_rows)} "
                f"({len(out_rows) - clean} carry at least one flag).\n\n")
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
                "verbatim in both columns. They are listed as unreviewed retrieval "
                "hints in `spine/aliases.yml` (T3b.2), which search expands through "
                "at query time; nothing from that file is written into any CSV:\n\n")
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
        f.write("\n## DocId stamps\n\n")
        f.write("DocId stamps do not appear in entities.csv; they live in "
                "pages.jsonl under `doc_id_stamp`. Truncation is assessed against "
                "that source by `scripts/assess_docid_stamps.py` (T3b.4), which "
                "logs cited gap rows in gaps.csv. The T3 check that looked only "
                "at entities.csv was mis-scoped and its 'nothing found' result "
                "is superseded.\n")
    print(f"{len(out_rows)} rows written, {changed} changed, rules {dict(rule_counts)}")
    print(f"flags: {dict(flag_counts)}")

if __name__ == "__main__":
    main()
