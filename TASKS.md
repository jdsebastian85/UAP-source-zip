# TASKS.md — work queue

Ordered by value per unit of effort. Each task states its acceptance criteria. Do not
mark a task done until the criteria are met and the spine files still load cleanly.

Run `python3 scripts/verify_spine.py` after every task. It is cheap and it catches
schema drift, orphan rows, and uncited rows before they compound.

---

## T0. Environment setup (do first, once)

```bash
sudo apt install -y tesseract-ocr poppler-utils ffmpeg
pip install pdfplumber pypdf opencv-python-headless numpy pillow pytesseract
```

Layout expected by every script:

```
uap-corpus/
  CLAUDE.md  TASKS.md  README.md
  spine/          <- unpack spine_snapshot.zip here (the derived data)
  sources/pdf/    <- 211 PDFs, re-pulled from Drive
  sources/media/  <- 112 videos, re-pulled from Drive
  scripts/
  site/
```

**Acceptance:** `python3 scripts/verify_spine.py` runs and reports 211 docs, 112 media
rows, no schema errors.

---

## T1. Confirm the remaining Drive zips are not duplicates — BEFORE downloading

The loose video uploads may already contain everything in the pending zips. Downloading
duplicates wastes a night.

List each zip's contents without extracting, diff filenames against `media.csv`, and
report the overlap. Only pull a zip that contains genuinely new files.

