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

## T1. Confirm the three remaining Drive zips are not duplicates — BEFORE downloading

The loose video uploads may already contain everything in the three pending zips
(~3 GB, ~4.5 GB, ~5.6 GB). Downloading 13 GB of duplicates wastes a night.

List each zip's contents without extracting, diff filenames against `media.csv`, and
report the overlap. Only pull a zip that contains genuinely new files.

**Acceptance:** a written diff per zip: N files, M already in media.csv, K new.

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

`site/pursue_corpus_reader.html` is a working single-file prototype with the corpus
data embedded. Regenerate it from current CSVs via `scripts/build_site.py`.

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

**Acceptance:** site builds from a single command; every displayed value traces to a
CSV row; no derived or inferred values on any page.

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
