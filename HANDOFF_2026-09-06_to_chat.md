# PURSUE corpus — handoff to chat

Written 2026-09-06 from a Claude Code session, continuing the handoff that came the other
way earlier the same day. Read `CLAUDE.md` and `TASKS.md` at the repo root first — both were
updated this session and now carry things that used to live only in a handoff document.

Repo: `github.com/jdsebastian85/pursue-corpus` (main)
Local clone: `C:\Users\bashs\pursue-corpus`
Site: `jdsebastian85.github.io/pursue-corpus/` · Investigator: `/investigate.html`

The project owner is a novice at the command line. Give exact commands, one at a time, and
do not assume a step succeeded because it did not error.

---

## 1. Immediate state

**T2.5 is closed and live.** Page images render beside the transcript on the public site.
`verified_on` is set to 2026-09-06 against images that were actually confirmed to load.

**The upload is still running** and is the only thing outstanding on T2.5. See §4.

Repo is clean and in sync with origin at `a863e87`.

---

## 2. What this session changed

The previous handoff said "push it and it works." That was wrong — the push had already
landed, and images still 404'd. Three separate defects were behind it, two of them not
previously identified, and the third was worse than the problem it was found next to.

### 2a. The host keys images by the real filename, not the catalogued one — `62c4ea3`

`manifest.csv` records `source_file` with spaces, underscores and dots flattened to hyphens.
The render folders — and therefore the keys on Internet Archive — carry the filename from the
source drop. **They differ for 90 of 211 releases.** Proven directly:

    .../NASA-UAP-D015_Astronaut-...pdf/p0008.jpg   → 200, 369 KB
    .../NASA-UAP-D015-Astronaut-...pdf/p0008.jpg   → 404   ← what the site generated

`scripts/build_page_image_dirs.py` joins the two on a separator-insensitive key. All 211
resolve, zero ambiguity. The result is written to `site/page_images.json` under `folders`,
and `pageImageUrl()` consults it ahead of the manifest value. An ambiguous match would be
reported and omitted, never guessed. The mapping is hosting bookkeeping, so it lives in
`site/` and `source_file` is left exactly as catalogued.

Regenerate with:

```bash
py -3.11 scripts/build_page_image_dirs.py --write
```

### 2b. Spine CSVs were read as cp1252 — `62c4ea3`

`build_investigator.py` opened every spine CSV with no encoding, so on Windows they decoded
as cp1252. A `U+2013` in one release id reached the built page as mojibake and could never
have matched anything. Same class of bug as the template read/write fixed earlier in
`058b5c3`. `pages.jsonl` is deliberately still opened `"rb"` — it is byte-indexed.

### 2c. Git was rewriting line endings, which broke the transcript — `f6e0d64`, `78f0e2e`

**This was the serious one and it was not in the previous handoff.**

`spine/pages.jsonl` is byte-indexed at build time and the browser fetches individual page
records from it with HTTP Range requests. `core.autocrlf` was true with no `.gitattributes`,
so the working copy carried one extra `\r` per line:

    working copy 32,206,882 bytes
    committed blob 32,198,221 bytes
    difference        8,661   ← exactly one per page

Offsets were computed against the CRLF copy and issued against the LF copy Pages serves.
Confirmed live: the record at offset 0 parsed and **every other one failed**. The transcript
was broken for 210 of 211 documents, silently, and had been for some time.

Fixed with `* -text` in `.gitattributes`, a working-tree renormalise, and a rebuild. 185
sampled records across 60 releases now decode and match the release and page they are
indexed under.

**If the transcript ever reports "Page record did not parse" again, check this first:**

```bash
wc -c spine/pages.jsonl && git cat-file -s $(git rev-parse HEAD:spine/pages.jsonl)
```

Those two numbers must be identical. This is now recorded in `CLAUDE.md` under
"Build invariants".

### 2d. Navigation keeps your place — `ce29739`

`go()` called `window.scrollTo(0,0)` unconditionally and there was no history stack. Every
return to a document list landed at the top of 211 rows and the browser back button did
nothing.

Each view is now a history entry. The scroll offset of the view being left is stamped onto
its own entry before the next is pushed, and `popstate` restores it. A redraw that is *not*
a navigation — starring, typing a note — leaves the scroll alone; that is why the pending
offset defaults to `null` rather than `0`. The view is written to the URL as well, so a
document or a single page can be bookmarked and reopened. Typing in the search box replaces
the entry rather than pushing one per keystroke.

