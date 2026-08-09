# T12 — Cross-modal correspondence (burned-in text, ASR, and the join)

Source: `T12_correspondence.pdf`, received 2026-08-09. Transcribed below.

Goal: show what the corpus actually holds across paper, video and audio, by finding the same
verbatim string in two places and citing both. Runs as a slow background job over roughly a
week.

**Not a stitcher.** It does not decide that a video is about a document. It records that a
string appears in both, and leaves the conclusion to a human.

## The rule that makes this legal under CLAUDE.md

`CLAUDE.md` says Layer 5 relations are derived at query time and never stored. A
correspondence table would be stored relations — unless the row is an observation rather
than a judgement. So:

> A correspondence is recordable only if it is a verbatim string appearing in two locations,
> each with its own independent cite and its own confidence.

*This string is burned into frame 00:04:12 of `DOD_111688421`, and the same string appears on
`DOW-UAP-D092` p50* is transcription with two citations. *This video concerns that memo* is a
judgement and does not go in a file.

Nothing under `spine/` changes. Candidates live in `review/`.

## Join key tiers

**Tier A — recordable as a correspondence key.** Burned-in text, read off the pixels by OCR.
Deterministic, and any reader can verify it by looking at the named frame. Sources: v2605
title cards (50 edited presentation products, B/W inverted), ISR metadata bars on the
111688/689 family (date, time, sensor, mission strings), slates, stamps, and any on-screen
document.

**Tier B — search only, never a key.** ASR. OCR failure is visible — `SSlflED` announces
itself. ASR failure is fluent: it returns plausible words that read as correct and cannot be
spotted without the audio. In a verbatim-only corpus that asymmetry is disqualifying. ASR
output is a search index and a corroboration column. It is never quoted as testimony and
never forms a correspondence on its own.

**Tier C — metadata.** Encode dates, filenames, DocId stamps, durations. Weak alone, useful
as corroboration.

## Expected yield, written before the run

Recorded in advance so a thin result reads as a measurement rather than a pipeline failure.

| Family | Share of duration | Expected Tier A yield |
|---|---|---|
| NASA seismograph animations (11 clips) | ~60% (5 of 8.38 h) | Near zero. Axis labels and timestamps at most. |
| v2605 edited products (50 clips) | small | Highest. Title cards are the point. |
| 111688/689 ISR | moderate | High if a metadata bar is present, zero if it was cropped before release. |
| 111764 / 111830 | moderate | Unknown. Measure and record. |

A family yielding zero is written into the results as a measured zero, not omitted from the
table.

## Sampling policy

Do not sample at 1 fps — that is ~30,000 frames of mostly nothing.

- **Opening burst:** first 20 s of every clip at 2 fps. Title cards live here. 133 clips →
  ~5,320 frames.
- **Persistent bar:** 1 frame per 10 s across the full duration. 30,168 s → ~3,017 frames.
- **Scene change:** `ffmpeg select='gt(scene,0.4)'`, capped at 200 frames per clip, to catch
  mid-clip slates.

Roughly 8,300 frames plus scene changes — a few CPU-hours of tesseract, not a week.

**Redaction adjacency.** ISR frames carry heavy per-frame redactions. Detect and mask
redacted regions before OCR, exactly as T2.1 does for pages. A masked region yields no text.
Record the count of frames where a redaction sat adjacent to extracted text, because that is
where a partial string is most likely.

## What actually takes a week

Not compute — bandwidth. At the 9000 kbps seen in `DOD_111764796-1920x1080-9000k`, 8.38 h is
on the order of 34 GB, before the 21 unmeasured files. `gdown` on large files is slow and
fails partway. Resume logic and a size check are the difference between a week that finishes
and a week that silently redownloads.

*(See the verification section below — measured bytes put this at ~7.5 GB, not ~34 GB.)*

## Queue and worker

An agent here is a queue, an idempotent worker, and cron. No LLM in the frame loop.

`work/jobs.jsonl` — one record per job:

```json
{"job_id":"...","kind":"FETCH|SAMPLE|OCR_FRAMES|ASR|JOIN|INDEX",
 "target":"<media_id or doc_id>","state":"PENDING|RUNNING|DONE|FAILED",
 "attempts":0,"started_at":null,"finished_at":null,
 "error":null,"output_hash":null}
```

- Worker: `scripts/t12_worker.py --budget 3`. Takes up to N pending jobs, does them, exits.
  Wrapped in `flock` so overlapping cron ticks cannot double-run.
- Cron every 20 minutes with a budget of 2–3 trickles the whole set across a week without
  ever holding a long-running process.
- Idempotent: a job whose output exists with a matching hash is skipped. A job killed mid-run
  leaves the queue consistent and re-does at most one job.
- `work/jobs.jsonl` is committed so the queue survives a clone — that is the handoff.
- Frames, video and audio are gitignored. **Never commit media.**
- Frames are not retained as files in the repo. Store the extracted string plus
  `media_id` + timestamp, from which the frame is regenerable deterministically.

