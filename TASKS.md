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
against `media.csv`. 133 videos in Drive, all 112 `media.csv` rows resolve to a live Drive
file, 21 videos are in Drive with no spine row. See T1b.

---

## T1b. Ingest the 21 videos that are in Drive but not in the spine

Listed in `media_links.csv` as `spine_status = NOT_INGESTED`. They are not a new release
family — every one belongs to a family already in the corpus:

| Family | Count |
|---|---|
| `DOD_111688*` / `DOD_111689*` (ISR) | 12 |
| `video_2605_DOD_*` (edited presentation products) | 7 |
| `DOD_111764796-1920x1080-9000k` | 1 |
| `DOD_111887384` | 1 |

Two of them (`DOD_111764796-1920x1080-9000k`, `DOD_111887384`) sit in the Drive root rather
than in the release folder. That is a filing fact about Drive, not a fact about the release.

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

## T2. Bulk OCR pass — biggest outstanding job

2,537 pages need it: 1,719 with no text layer, 818 with low quality.

Rules:
- Write to `ocr_recovered.csv`, never into `pages.jsonl` text fields. The two sources
  stay separable forever.
- Tag every recovered page `OCR_RECOVERED`.
- Set a quality floor. Pages below it are logged as still-failed and are **not** fed to
  entity extraction. Polluting Layer 3 with OCR garbage is worse than having no text.
- Worst offenders, expect failure and log it rather than forcing output:
  FBI-UAP-D027/D038/D039/D041/D042 (quality 0.0), FBI-Photo-B series (image-only),
  DOW-UAP-D60/D63/D65 Mission Reports (0.0).

Run it overnight. It is multi-hour and it is why we moved to Code.

**Acceptance:** `ocr_recovered.csv` populated; a summary table of pages recovered,
pages still failed, and mean quality by release; `pages.jsonl` byte-identical to before.

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
- Drive is not a hosting plan and should not be treated as one. Public link-sharing on a
  consumer account carries an undocumented daily download cap; a file that gets attention
  starts returning a quota page instead of the video, and the failure looks like the
  corpus is broken rather than like Google rate-limiting. This is the operational argument
  for the Internet Archive upload, separate from the removal argument. Until that upload
  exists, the media set has a single point of failure that is one account's quota.
