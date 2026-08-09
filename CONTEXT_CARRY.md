# PURSUE corpus — carry-over brief

Written 2026-08-09. Supersedes `spine/CONTEXT_BRIEF.md` for session handoff.
Read `CLAUDE.md` first — the evidence rules there are binding and are not style.

**Resuming cold: clone the repo. That is the whole handoff.** Everything in `spine/`
is committed, including `pages.jsonl`. A `spine_snapshot.zip` is not needed and, once it
exists alongside the repo, becomes a second copy that can silently disagree with it.

## Project

Structured index of the DoW / PURSUE UAP declassified release.
Repo `github.com/jdsebastian85/pursue-corpus`, `main`, deployed via GitHub Pages.

- Public reader — https://jdsebastian85.github.io/pursue-corpus/
- Investigator tool — https://jdsebastian85.github.io/pursue-corpus/investigate.html

The two front ends are deliberately different. `index.html` is the credibility artifact for
a skeptical stranger and carries no Drive link. `investigate.html` is the owner's working
tool and leads with them. Both read the same spine; neither writes to it.

## Corpus state

211 documents / 8,661 pages / 112 rows in `media.csv` / 8.38 h / 580 segments /
11,090 entity mentions in 6,155 groups. Gaps: 1,719 NO_TEXT_LAYER, 818 LOW_OCR_QUALITY,
251 ENCLOSURE_REFERENCED, 127 REDACTION_MARKER, 12 DOCID_STAMP_TRUNCATED,
1 DOCID_STAMP_ANOMALOUS.

`verify_spine.py` is the gate. Run it after every task; it exits nonzero on error.

## Done

- Spine layers 0–3, `verify_spine.py`, snapshot workflow
- T3 normalization (806 rewrites, `entities.csv` hash-unchanged)
- T3b candidate flags (404 flagged mentions / 300 groups), rank consistency, DocId gap
  scoped (68 stamps, 12 TRUNCATED, 1 ANOMALOUS), `aliases.yml` (10 clusters, 39 members,
  all unreviewed), site entity index with disclosed filtering
- Investigator tool: byte-range page fetch, inline video, cite jumping, marks with
  export/import keyed by type + normalized value and stamped with `corpus_build`
- T2.4 display layer: `[REDACTED]` as a drawn block, sub-floor words dimmed, per-page
  source and mean confidence, **published confidence floor = 60**
- T2.6 for media: `source_url` / `mirror_url` / `working_url` on `manifest.csv` and
  `media.csv`. 112 media rows have a working link; all 211 documents have three empty
  cells because the PDFs are still zipped.
- `ingest.py` preserves columns it does not own across a re-ingest (2026-08-09)

## Open, in order

1. **T1b ingest** — 21 corpus videos with no `media.csv` row: 19 in the shared folder
   (12 `DOD_11168*`/`11169*`, 7 `video_2605_*`) plus 2 in the Drive account root
   (`DOD_111764796-1920x1080-9000k`, `DOD_111887384`). Re-run
   `scripts/build_media_links.py` afterwards.
2. **Internet Archive account** — the single decision that unblocks both document access
   and the war.gov removal risk. Until it exists, `mirror_url` is empty everywhere and
   nothing in the corpus has a citable permanent link.
3. **T2.1–T2.3 OCR pass** — 2,537 pages. Blocked on toolchain and sources: needs a machine
   with tesseract, poppler and opencv *and* the source PDFs on disk. Redaction-detect →
   mask → OCR → per-word confidence into `ocr_recovered.csv`. Entity extraction only at or
   above the floor. `pages.jsonl` stays byte-identical. No display work is waiting behind
   it — the tool already reads the word schema.
4. **Document access** — the 211 PDFs are inside `Release_1.zip`,
   `release_03_documents.zip` and `Archive.zip` in the Drive folder. Not linkable while
   zipped. Extracting into a Drive folder works; the Archive upload is permanent.
5. **T9 marks migration** — a stored verbatim set matching more than one current group must
   report ambiguous with both candidates, not auto-resolve. Zero matches and one match are
   different messages.
6. **Aliases review** — promote or reject the commented candidates. Stever is a distinct
   person (H. Guyford Stever); reject that candidate and record why.
7. **Fifth release (2026-08-07)** downloaded but not reconciled against the manifest. Do
   not describe the index as complete until it is.
8. **T10 Layer 5 co-presence** — spec in `docs/T10_copresence.md`, eleven acceptance
   criteria, not built. Payload verified against the corpus: build gate lands exactly on
   6,124 R / 818 L / 1,719 N = 8,661; `read` run-strings 17.1 KB, `mentions` map 213.5 KB,
   so the payload goes from 1.48 MB to about 1.71 MB and stays one file. Media segments are
   decided — held out, with a visible count of segments not searched. The `relations.html`
   fixture is a demonstration only and is not in the repo.

## Two corrections to the 2026-08-08 brief

- It lists a **reading room** page built by `build_reading_room.py`. Neither the script nor
  the page exists in this repo — `scripts/` holds `assess_docid_stamps`, `build_investigator`,
  `build_media_links`, `build_site`, `fetch_sources`, `normalize_entities`, `search_entities`,
  `track_object`, `verify_spine`. Treat the reading room as not started.
- ~~Span disagreement~~ **resolved 2026-08-09 against `manifest.csv`: 1944–2026 is correct**
  and `CLAUDE.md`/`README.md` have been corrected. The 1944 is a single real document,
  `331-120752-Numeric-Files-1944–1945-...-German-Armament-Equipment-Documents.pdf`; 1946
  was the second-earliest. Two caveats now recorded in `CLAUDE.md`: only 117 of 211
  documents carry a year token at all, and the earliest date *mentioned in the text* is
  1848, which is a different measurement and must not be quoted as the span.

## Environment facts

Chat sandbox: roughly 7 GB usable disk, per-command timeouts, resets between sessions. No
tesseract, poppler or opencv, and `apt-get` 404s on the Ubuntu archives. Remote Code
sessions additionally block `drive.google.com` and `*.github.io` at the network proxy, so
Drive listings must go through the Drive connector and a Pages deploy can only be confirmed
via the Actions API, not by fetching the URL.

Drive pulls via `gdown "https://drive.google.com/uc?id=FILE_ID" -O out`; folder listing via
`gdown.download_folder(url=..., skip_download=True)`. Process substitution `<(...)` fails
under `/bin/sh`.

## Working split

Claude Code on a real machine: pipeline, OCR, batch tracking, site builds. Chat: judging
what imagery shows, what counts as a contradiction, design and copy calls.

## Commercial standing instruction

Flag revenue, licensing, grant or career implications unprompted. The site stays free; the
**pipeline** is the sellable asset. Drive is not a hosting plan — public link-sharing on a
consumer account has an undocumented daily download cap, and a file that gets attention
starts serving a quota page instead of the video.