## Correspondence record

`review/correspondences.csv` — outside `spine/`, all rows start `CANDIDATE`:

```
corr_id, key_type, key_norm, verbatim_a, cite_a, conf_a,
verbatim_b, cite_b, conf_b, method, corroboration, state
```

- `key_type`: `DATE | TIME | DOCID | CASE_NO | LOCATION | STAMP | TITLE`
- `cite_a` / `cite_b`: `media_id@HH:MM:SS` or `release_id p<n>`. **Both required.**
- `corroboration`: free field where Tier B and Tier C evidence may be named. It never
  promotes a row on its own.
- `state`: `CANDIDATE | PROMOTED | REJECTED`, reviewed the way `aliases.yml` is.

## Acceptance criteria

1. `verify_spine.py` hash-identical before and after every run. Nothing under `spine/` is
   written by T12.
2. Every row carries two cites with two independent confidences. A row with one cite is
   invalid and fails the build.
3. No ASR string ever appears in `verbatim_a` or `verbatim_b`. ASR is confined to
   `corroboration`.
4. No media file, frame or audio track is committed. `.gitignore` enforces it and a
   pre-commit size check backs it up.
5. The expected-yield table is written before the first run and the actual yield is recorded
   against it, including zeros.
6. The worker is resumable and budget-bound. A run exceeding its budget fails loudly rather
   than continuing.
7. Partial downloads are detected by size and resumed or discarded, never treated as
   complete.
8. Nothing renders in the investigator until `PROMOTED`, and the count of unreviewed
   candidates is displayed — the same rule as media segments not searched.
9. Redaction masking runs before OCR on every frame, and frames with adjacent redaction are
   counted.

## Ordering

Independent of T11. Burned-text OCR generates its own per-word confidence from scratch, so
extraction does not inherit the two-floor contradiction. Only the display and thresholding of
results waits on T11 — extract now, gate later.

## Open question for the owner

The ASR pass produces per-segment confidence, which is exactly the number criterion 11 was
waiting on to let media into Layer 5. Whether that should unblock it is not obvious: ASR
confidence measures the model's certainty, not its accuracy, and the fluent-failure problem
means a confident wrong transcript is the normal case rather than the edge.

Recommend media stay out of Layer 5 even after scoring, or enter with a visually distinct
tick state that does not read as equivalent to a page.

---

# Verification against the corpus (added 2026-08-09, not part of the spec)

## The bandwidth figure is about 4x too high

`media.csv` carries measured `file_bytes` per clip, spot-checked as an exact match against
the `fileSize` Drive reports:

| | |
|---|---|
| 112 ingested clips, measured | **7.46 GB** |
| implied mean bitrate | **2.0 Mbit/s** |
| 21 un-ingested, extrapolated at the same mean | +1.4 GB |
| **total** | **~8.9 GB** |

The 34 GB comes from applying the `-9000k` filename label across the full 8.38 h. Only part
of the set carries that label and the measured bytes do not bear it out. Bandwidth still
dominates compute, so the shape of the call holds — but this is a long night, not a week.

**Gap this exposes:** `spine/drive_listing_2026-08-08.tsv` records id, title and parent but
**not `fileSize`**. Criterion 7 requires detecting partial downloads by size, and there is no
expected size on record for the 21 clips with no `media.csv` row. Capture `fileSize` on the
next Drive listing, or criterion 7 cannot be met for those files.

## Sampling arithmetic checks out, with one caveat

133 clips x 20 s x 2 fps = 5,320 ✓.  8.38 h = 30,168 s, at 1 per 10 s = 3,017 ✓.
Total ~8,337 ✓.

Caveat: the opening burst counts **133** clips while the persistent-bar figure is derived
from the **112** measured durations. The 21 un-ingested clips have no duration on record, so
the persistent-bar count will grow once T1b runs. It is a floor, not a total.

## The seismograph share is defensible; the composition is not yet queryable

Longest 11 clips = 5.35 h of 8.38 h (64%). Longest 5 alone = 4.81 h (57%). So "5 of 8.38 h,
~60%" is well supported as a duration share.

But `media.csv` has **no column recording which clips are seismograph renders** — that is an
observation in `CLAUDE.md`, not a queryable fact. Criterion 5 requires actual yield recorded
against the predicted table by family; that join does not currently exist. **Record the
family classification per clip before the run**, or the yield table cannot be filled in
afterwards without redoing the identification by eye.

## Criterion 4 partially enforced as of 2026-08-09

`.gitignore` previously covered `*.mp4` and `*.zip` only. Extended to `.mov`, `.mkv`, `.avi`,
`.webm`, `.m4v`, `.wav`, `.mp3`, `.m4a`, `.flac`, plus the `frames/`, `page_images/`,
`work/media/` and `work/tmp/` output directories.

Deliberately **not** a blanket `*.jpg`: the 112 video contact sheets under `spine/` are
tracked evidence and must stay tracked. Confirmed still tracked after the change.

The pre-commit size check the criterion also asks for is not built.