Zips present in the Drive folder as of 2026-08-08 (`Release_1.zip` 1.22 GB,
`release_03_documents.zip` 867 MB, `Archive.zip` 69 MB, plus `spine snapshot.zip` 610 KB
which is this repo's own snapshot, not source material). Contents are not listable through
the Drive API — a zip is one opaque file to it — so this needs a machine that can download
and `unzip -l` them.

**Acceptance:** a written diff per zip: N files, M already in media.csv, K new.

**Done on the video side (2026-08-08):** the Drive folder was listed in full and diffed
against `media.csv`. The folder holds 135 items: 131 `.mp4` and 4 zips. Two further corpus
videos sit in the Drive account root rather than in the folder, so the corpus has 133
videos in Drive in total. All 112 `media.csv` rows resolve to a live Drive file. See T1b.

---

## T1b. Ingest the 21 videos that are in Drive but not in the spine

Listed in `media_links.csv` as `spine_status = NOT_INGESTED`. They are not a new release
family — every one belongs to a family already in the corpus:

| Family | In the release folder | In the Drive root |
|---|---|---|
| `DOD_111688*` / `DOD_111689*` (ISR) | 12 | — |
| `video_2605_DOD_*` (edited presentation products) | 7 | — |
| `DOD_111764796-1920x1080-9000k` | — | 1 |
| `DOD_111887384` | — | 1 |
| **Total** | **19** | **2** |

Nineteen inside the folder, twenty-one counting the two that sit in the Drive account root
rather than in the folder. Both numbers are right about different sets; the ingest pass
should take all 21. The in-folder split is 12 ISR and 7 `video_2605_*`, verified against
`media_links.csv`.

Needs the files on disk: `ffprobe` for the Layer 0 row, frame extraction for the triage
strip. Run the existing media ingest path, then re-run `scripts/build_media_links.py` so
`spine_status` flips to `INDEXED`.

**Acceptance:** `media.csv` at 133 rows, `verify_spine.py` OK, `media_links.csv` showing
`NOT_INGESTED` 0.

---

## T1c. Documents cannot be linked until the zips are extracted

The 211 PDFs are not files in Drive. They are contents of the zips above. Drive can only
address a file, and nothing can address a path inside a zip, so there is no URL to store
for any document until the archives are extracted into a Drive folder as individual files.

This is the blocker on a document-side `media_links.csv` equivalent, and it needs a
computer — extracting 2 GB of zips is not something the Drive API can be asked to do.

**Acceptance:** 211 PDFs present as individual Drive files; a `doc_links.csv` built the
same way as `media_links.csv`, joined on `manifest.csv` release_id.

---

## T2 (revised). Readable transcripts, and the page image beside them

2,537 pages need OCR: 1,719 with no text layer, 818 with low quality.

Order, from the spec: **T2.4 first** (display only, no rerun), then T2.2 + T2.1 + T2.3 as
one OCR pass, then T2.5 and T2.6 once hosting is decided. Run `verify_spine.py` after each.
`pages.jsonl` stays byte-identical throughout: recovered text lives in `ocr_recovered.csv`
and is never written into the shipped-text layer.

**The published confidence floor is 60** (tesseract word confidence, 0–100). It is stated
in the header of `scripts/build_investigator.py` and shown in the tool. The OCR pass must
use the same number for its entity cutoff.

### T2.4 — Render honestly in the tool — DONE 2026-08-09

Shipped ahead of the OCR rerun, as the spec ordered. In the page view:
- `[REDACTED]` renders as a drawn block, not as the literal word sitting in the sentence.
- Words below the floor render dimmed with the score on tap, so a bad transcript is
  legible as a bad transcript.
- Every page states its source: shipped text layer, locally recovered, or neither, with
  the mean confidence for that page.
- A page with no text from either source says exactly that, instead of showing an empty
  panel that reads as nothing being there.

The renderer already speaks the T2.3 word schema. `build_investigator.py` reads
`ocr_recovered.csv` in either shape and byte-indexes it per page, so the OCR pass only has
to write the file — no display work is left. Until it runs, the existing 61 recovered pages
are page-per-row with no scores, and the panel says so rather than implying confidence
that was never measured.

### T2.1 — Redaction-aware OCR — NOT STARTED

Detect filled rectangles, mask them white, OCR the cleaned image, reinsert `[REDACTED]` at
the block's reading-order position. Write `redactions.csv`:
`release_id, pdf_page, bbox, area_px, method`.

Do not attempt to recover redacted content by any means. The block is the fact.

The tool already reads `redactions.csv` and counts blocks per page separately from the
`REDACTION_MARKER` gap rows. A drawn block and a typed marker are different observations
and are displayed as different pills.

### T2.2 — Preprocessing before OCR — NOT STARTED

Upscale to ~300 dpi, deskew, adaptive threshold, despeckle, try `--psm 6` and `--psm 4`
and keep the higher-scoring result.

### T2.3 — Per-word confidence — NOT STARTED

Tesseract TSV output, not plain text. New `ocr_recovered.csv` columns:
`release_id, pdf_page, word_no, word_verbatim, conf, bbox, source_tag`.

Sub-floor words are kept with their score, never deleted. **Entity extraction runs only on
words at or above the floor** — feeding low-confidence OCR into Layer 3 manufactures names
that were never on the page.

Rows for a page must be contiguous and sorted by `release_id, pdf_page`. The index builder
refuses to index a page whose rows are split, rather than indexing a fragment and calling
it the page.

Worst offenders — expect failure and log it rather than forcing output:
FBI-UAP-D027/D038/D039/D041/D042 (quality 0.0), FBI-Photo-B series (image-only),
DOW-UAP-D60/D63/D65 Mission Reports (0.0).

**Blocked here:** this container has no tesseract, no poppler, no opencv, and `apt-get`
cannot reach the archives. The pass needs a machine with the toolchain and the source PDFs,
which are still inside the Drive zips.

**Acceptance:** `ocr_recovered.csv` in word schema; a summary of pages recovered, pages
still failed, and mean confidence by release; `pages.jsonl` byte-identical to before.

### T2.5 — Page image beside the text — LIVE 2026-09-06, UPLOAD IN PROGRESS

Split the same way as T2.4: everything that does not need the PDFs is built and tested.

**Renderer.** `scripts/render_page_images.py`, PyMuPDF rather than `pdftoppm` — poppler is
not installable in the sandbox (apt archives 404) while PyMuPDF ships its own binaries
through pip, so this runs anywhere Python does. Writes `<out>/<release_id>/p0001.jpg`,
idempotent, and a PDF that will not open is reported rather than silently skipped.

**Measured, not estimated:** 150 dpi at JPEG quality 80 gives roughly **34 KB per page**, so
all 8,661 pages is about **295 MB** — not the "over a gigabyte" the spec assumed. Still far
too much for this repo, but it changes which hosting options are comfortable.

**Viewer.** The page view is now a two-column split at 900px and above: page image on the
left, sticky, transcript on the right; single column on a phone. The image URL is expanded
from `url_template` in `site/page_images.json` and **never guessed**. With no template the
panel says no host is configured and names the blocker. If the template resolves to a URL
that returns nothing, the panel says the image is missing from the host rather than
implying the page is blank — the same rule as everywhere else.

**Do not guess the Internet Archive URL form.** Upload an item, observe the real per-page
URL, paste it into `url_template`, and record the date in `verified_on`.

Preference order unchanged: Internet Archive item, then a separate assets repo served from
Pages, then a local directory for offline work. Page images are assets, not evidence:
nothing is written to `spine/`, and nothing is inlined into the payload.

**Live 2026-09-06.** 8,661 pages rendered from the 276 source PDFs and hosted on the
Internet Archive item `pursue-corpus-page-images`. `url_template` was set from an observed
URL, never guessed, and `verified_on` records the date a real image was confirmed to load.

Two defects had to be fixed before any image resolved:

* **The host keys images by the real filename, not the catalogued one.** `manifest.csv`
  records `source_file` with spaces, underscores and dots flattened to hyphens; the render
  folders — and therefore the IA keys — carry the filename from the source drop. They differ
  for 90 of 211 releases. `scripts/build_page_image_dirs.py` joins the two on a
  separator-insensitive key and writes the result to `site/page_images.json` under
  `folders`, which `pageImageUrl()` consults ahead of the manifest value. All 211 resolve
  with no ambiguity, and an ambiguous match would be reported and omitted rather than
  guessed. The mapping is hosting bookkeeping, so it lives in `site/` and `source_file` is
  left exactly as catalogued.
* **`build_investigator.py` read the spine CSVs without an encoding**, so on Windows they
  decoded as cp1252 and a U+2013 reached the built page as mojibake that could never match.

**Upload is not finished.** Roughly 2,000 of 8,661 images were still uploading on
2026-09-06; releases late in the alphabet report the image missing from the host until it
completes. Re-run `ia_upload_resume.py` — it skips everything already in `uploaded.txt`.

**Dead weight on the IA item, not yet cleaned:** 1,897 images carry a full Windows path as
their key (`C:/Users/bashs/...`) from an early run, about 0.51 GB, plus 4,434 IA version-
history files. A further 206 images sit in folders named `... (n).pdf` — duplicate
downloads of releases already mapped, which no page view will ever request. All are
unreachable rather than wrong, and deleting them is a separate decision.

**Still open:** the 211 source PDFs themselves have no `source_url` / `mirror_url` /
`working_url`. Page images are hosted; the documents they came from are not.

### T2.6 — Link every document to its sources — DONE for media 2026-08-09

`manifest.csv` and `media.csv` now carry `source_url`, `mirror_url`, `working_url`.
All 112 ingested media rows have a working link. All 211 documents have all three empty,
because the PDFs are still inside the zips and there is nothing to link to.

These columns are written by `scripts/build_media_links.py`, not by `ingest.py`. **An
ingest pass rewrites a release's rows and will drop them**, so re-run that script after
every ingest. `verify_spine.py` warns when the columns are missing and errors when they
disagree with `media_links.csv`.

---

## T3. Entity normalization

`entities.csv` has 11,090 mentions with known variant collapse needed:
- Rank titles: `Lt. Colonel` / `Lt. Col` / `Lt Col` / `LTC`
- `LaPaz` variants (the green-fireball thread runs through these)
- Truncated DocId stamps

Write `entities_normalized.csv` as a **new file with a `value_verbatim` column
preserved alongside `value_normalized`.** Never overwrite the verbatim value. The
normalized column is a retrieval convenience; the verbatim column is the evidence.

**Acceptance:** new file, both columns present, original `entities.csv` untouched, plus
a collapse report showing every merge decision made.

---

## T4. Kinematic pass — start with DOD_111764189

The butte orb clip. 54 s, 30 fps, fixed camera, dusk. It is the direct moving-imagery
counterpart to the USPER "Large Fiery Orb" slide in the paper corpus, which makes it
the highest-value target in the media set.

Pipeline: stabilize (fixed camera, so verify drift first), threshold/blob-detect the
bright object, track centroid per frame, output `tracks.csv` with columns
`release_id, frame, t_seconds, cx_px, cy_px, area_px, mean_intensity, bbox`.

Hard rule: **pixel coordinates only.** Do not convert to altitude, distance, or speed.
Those conversions require camera intrinsics, focal length, and range that we do not
have. Anyone who publishes derived speeds from uncalibrated footage is fabricating,
and it is the fastest way to discredit the entire corpus.

Companion clip: `DOD_111764213` (same terrain, 21 s).

Then generalize the same script across all 112 videos in batch.

**Acceptance:** `tracks.csv` for 189 and 213; a plotted centroid trajectory saved as
PNG; the script runs unattended on a directory of videos.

---

## T5. Layer 4 assertion ledger — pilot on the Western US Event cluster

The densest cross-format cluster in the corpus, and now the only one with moving
imagery:

- D077 case analysis, D078 notional map, D079–D083 five witness narratives
- USPER helicopter log, marked SECRET//NOFORN
- 10 FBI digital renderings, 3 Serial FD-302 interviews, 8 FBI-Photo-A FLIR frames
- Videos DOD_111764189 and DOD_111764213

Extract every assertion with speaker, verbatim quote, page cite, and statement type.
The distance contradiction (500–600 m witness vs ~1,050 m AARO) gets two rows, both
cited, no resolution.

**Acceptance:** `assertions.csv` populated for the cluster; contradictions present as
paired rows; spot-check 10 rows against the actual PDF pages and report any mismatch.

---

## T6. Enclosure verification

251 `ENCLOSURE_REFERENCED` gap rows. Check each referenced enclosure against the
corpus. Three outcomes only: `PRESENT` (with the release_id it resolves to),
`NOT_IN_CORPUS`, `AMBIGUOUS_REFERENCE`.

`NOT_IN_CORPUS` means exactly that. It does not mean withheld.

**Acceptance:** `enclosures.csv` with those three states and a count of each.

---

## T7. Visual pass on still imagery

30 standalone images plus ~35 image-only PDF pages (FBI-Photo-B series, zero-text
FBI-UAP items). Describe what is visible, extract any burned-in text via OCR, log
redaction blocks. Same description discipline as video.

**Acceptance:** `image_observations.csv`, one row per image, every row cited.

---

## T8. Rebuild and deploy the public site

`index.html` at the repo root is the working single-file site with the corpus
data embedded; GitHub Pages serves it directly. Regenerate it from current CSVs
via `scripts/build_site.py` (sole output; `site/` holds only `template.html`).

Deployment plan:
1. **Internet Archive** for videos and source PDFs. Free, permanent, built for exactly
   this material, gives streaming embeds and kills the bandwidth cost that would
   otherwise make self-hosting 10+ GB expensive.
2. **GitHub Pages or Cloudflare Pages** for the static site. Free tier, no server, no
   database, nothing to maintain or get breached.
3. **Pagefind** for client-side full-text search across all 8,661 pages — after T2, so
   the index contains recovered text.
4. Media pages grouped by the five families, each showing Layer 0 facts and the triage
   strip.
5. Cluster pages, Western US Event first, with contradictions displayed as
   contradictions rather than resolved.
6. Links on the public site come from `source_url` and `mirror_url` only. The `working_*`
   columns in `media_links.csv` point at one private Drive account and must not be
   rendered into the public build. They are for the investigator tool.

**Acceptance:** site builds from a single command; every displayed value traces to a
CSV row; no derived or inferred values on any page; no `working_*` URL in the output.

---

## T9. Investigator tool — built 2026-08-08, `investigate.html`

The private counterpart to the public reader. Built by `scripts/build_investigator.py`
from `site/investigator.html`. 1.5 MB, phone-first, no external requests except the Drive
player iframe.

What it does: browse 211 documents with gap counts, read any of the 8,661 pages with the
text source labeled (`TEXT_LAYER` and `OCR_RECOVERED` shown as separate blocks, never
merged), 133 media files grouped by family with the triage strip and a one-tap Drive open,
6,155 entity groups where a cite jumps straight to the page with the verbatim spelling
highlighted, and stars plus notes on any document, page, media file or entity.

Page text is not embedded — 27 MB would kill it on a phone. The build emits a byte-offset
index into `spine/pages.jsonl` and the app fetches one page per Range request, validating
that the returned record is the release and page it asked for. If the host ignores Range
it downloads once, says so, and slices locally.

### Mark keys name the thing, never its position

A mark key identifies what it marks:

```
doc:<release_id>          med:<release_id>
page:<release_id>:<n>     ent:<ENTITY_TYPE>:<value_normalized>
```

The first version keyed entities as `ent:<array index>`. Entity order is by mention count,
so T2 alone would have reshuffled it and every entity star would have silently re-pointed at
a different entity while still displaying its old label. Silent wrong is worse than broken.

A key that no longer resolves is displayed as unresolved and is never rebound to whatever
now occupies that slot. Export format:

```json
{"schema":"pursue.marks/2","exported_utc":"…",
 "corpus_build":{"commit":"92de5a3","dirty":false,"built":"2026-08-08"},
 "marks":{…}}
```

`corpus_build.commit` is HEAD at build time, so a tool built before its own commit lands
points at the parent; `dirty` flags an uncommitted tree. Import reads both the current
schema and the old bare-map format, rekeys positional entity marks through the current
ordering, and says out loud that it assumed the file came from this build — a v1 file has
no stamp, so that assumption cannot be checked. Import also compares `corpus_build.commit`
against the running build and warns when they differ. Existing marks in localStorage
migrate on first load; the v1 copy is left in place rather than deleted.

Still open on it:
- Notes are localStorage, so per-device. Export from the Marks tab is the only backup.
- `value_normalized` is a derived convenience, so changing `aliases.yml` or the
  normalization rules will change entity keys. That surfaces as an unresolved mark, which
  is the correct failure — visible, not silent — but it is a real migration cost to weigh
  before rewriting normalization rules.
- Documents have no open-in-one-tap because they are still inside the zips (T1c). When
  `doc_links.csv` exists, wire it into the document card the same way media is wired.
- No full-text search across pages. Entity search covers most of it; a real one wants
  Pagefind or a prebuilt inverted index, and should wait until after T2 so recovered text
  is in the index.

**Note before merging:** GitHub Pages serves whatever is on the default branch, so merging
puts `investigate.html` at a public URL. Nothing in it is secret — the notes are local to
the browser and never leave the device, and the Drive folder is already shared
`anyone: reader` — but it is a public URL with no auth, so treat it as discoverable.

---

## T10. Layer 5 co-presence in the front end — DESIGN RECORDED, NOT BUILT

**Spec received 2026-08-09 and transcribed to `docs/T10_copresence.md`** — eleven acceptance
criteria and the payload contract. That file governs; the summary below is orientation only.
The `relations.html` fixture is a synthetic demonstration, is not in this repo, and can be
rebuilt from the spec.

### Why it belongs in the front end

`CLAUDE.md` says Layer 5 is derived at query time and never written to disk. That rules it
out as a pipeline task by construction: anything the pipeline produced would be a stored
edge. So it has to be computed in the reader, per query, and thrown away. The design as
described complies — nothing new is persisted.

### The coverage comb

Every result sits on a strip where one tick is one page in scope. Scope is **every page of
every document the subject appears in**, unread pages included, because that is the set
where a co-mention could have existed.

Three states, and amber means exactly one thing — *you could not read this page*. No other
element on the page may use that colour.

| Tick | Meaning | Count today |
|---|---|---|
| solid | shipped text layer | 6,124 |
| hollow | below the OCR floor | 818 |
| amber | no text layer | 1,719 |

**The data already exists and is cheap.** Derivable per page from `pages.jsonl`
(`no_text_layer`) plus the `LOW_OCR_QUALITY` rows in `gaps.csv`. Encoded as one run-string
per release it costs **17.8 KB** across all 211 releases — small enough to embed in the
payload rather than fetch. It is not in the payload today; only per-document gap totals are.
That is the one build change the feature needs.

### Three outcomes on a pair test, never two

1. **Co-present** — with cites.
2. **Not observed** — with the blind-spot count attached.
3. **String missing from the index** — the term never appears at all.

Today a zero result and a true absence render identically. These are different claims and
must read differently. Same T9 semantics as marks migration: zero matches and one match are
different messages.

### Vocabulary rule

No copy in the panel may say *related*, *linked*, or *network*. The claim is co-presence on
a cited page, which is the only thing verbatim data supports.

### The tension, and a way to settle it

The purist objection is fair: showing co-occurrence at all invites the reader to infer
connection, which is what this corpus exists to avoid. The counter is that the inference
happens anyway, unmeasured, and rendering it with a denominator is more honest than leaving
it to the reader's head.

Both are true, so make it structural rather than a matter of taste: **a zero result must be
unable to render without its denominator.** The failure mode is not the feature, it is the
comb being dropped for space on a narrow screen — that is the moment it silently becomes
the thing the purist feared. So the comb is non-optional, it is not responsive-hidden, and
there is an acceptance test that a "not observed" panel with no comb cannot be produced.

### Open question — the owner's call

**Do media segments enter the index, or stay out until segment confidence is scored?**

Recommendation, not a decision: keep them out for now. Media can carry a cite (timestamp,
per rule 3) but there is no segment confidence score yet, so media rows would enter with no
denominator while document pages have one. A result mixing the two would have a coverage
strip that is only partly meaningful, which is worse than a narrower scope. Show a separate
count of media segments not searched, so their absence is visible rather than silent — the
same principle as the comb itself.

---

## T12. Media pass — ASR and frame sampling (decisions recorded 2026-08-09)

**Spec received 2026-08-09 and transcribed to `docs/T12_correspondence.md`** — nine
acceptance criteria, the tier rules, the sampling policy, the queue schema and the
correspondence record. That file governs; the notes below are the decisions with agreement
or objection against each.

### 1. ASR is a search index, never a correspondence key — AGREED

OCR failure announces itself: `SSlflED` is visibly broken. ASR failure is fluent — it
returns plausible words that read as correct and cannot be caught without listening. In a
verbatim corpus every row must be checkable against its source, and an ASR row cannot be
checked without replaying audio.

Worth stating explicitly, because it is not the same rule as the OCR floor: for OCR a
confidence threshold works because the score tracks visible brokenness. For ASR it does
not, so the answer is not a higher floor — it is a different tier. ASR corroborates. It
never carries a row.

### 2. Expected yield written down before the run — AGREED, with one strengthening

Pre-registration only works if the timestamp is verifiable. **Commit the prediction before
the run starts**, so "we predicted that" is falsifiable rather than asserted afterwards.

**Predict by `release_id`, not by percentage.** Checked against `media.csv`: the longest 11
clips are 5.35 h of 8.38 h (64%), but the longest 5 alone are 4.81 h (57%) and the next six
are 5–8 minute clips. A bare "60%" is satisfied by several different clip sets, and T1b
changes the denominator anyway. Name the ids.

Note also that `media.csv` has no column recording which clips are seismograph renders —
that is an observation in `CLAUDE.md`, not a queryable fact. If the prediction depends on
it, the classification should be recorded per clip first.

### 3. Candidates live in `review/`, not `spine/` — AGREED, with an addition

Keeps `verify_spine.py` hash-identical and keeps machine inference out of the tier people
cite. The sharper framing than licence tiers: `spine/` is what gets cited, `review/` is what
has not earned a cite yet. Same shape as `aliases.yml` — nothing promotes without the owner.

**Addition:** `verify_spine.py` should assert that no spine row ever references a `review/`
file, the same way it already refuses to let Layer 5 be persisted. Otherwise the boundary is
a convention rather than a gate, and conventions erode.

### 4. The week is bandwidth, not compute — AGREED on shape, but the number is 4x too high

Measured against `media.csv`, which carries real `file_bytes` per clip (spot-checked against
Drive's reported `fileSize` — exact match):

| | |
|---|---|
| 112 ingested clips, measured | **7.46 GB** |
| implied mean bitrate | **2.0 Mbit/s**, not the 9000k the filenames advertise |
| 21 not yet ingested | size unknown |
| extrapolated total at the same mean | **~8.9 GB** |

The ~34 GB figure comes from 9 Mbit/s x 8.38 h. Only part of the set carries the `-9000k`
label and the measured sizes do not bear it out. This is closer to a long night than a week,
which changes the plan.

**A real gap this exposes:** `drive_listing_2026-08-08.tsv` records id, title and parent but
**not `fileSize`**, so resume-and-verify has no expected size to check against for the 21
un-ingested clips. Capture `fileSize` on the next Drive listing — without it, a truncated
download is indistinguishable from a complete one.

Resume logic remains the thing that decides whether the run finishes: verify by size and
hash after each file, never by existence alone.

### Ordering note from the spec

T12 is **independent of T11**. Burned-text OCR generates its own per-word confidence from
scratch, so extraction does not inherit the two-floor contradiction — only display and
thresholding wait on T11. Extract now, gate later.

### Open question — does ASR confidence unblock T10 criterion 11?

**Recommendation: no, and for a stronger reason than model certainty.**

The owner's argument is right — confidence measures the model's certainty, not its accuracy,
and under fluent failure confident-and-wrong is the normal case. But the structural reason is
sharper: T10's comb needs a *readability* measure comparable across the whole scope. For a
page, "no text layer" is an observable fact about the artifact. Audio has no equivalent —
**a segment where nobody spoke and a segment the model could not hear are indistinguishable
from confidence alone.** Media would enter with a denominator unable to separate "nothing was
said" from "we could not hear it", which is exactly the distinction the comb exists to draw.

So confidence is not merely the wrong number; the comb's semantics have no media analogue
yet. What *would* unblock criterion 11 is a per-segment **audibility** measure — speech
present or absent, measured from the signal rather than from the transcriber — which is a
different thing to build and should be named as such rather than assumed to arrive with ASR.

Decide this before the data exists, per the owner's own point: once confidence scores are
sitting in a file they will argue for their own admission.

---

## T11. Launch-readiness queue (owner's ordering, 2026-08-09)

Ordered by cheapest-and-most-irreversible-if-skipped, not by size.

1. **LICENSE + CITATION.cff — DONE 2026-08-09.** 54 copies were already out with no terms
   attached, and copies that exist cannot be retroactively licensed. Three-way split:
   released documents are US government work in the public domain, the spine is CC BY 4.0,
   the code is MIT. BY over CC0 because the stated goal is to be cited rather than silently
   absorbed. See `LICENSE`, `LICENSE-DATA`, `CITATION.cff` and the README section.
2. **Audit `.github/workflows/` — DONE 2026-08-09, nothing found.** There is no `.github/`
   directory in the repo. No workflow files exist anywhere, and `schedule:` appears in no
   YAML — the only YAML is `spine/aliases.yml`. The runs visible in the Actions tab are
   GitHub's built-in `dynamic/pages/pages-build-deployment`, which is push-triggered, at
   roughly one per push. **Scheduled CI cannot account for the clone count.** Traffic
   conclusions drawn from it are not self-inflicted.
3. **Cloudflare beacon.** No site measurement exists at all today, and the launch window is
   the one period that cannot be reconstructed later.
4. **Resolve the two-floor contradiction — NOT STARTED, and it blocks T10.** The gap flags
   threshold at 0.90 (a page-level OCR quality score, 0–1) while the published display floor
   is 60 (a tesseract per-word confidence, 0–100). These are different scales measuring
   different things, so "below the floor" currently has two meanings. T10's comb renders its
   hollow ticks off one of them. Pick one, document which and why, and make
   `verify_spine.py` assert it. Until then the comb would make a coverage claim the data
   does not support — the exact failure the project exists to avoid, and the reason this
   must land **before** T10 is built, not after.
5. **Prebuilt summary JSON for first paint.** 32 MB loads before anything renders. Biggest
   conversion lever available and it touches nothing in the spine.
6. **Tell someone.** No human has seen it; the traffic is automated indexing. Candidates:
   r/UFOs, r/UAP, the Black Vault community, the FOIA/MuckRock crowd, Hacker News — where
   the angle is the coverage-comb epistemics, not the subject matter. One post, one honest
   description of what is indexed and what is not.
7. **Internet Archive upload.** Solves the zipped-PDF blocker, the war.gov removal risk, and
   supplies an independent download counter GitHub cannot give.

---

## Commercial notes (standing instruction: surface these unprompted)

- The site stays free. The material is public domain and the project's credibility
  depends on it not being monetized.
- The **pipeline** is the sellable asset. Ingest to spine to searchable static site is
  repeatable for any large FOIA or declassification dump. Buyers who receive document
  dumps and have no way to navigate them: newsrooms, law firms in discovery, academic
  archives, advocacy orgs.
- The corpus is also a portfolio artifact with his name on it, which matters for the
  ops and technical roles he is currently applying for. A live URL demonstrating a
  211-document, 8-hour-media pipeline is stronger evidence than any bullet on a resume.
- Internet Archive hosting keeps marginal cost near zero, which is what makes the free
  public version sustainable indefinitely rather than until a bandwidth bill arrives.
- **The coverage comb is separable IP and worth documenting away from PURSUE.** Every
  research tool over scanned government records has the same silent failure: search 8,661
  pages where 2,537 are not machine-readable, report no hits, and the reader cannot tell a
  real absence from an unread page. A convention that puts the unreadable fraction on every
  result is small to build and, as far as we know, absent from FOIA readers, court
  e-discovery viewers and archive front ends. Write it up as a standalone UI pattern with
  the PURSUE corpus as the worked example, not as a PURSUE feature.
- Drive is not a hosting plan and should not be treated as one. Public link-sharing on a
  consumer account carries an undocumented daily download cap; a file that gets attention
  starts returning a quota page instead of the video, and the failure looks like the
  corpus is broken rather than like Google rate-limiting. This is the operational argument
  for the Internet Archive upload, separate from the removal argument. Until that upload
  exists, the media set has a single point of failure that is one account's quota.
