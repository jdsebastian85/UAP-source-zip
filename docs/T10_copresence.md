# T10 — Co-presence panel (Layer 5, query time only)

Source: `T10_copresence.pdf`, received 2026-08-09. Transcribed verbatim below.
Prototype fixture `relations.html` is a synthetic demonstration and is **not** in this repo;
it can be rebuilt from this spec. The spec is the load-bearing document.

Adds the missing analytical layer to `investigate.html`. The panel answers one question and
refuses to answer a second one: **what else sits on the pages where this entity sits**, and
never *what is this entity connected to*.

Merge into `site/investigator.html` + `scripts/build_investigator.py`.

## Why this belongs in the front end

`CLAUDE.md` says Layer 5 relations are derived at query time and never stored. That rule
makes co-presence a rendering problem, not a pipeline problem. Nothing in this task writes
to `spine/`.

## Build-time payload

`build_investigator.py` emits one additional embedded object. No new spine file.

Readability travels as a run-string per release, not per page. `R` = text layer, `L` = below
the published OCR floor of 60, `N` = no text layer.

> **Corrected 2026-09-06 (T11).** The `L` label above is wrong and the spec's own verification
> section below is right. `L` is derived from the `LOW_OCR_QUALITY` gap rows, which fire on a
> **page-level text-layer legibility proxy under 0.90** (`ingest.py:ocr_quality`, a 0–1
> character-composition measure over the shipped text layer). The published floor of 60 is a
> per-word tesseract confidence on 0–100 that governs `[unclear]` display of recovered words
> and backs no corpus-wide data yet. They are different measurements on different scales. The
> comb's hollow tick means *this page has a text layer that scores poorly on legibility*, and
> the UI must say that rather than "below the OCR confidence floor". See CLAUDE.md build
> invariants. It embeds rather than fetches. **If a
page carries both flags, `N` wins.**

**Verification gate.** The run-strings must expand to exactly 6,124 R / 818 L / 1,719 N =
8,661. Any other total means the gap rows and `pages.jsonl` disagree, and the panel must not
build.

`mentions` is keyed `doc#page` and holds entity **indices** into `entities`, not ids. A page
absent from `mentions` has no *extracted* entities, which is not the same as having none. A
page with `N` readability must never be presented as empty.

```json
{
  "corpus_build": "<stamp already used by marks export>",
  "docs":     [{"id":"DOW-UAP-D077","agency":"DOW","year":1966,"pages":85,
                "read":"R41,L3,N12,R29"}],
  "entities": [{"id":"e0412","label":"...","cluster":"c3|null","candidate":true}],
  "mentions": {"DOW-UAP-D077#14":[412,88]}
}
```

`cluster` comes from `aliases.yml`. All 10 clusters are unreviewed, so the default view is
raw surface form, with cluster grouping behind an explicit toggle. **Do not silently merge
unreviewed aliases into one node.**

`candidate` is the T3b flag (404 mentions / 300 groups).

## Scope and denominator

Scope for a subject = every page of every document where the subject appears, **including
unreadable pages**. That is the set where a co-mention could have existed. Coverage is
reported against that set, never against the readable subset alone.

## Acceptance criteria

1. Selecting a subject renders a per-page comb over the full scope: solid tick = text layer,
   hollow tick = below floor, amber tick = no text layer. Over ~520 pages the comb
   subsamples with a fixed stride and states the stride.
2. Every partner row shows documents / pages as two separate numbers plus the spread bar. A
   partner appearing 12 times inside one document must be visually distinguishable from one
   appearing 12 times across 9 documents.
3. Partner rows sort by document count first, page count second. Never by raw mention count
   alone.
4. A subject with zero partners renders the absence statement with the unread page count,
   not an empty list.
5. The pair test returns three distinct outcomes, matching the T9 rule: co-present (with
   cites), not observed (with the blind-spot count), and string not in the index (a miss in
   the index, not a fact about the corpus).
6. Candidate-flagged entities carry the marker in the picker, the subject head, and every
   partner row. A count built on a candidate is visibly provisional.
7. Cites are live: clicking one opens the existing byte-offset page reader at that page.
   Cites on `L` pages render dashed.
8. Nothing is written to `spine/`. `verify_spine.py` hash-identical before and after.
9. No copy anywhere in the panel uses "related to", "linked to", "connected to", or
   "network". The claim is co-presence on a cited page.
10. **The comb cannot be suppressed.** It is not behind a collapse control, not behind a
    media query, and not dropped at any viewport width. A test asserts that a rendered "not
    observed" panel containing no comb element is unproducible: the zero result and its
    denominator ship together, or the build fails. On narrow screens the comb subsamples
    further. It never hides.
11. **Media segments are out of scope and say so.** Until segment confidence is scored, media
    contributes no rows to the panel, and the panel displays a count of media segments not
    searched. Silent exclusion fails the same rule the comb enforces.

## Media segments — decided, with the reasoning kept

Held out. Media can carry a cite by timestamp, but with no confidence score a segment enters
with no denominator while document pages have one, and a coverage strip that is only partly
meaningful is worse than a narrower scope that is honest about its edge. Revisit when
segment confidence is scored. The run-string format extends to segments unchanged.

## Separable from PURSUE

The comb is a general pattern. Any search interface over partially machine-readable scanned
records reports hits without reporting the unreadable denominator, so a null result and a
blind spot look identical to the reader. Document it as a standalone UI pattern with PURSUE
as the worked example, not as a PURSUE feature.

---

# Verification against the corpus (added 2026-08-09, not part of the spec)

Run before committing the spec, so the next session starts from measured numbers rather
than estimates.

**Build gate passes.** Deriving per-page state from `pages.jsonl` (`no_text_layer`) plus the
`LOW_OCR_QUALITY` rows in `gaps.csv`, with `N` winning ties as the spec requires:

| | R | L | N | total |
|---|---|---|---|---|
| measured | 6,124 | 818 | 1,719 | 8,661 |
| spec gate | 6,124 | 818 | 1,719 | 8,661 |

**Payload cost, measured on real data.**

| Object | Size | Notes |
|---|---|---|
| `read` run-strings, RLE per the spec | **17.1 KB** | the 17.8 KB figure quoted in the spec was one char per page; RLE is slightly smaller, so 17.8 KB stands as an upper bound |
| `mentions` map, `doc#page` → entity indices | **213.5 KB** | 3,006 keys, 11,072 entries |
| combined addition to a 1.48 MB payload | ~230 KB | lands around 1.71 MB, still one file |

**Two facts the build should carry forward.**

- **5,655 of 8,661 pages are absent from the `mentions` map** — 65% of the corpus. That is
  the exact trap the spec names. At that scale the "absent ≠ has none" rule is not an edge
  case, it is the common case, and criterion 4's absence statement will be the panel's
  normal output rather than a rare one.
- The map holds 11,072 entries against 11,090 mentions, because it deduplicates an entity
  group appearing more than once on the same page. **Raw mention counts cannot be recovered
  from it.** That is consistent with criterion 3, which forbids sorting by raw mention count
  anyway, but it means the payload structurally cannot support a metric the spec already
  rules out — worth knowing rather than rediscovering.
