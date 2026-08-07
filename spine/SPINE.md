# Analysis Spine — DoD/DoW UAP Release Dump

Purpose: a fixed, repeatable structure that every release PDF passes through, so that
documents arriving one at a time accumulate into one queryable corpus. The spine records
what the documents say and where they say it. It does not evaluate, rank, or conclude.

## Evidence rules (applied at every layer)

1. Every stored value is verbatim from the page, or a mechanically derived measurement
   (character count, hash, page number). No paraphrase in the data files.
2. Every row carries `release_id` + `pdf_page`. A statement without a cite is not stored.
3. Source of text is tagged: `TEXT_LAYER` (publisher's OCR, shipped in the PDF) vs
   `OCR_RECOVERED` (produced locally from a raster pass). These are not interchangeable.
4. Absence is recorded, never assumed. A referenced enclosure that is not in the dump is
   logged as a gap, not as a missing document, and not as a withheld one.
5. Names, dates, and organizations extracted by pattern are candidates until eyeballed on
   the page. `entities.csv` is an index for retrieval, not a verified roster.
6. Contradictions between documents are preserved as separate rows with both cites. The
   spine has no merge or reconciliation step.

## Layers

| Layer | File | Unit | Holds |
|---|---|---|---|
| 0 Provenance | `manifest.csv` | one release PDF | release ID, embedded metadata, producer, SHA-256, page count, OCR quality mean |
| 1 Page | `pages.jsonl` | one page | full text, release stamp (NW), Docld stamp, markings, extracted entities, char count, quality score |
| 2 Record | `segments.csv` | one memo/letter/minutes inside a release | start/end page, subject line, TO/FROM routing, first date |
| 3 Entity | `entities.csv` | one mention | PERSON / ORG / DATE / LOCATOR / MARKING, verbatim, with page cite |
| 4 Assertion | `assertions.csv` (manual) | one claim | verbatim quote, who states it, page cite, and what kind of statement it is |
| 5 Relational | derived at query time | pairs | co-occurrence of persons/orgs by segment; document→document references; timeline |
| 6 Gap | `gaps.csv` | one defect | NO_TEXT_LAYER, LOW_OCR_QUALITY, REDACTION_MARKER, ENCLOSURE_REFERENCED |

### Layer 4 — assertion ledger (the only hand-built file)

Columns: `release_id, pdf_page, segment_no, speaker_verbatim, assertion_verbatim, statement_type, addressed_to`

`statement_type` is a closed set describing the grammatical form of the statement, not its
truth: `DIRECTIVE` (orders an action), `FINDING` (states a determination reached),
`OBSERVATION_REPORT` (relays a witnessed event), `RECOMMENDATION`, `POLICY_STATEMENT`,
`STATUS`, `REQUEST`, `DENIAL` (states a thing did not occur or does not exist),
`REFERENCE` (points to another document). Choosing a type is a reading of the sentence's
form; if a sentence resists the set, record it as `UNCLASSIFIED_FORM` rather than forcing it.

### Layer 5 — relational patterns (derived, never stored as fact)

Three joins carry most of the analytic weight across a dump like this:

- **Person × segment** — who appears together in the same record. Co-appearance is
  co-appearance; it is not collaboration, agreement, or knowledge.
- **Org × date** — which offices appear in which months. Shows where correspondence
  volume sits over time, and where it stops.
- **Document → document** — segments whose text cites another Docld, subject line, or
  dated memo. This is what turns 85 loose pages into a chain, and it is also where the
  chain visibly breaks.

Query these from `pages.jsonl` at analysis time. Do not bake them into stored rows: a
derived edge that gets stored starts getting cited as if it were on the page.

## Running it

```bash
python3 ingest.py /mnt/user-data/uploads/<next-release>.pdf   # idempotent per release
python3 ocr_fallback.py /mnt/user-data/uploads/<next-release>.pdf   # only if gaps.csv shows NO_TEXT_LAYER
```

Re-running `ingest.py` on a release replaces that release's rows and leaves every other
release untouched, so files can arrive in any order and be reprocessed after a schema change.

## Known condition of the source PDFs

The release PDFs are scans run through Adobe Paper Capture. The shipped text layer is
lossy and inconsistent: control stamps come out truncated (`Docld:34714841` also appears
as `Docld:347`, `Docld:3471`), and some pages carry no text layer at all despite being
full of typed text. Any page-level absence must be checked against a local OCR pass before
it is described as blank.