Verified: back restores 1400px exactly, two-level back and forward keep both the view and
the offset, a bookmarked document URL opens to that document.

### 2e. Human coverage — `54adc2b`

Built after the project owner said the work is **surveying** — finding out what is in the
corpus — rather than searching for something specific or assembling a book. That answer
should shape anything built next.

Coverage rides on the existing marks record rather than a parallel store, so it exports,
imports and migrates with everything else. A page carries `worked` alongside `star` and
`note`; a release carries `assessed` on its own key. Those are **two different claims and are
kept apart** — a release can be assessed with no pages worked, and the list says which.

Nothing is inferred from opening a page. The tool cannot observe reading, so it does not
pretend to.

* Per release, a **comb of one tick per page**, filled where worked, clickable to toggle.
  This is deliberately the human half of the comb. When T10's machine-readability row lands
  directly above it, the disagreement between the two rows — pages a machine can read that
  no human has opened — is the gap findings live in, and nothing surfaces it today.
* The document list carries a coverage pill per release, a corpus line (started, worked
  through, pages worked of 8,661) and a filter across all / not started / in progress /
  worked through. The filter travels in the URL.
* **Next not started →** jumps to the next untouched release, wrapping once, from both the
  list and the foot of a release.

One correctness point that fell out of it: a record is now discarded only when it makes no
claim at all. Un-starring a page you had worked used to delete the record, which would have
silently taken the coverage with it.

### Commits this session

    a863e87  docs: record the Python version the IA uploader needs
    54adc2b  feat: human coverage — what you have worked, stated not inferred
    ce29739  feat: navigation keeps your place, and the URL carries the view
    8c901af  docs: record T2.5 state and the two build invariants
    78f0e2e  rebuild: page index against normalised line endings
    f6e0d64  fix: stop git rewriting line endings
    62c4ea3  fix: address page images by their real host folder

---

## 3. What was verified, and how

Nothing below is inferred from the code reading correct.

* 33 page images fetched **200** from the live host, including folder names containing a
  space, an apostrophe and an en-dash — the three cases most likely to break URL encoding.
* The live page's own `pageImageUrl()` returns 200 for all five previously-broken cases.
* **24 of 24** transcripts across the corpus parse on the live site. Before the fix: 0 of 24.
* A live page view at `#t=page&id=DOW-UAP-D092&pg=43` loads the scan (1598 px) beside 2,418
  characters of transcript.
* Coverage round-trips live; the comb renders 85 ticks for an 85-page release; a star round
  trip does not destroy coverage; a star-only round trip still discards the record.
* **Privacy:** `direct_deposit_info.pdf` appears in no render folder, in no line of
  `uploaded.txt`, and in none of the 13,141 files on the IA item. Checked explicitly.

---

## 4. The upload — the one thing still in flight

**6,967 of 8,866 as of writing.** Measured throughput 6.4 files/min, so roughly **5 hours**
remaining. Releases late in the alphabet report the image missing from the host until it
finishes; that panel is behaving correctly, not failing.

Resume or continue with:

```bash
py -3.11 C:\Users\bashs\ia_upload_resume.py
```

It skips everything already in `C:\Users\bashs\uploaded.txt`. **It must be `py -3.11`** —
Python 3.14 on this machine cannot complete an SSL handshake with archive.org and the
connection resets before any upload starts, which presents as a network fault and is not.

Progress can be checked without touching the running job:

```bash
wc -l < C:\Users\bashs\uploaded.txt
```

Note the real target is **8,661**, not 8,866. The extra 205 images sit in folders named
`... (n).pdf` — duplicate downloads of releases already mapped, which no page view will ever
request. They are already uploaded and are harmless.

---

## 5. Approved and waiting on the upload

The project owner has already said yes to both of these. **Do them once the upload reports
done, not before.**

1. **Delete the dead weight on the IA item.** 1,897 images carry a full Windows path as their
   key (`C:/Users/bashs/page_images_rendered/...`), about 0.51 GB, from an early run. Plus
   206 images in the `(n).pdf` duplicate folders. Show the exact delete list before running
   anything. There are also 4,434 IA version-history files (`history/files/...~N~`) which are
   IA-internal.
2. **Fix the public item title.** It currently reads `PURSUE Corpus � page images` — a
   mojibake em-dash. `METADATA` in `C:\Users\bashs\ia_upload_resume.py` has already been
   corrected so future runs stop rewriting it, but the running process holds the old value in
   memory, so **changing the live title now would just be overwritten.**

---

## 6. Next work

