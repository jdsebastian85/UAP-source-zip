# CLAUDE.md — PURSUE UAP Release Corpus

You are working on a structured analysis of a Department of War (DOW) / PURSUE
initiative UAP declassified document and media release. This file governs how you
work on it. Read it fully before touching anything. It overrides your defaults.

## What this project is

A **spine**: a fixed, repeatable structure that every release file passes through, so
that documents arriving one at a time accumulate into one queryable corpus. The spine
records what the documents say and where they say it. It does not evaluate, rank, or
conclude.

The output is a public, citable research resource. Its entire value rests on being
trustworthy about provenance. A single unmarked inference poisons the whole thing,
because a reader cannot tell which rows to trust once one row is wrong.

## Operating rules — non-negotiable

1. **No opinions. No assumptions.** You extract, index, and measure. You do not
   interpret what an object "is," what a redaction "hides," or what a gap "means."
2. **Every stored value is verbatim from the page**, or a mechanically derived
   measurement (character count, hash, page number, duration, pixel coordinate).
   No paraphrase inside the data files. Paraphrase belongs in prose summaries only,
   and even there it is labeled as summary.
3. **Every row carries `release_id` + page (or timestamp, for media).** A statement
   without a cite is not stored. If you cannot cite it, drop it.
4. **Text source is tagged.** `TEXT_LAYER` (publisher's OCR, shipped in the PDF) vs
   `OCR_RECOVERED` (produced locally). These are never merged or treated as equivalent.
5. **Absence is recorded, never assumed.** A referenced enclosure not present in the
   dump is logged as `ENCLOSURE_REFERENCED` — not as "missing," not as "withheld,"
   not as "suppressed." You do not know why it is not there.
6. **Contradictions are preserved side by side, both cited.** There is no merge step,
   no reconciliation, no "most likely" value. Example currently in the corpus: witness
   distance 500–600 m vs AARO-assessed ~1,050 m for the same event. Both stand.
7. **Entities are candidates, not facts.** `entities.csv` is a retrieval index built by
   regex. It is not a verified roster. Never present an entity row as established.
8. **Flag monetary/commercial angles unprompted.** If something in the work has a
   revenue, licensing, grant, or career implication, say so in your prose summary —
   the project owner has standing instructions to be told, without being asked.

## Language discipline

Use natural language and normal punctuation. Limit hyphens. Watch for run-on
sentences. Do not pad prose with hedging boilerplate, and do not editorialize about
the subject matter in either direction — no debunking tone, no believer tone. Describe
what is on the page or in the frame.

When you describe imagery, describe **what is visible**: shape, brightness, motion
relative to frame, sensor overlay elements, redaction blocks. Do not name a cause.
"Small dark object crosses frame left to right against cloud layer" is correct.
"Object performs a controlled maneuver" is not.

## Corpus state at handoff (2026-08-07)

- **211 documents / 8,661 pages**, 11 agency prefixes, span 1944–2026
  (document coverage: earliest and latest year token in `release_id` + `subject_meta`,
  derived from the 117 of 211 documents that carry one. Not the same as the earliest date
  *mentioned* in the text, which is 1848 — see below.)
- **112 videos / 8.38 hours**
- 580 segments, 11,090 entity mentions
- Gaps logged: 1,719 NO_TEXT_LAYER, 818 LOW_OCR_QUALITY, 251 ENCLOSURE_REFERENCED,
  127 REDACTION_MARKER

Known page-weight finding: DOW has the most releases but FBI-legacy numbered files are
~41% of all pages, and a single FBI file (65-HS1 / 62-HQ-83894, 2,647 pages) is ~31%
of the whole corpus. Temporal shape is bimodal: 1946–1969 peak, 2020–2026 peak, with a
valley across the 1970s–2010s. **Cause of the valley is undetermined and is recorded as
a gap, not explained.**

## Media families (Layer 0 observed, not concluded)

| Family | Count | Encode date | Character |
|---|---|---|---|
| `video_2605_DOD_*` | 50 | 2026-05-20/21 | **Edited presentation products.** Contains title cards ("UAP 2021 — B/W values inverted, picture zoomed", "Original Video"), zoom insets, processing annotations. An analysis cell handled this footage before release. |
| `DOD_111830*` | 23 | 2026-07-09 | Military sensor/FLIR with burned-in redaction blocks. Includes 4 long NASA seismograph renders. |
| `DOD_111887*` | 15 | 2026-08-06 | Screen-recorded optical scope family (six clips share an identical reticle and circle/triangle annotation symbology), plus composites. |
| `DOD_111764*` | 8 | 2026-06-10 | Handheld/phone-style outdoor footage plus seismograph renders. |
| `DOD_111688*` / `DOD_111689*` | 16 | 2026-05-07/08 | ISR imagery, heaviest per-frame redaction in the media set. |

**Cross-family fact worth carrying:** 11 clips totaling roughly 5 hours are NASA
watermarked seismograph waveform animations, not sky footage. By duration they are the
majority of the media corpus. They pair with the NASA Apollo/Skylab transcript releases
(D1–D7). Record the pairing; do not theorize about it.

## Spine layers

| Layer | File | Unit |
|---|---|---|
| 0 Provenance | `manifest.csv`, `media.csv`, `images.csv` | one release file |
| 1 Page | `pages.jsonl` | one page |
| 2 Record | `segments.csv` | one memo/letter inside a release |
| 3 Entity | `entities.csv` | one mention |
| 4 Assertion | `assertions.csv` (hand-built, not yet started) | one claim |
| 5 Relational | derived at query time, never stored | pairs |
| 6 Gap | `gaps.csv` | one defect |

**Layer 5 is derived at query time and never written to disk.** A derived edge that
gets stored starts getting cited as if it were on the page. This is the single easiest
way to corrupt the corpus. Do not do it.

`assertions.csv` columns: `release_id, pdf_page, segment_no, speaker_verbatim,
assertion_verbatim, statement_type, addressed_to`

`statement_type` is a closed set describing the **grammatical form** of a statement,
never its truth: `DIRECTIVE`, `FINDING`, `OBSERVATION_REPORT`, `RECOMMENDATION`,
`POLICY_STATEMENT`, `STATUS`, `REQUEST`, `DENIAL`, `REFERENCE`. If a sentence resists
the set, record `UNCLASSIFIED_FORM` rather than forcing a fit.

## Working style with this project owner

- He works from a phone much of the time and steps away often. Leave the repo in a
  runnable state after every task; never leave a half-written CSV.
- He wants efficiency and low redundancy. Do not re-explain what he already knows.
- Do not ask permission for reversible in-repo work. Ask before anything destructive,
  anything that costs money, and anything that publishes.
- Report findings as findings, with the cite. If a result is ambiguous, say it is
  ambiguous rather than picking a side.
- Disagree with him when the data disagrees with him. That is the job.
