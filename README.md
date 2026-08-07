# PURSUE UAP Release Corpus

Structured analysis of a Department of War / PURSUE initiative UAP declassified
document and media release. 211 documents, 8,661 pages, 112 videos, 8.38 hours,
spanning 1946 to 2026.

The spine records what the documents say and where they say it. It does not evaluate,
rank, or conclude. Read `CLAUDE.md` before working on this — the evidence rules are
not stylistic preferences, they are what makes the corpus usable by anyone else.

## First run

```bash
git clone <your-repo> uap-corpus && cd uap-corpus
unzip spine_snapshot.zip -d spine/

sudo apt install -y tesseract-ocr poppler-utils ffmpeg
pip install pdfplumber pypdf opencv-python-headless numpy pillow pytesseract gdown

python3 scripts/verify_spine.py     # expect: 211 docs, 112 media, OK
```

Then start Claude Code in the repo root. It reads `CLAUDE.md` automatically. Point it
at `TASKS.md` and work top down.

## Layout

```
CLAUDE.md      operating rules — the evidence discipline, non-negotiable
TASKS.md       prioritized queue with acceptance criteria per task
spine/         the derived data (unpack the snapshot here)
sources/pdf/   211 source PDFs — re-pull from Drive, not in the snapshot
sources/media/ 112 videos — re-pull from Drive, not in the snapshot
scripts/
  verify_spine.py    integrity gate — run after every task
  fetch_sources.py   idempotent Drive pull, diffs against what is already ingested
  track_object.py    per-frame blob tracking, pixel coordinates only
  build_site.py      regenerate the public reader from current CSVs
site/          static single-file reader, deploys to GitHub Pages as-is
```

**The snapshot contains derived data only.** Source PDFs and videos are not in it and
must be re-pulled before any OCR, visual, or citation-verification work:

```bash
python3 scripts/fetch_sources.py --all --dry-run   # check first
python3 scripts/fetch_sources.py --all
```

## Why this moved off the chat sandbox

The sandbox capped at ~7 GB usable disk, timed out long ffmpeg jobs, and reset between
sessions, forcing a full re-pull from Drive every time. The remaining work is
multi-hour OCR across 2,537 pages and batch tracking across 112 videos. That needs
persistent disk and no execution ceiling.

## What still belongs in chat, not here

Judging what a clip actually shows, deciding what counts as a contradiction, and
design calls. Code runs the pipeline; a conversation is better for looking at things
and deciding what they mean.

## Data discipline in one line

Every stored value is verbatim with a cite, absence is recorded rather than explained,
contradictions are kept side by side, and Layer 5 relations are derived at query time
and never written to disk.