**T11 is the recommended next task.** It blocks T10, and T10 completes the comb whose bottom
half was built this session.

1. **T11 — two-floor unit contradiction.** The 0.90 gap threshold is a page-level quality
   score on 0–1; the published floor of 60 is a Tesseract per-word confidence on 0–100.
   Different units measuring different things, and the coverage comb's hollow ticks render
   off one of them. Must be resolved before T10 can render honestly.
2. **T10 — co-presence panel with coverage comb.** Non-optional, never responsive-hidden.
   Per-release readability costs 17.8 KB embedded across all 211 releases (6,124 solid /
   818 hollow / 1,719 amber). Its machine row goes directly above the human comb now in
   `docView()`.
3. **T1b** — ingest of 21 un-measured videos. Blocked on item 4.
4. **`ingest.py` column preservation** — drops `source_url` / `mirror_url` / `working_url` on
   re-ingest.
5. **T9 marks migration** — a stored verbatim set matching several groups must report
   ambiguous with both candidates, never auto-resolve.
6. **Aliases review** — Stever is H. Guyford Stever, a distinct person. Reject that cluster
   and record why.
7. **Fifth release reconciliation** — downloaded 2026-08-07, still not reconciled against the
   manifest. Do not claim a complete index until it is. Related observation from this
   session: 276 PDFs were rendered but the manifest holds 211 releases, and all 65 extra
   folders are `(n).pdf` duplicates — so this is *not* evidence of 65 unreconciled documents.
8. **T12 cross-modal correspondence.** Spec at `docs/T12_correspondence.md`, pushed at
   `ae05eb4`.

### Still open from the investigator rework

* **Readable transcripts (three-state view).** Raw shipped text / recovered OCR / a reading
  layer where every correction renders visibly as a correction, derived at render time and
  never written to the spine. Effectively blocked: there are only 61 recovered pages and the
  schema is still page-per-row with no per-word confidence, so the middle state has almost
  nothing to show. Needs T2.1–2.3.
* **A hand-assembled reading queue.** The automatic ordering that surveying wants is built
  ("next not started"). The curated queue is the editorial act that produces a book, and is
  worth building when the work shifts from surveying to assembling.

### Also outstanding

211 source PDFs are still inside Drive zips with no `source_url` / `mirror_url` /
`working_url`. Every document page says so. An IA upload of the PDFs themselves — separate
from the page images — is the preferred fix: permanent per-document URLs, and insulation
against removal from war.gov.

---

## 7. Environment gotchas

* **`py -3.11` for anything touching archive.org.** Python 3.14 cannot complete the SSL
  handshake. Python 3.11 is at
  `C:\Users\bashs\AppData\Local\Programs\Python\Python311\`.
* **PowerShell `Out-File -Encoding utf8` writes a BOM**, which breaks `json.load`. Use
  `[System.IO.File]::WriteAllText(...)` for JSON.
* **Never let git rewrite line endings.** Enforced by `.gitattributes` now; see §2c.
* **Read spine files with an explicit encoding.** They are UTF-8; Python on Windows defaults
  to cp1252.
* **IA rate-limits hard.** `bucket_tasks_queued exceeds` and 502s are IA-side, not client
  bugs; the uploader backs off and retries. `SLEEP_SEC = 5` has been holding.
* **GitHub Pages caching.** After a push, the *server* updates within a minute or two but a
  browser will happily serve a stale `investigate.html`. Verify with a cache-busting query
  string before concluding a fix did not deploy — this cost real time this session.
* **Do not paste tokens into chat.** Several were leaked and rotated in an earlier session.
  Use the credential manager.

Files that live outside the repo and are easy to lose:
`C:\Users\bashs\ia_upload_resume.py`, `C:\Users\bashs\uploaded.txt`,
`C:\Users\bashs\page_images_rendered\`.

---

## 8. Standing constraints

From `CLAUDE.md`, binding on all work:

* Verbatim only. Every row carries `release_id` + page cite.
* Absence is recorded, never assumed.
* Contradictions preserved side by side, never resolved silently.
* Entities are candidates, not facts.
* Layer 5 relations derived at query time, never stored.
* Flag commercial angles unprompted.

Licence split: released PDFs and video are public domain (17 U.S.C. § 105); `spine/` is
CC BY 4.0; `scripts/`, `site/` and built pages are MIT.

**One rule earned this session:** `investigate.html` at the repo root is generated output.
Never edit it directly — edit `site/investigator.html` and rebuild with
`py -3.11 scripts/build_investigator.py --out investigate.html`.
