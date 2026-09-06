# PURSUE corpus — handoff to Claude Code

Written 2026-09-06 from a Cowork chat session, answering `HANDOFF_2026-09-06_to_chat.md`
from earlier the same day. Read `CLAUDE.md` and `TASKS.md` first, as always. Then read the
three new documents in `docs/` that this session produced — they are the substance of this
handoff and are not repeated in full here.

Repo: `github.com/jdsebastian85/pursue-corpus` (main)
Local clone: `C:\Users\bashs\pursue-corpus`
Site: `jdsebastian85.github.io/pursue-corpus/` · Investigator: `/investigate.html`

The project owner is a novice at the command line. Exact commands, one at a time, and do
not assume a step succeeded because it did not error.

---

## 1. Immediate state

**Nothing was executed this session.** The isolated Linux shell on the owner's machine
failed to start, so the chat session could only stage files up, work on them remotely, and
write files back. No script ran, no git command ran, `verify_spine.py` was not run. Every
claim below about the repo or the data is from reading files, not from running anything.
**Your first job is to verify the state the chat session could only observe.**

**The upload was still running.** `uploaded.txt` read 7,025 lines when last staged (up from
6,967 in the prior handoff), and its mtime was advancing, so the process was alive. Target
is 8,661. Check it before anything else:

```bash
wc -l < C:\Users\bashs\uploaded.txt
```

If it is at or past 8,661, the two parked items in §5 of the previous handoff are unblocked
(IA dead-weight delete, with the list shown first; and the mojibake title fix, only after the
uploader process has exited). If it is short, the uploader may have died — resume with
`py -3.11 C:\Users\bashs\ia_upload_resume.py`. Never `py` alone; 3.14 cannot handshake
with archive.org.

**Git:** last known clean and in sync at `a863e87`. This session then wrote four new files
to the working tree and did not commit them (see §3). Expect `git status` to show them as
untracked and nothing else modified. If anything else shows modified, stop and find out why.

---

## 2. Decisions the owner made this session

These are settled. Do not reopen them; build on them.

1. **Umbrella: anthro-tech.org.** PURSUE keeps its own name and its own credibility. It sits
   beside VISCERA under anthro-tech.org. It is *not* badged as the AI v.Human app and is
   *not* under Lyriqal Digital Media.
2. **The coverage comb is separable IP, documented under the AI v.Human thesis**, with PURSUE
   as the worked example — not as a PURSUE feature. That is where the reusable, sellable idea
   lives.
3. **Look: restrained instrument, cool palette.** Dark-first slate ground, one steel-cyan
   accent, glass and depth on the *chrome only*, the evidence layer flat and opaque always.
   Amber is reserved for exactly one meaning — a page that could not be read — and appears
   nowhere else.
4. **Sequencing: interleave.** The design system lands together with T11 (Wave 1), not before
   and not after.

**One thing is NOT yet signed off:** the owner has been shown the rendered palette
(`docs/tokens_preview.html`) but had not confirmed it visually when this handoff was
written. He asked for this handoff instead of answering. **Get an explicit yes on the
palette before Wave 1.2 bakes it into `site/investigator.html`.** Everything else in the
token set is cheap to change; the mood is not.

---

## 3. What this session produced (all in the working tree, none committed)

| File | What it is |
|---|---|
| `docs/BRANDING_UX_PLAN.md` | The four-wave plan. Each task is 2–3 actions by the owner's request. Companion to `TASKS.md`, which stays the queue of record. |
| `docs/UX_AUDIT.md` | Wave 0.1. Current-state read of `site/investigator.html`: it is already tokenized and theme-aware, the chrome-vs-evidence class split already exists in the markup, and the five concrete legibility problems to fix. |
| `docs/DESIGN_TOKENS.md` | Wave 0.2. The full CSS variable set (light on bare `:root`, dark in both dark blocks, same structure the tool uses), the reserved comb trio, glass values, and how each token maps to existing classes. |
| `docs/tokens_preview.html` | A self-contained rendering of the token set: header with glass, palette chips, the two combs stacked, a chrome card, and the flat evidence layer. Open it in a browser and toggle the theme. |

Commit them as one docs commit once you have confirmed `git status` shows only these four:

```bash
git add docs/BRANDING_UX_PLAN.md docs/UX_AUDIT.md docs/DESIGN_TOKENS.md docs/tokens_preview.html
git status
git commit -m "docs: branding/UX plan, investigator audit, design tokens, palette preview"
git push
```

Also add a one-line pointer in `TASKS.md` to `docs/BRANDING_UX_PLAN.md` so the queue of
record knows the plan exists. The plan does not replace `TASKS.md`.

---

## 4. Findings from the audit that change how Wave 1 is built

The full audit is in `docs/UX_AUDIT.md`. The three that matter most for your hands:

* **The reskin is a token swap, not a rewrite.** `site/investigator.html` already has a clean
  `:root` / `prefers-color-scheme` / `[data-theme="dark"]` structure. Replace values inside
  it; do not restructure. The chrome classes (`header`, `nav`, `.card`, `.pill`, `button.act`,
  `footer`) and the evidence classes (`.pagetext`, `.comb`, `.unclear`, `.redblk`, `mark`,
  `.pageimg`, `ul.cites`, `.conflegend`, `.warnbox`) are already separate, so "glass on chrome
  only" is enforceable at the selector level.
* **Comb ticks are 11×17px** — too small to tap on a phone, and Wave 2 stacks a second comb
  row directly above them. Keep the visual tick small but give it a ≥24px touch area.
* **There is no amber in the current CSS at all**, which is good: the reserved
  `--comb-amber` collides with nothing. Keep it that way. Do not let the search highlight
  (`--mark`) drift toward amber; the token set deliberately makes it a cool wash.

---

## 5. Next work, in order

**Wave 0.3 — identity brief, plus a correction the decision forces.** Not started. One
page: the PURSUE lockup with "an anthro-tech.org project" beneath it, wordmark direction,
how it stays distinct from the Lyriqal mark (angular lime-and-purple) and the AI v.Human
mark, and the name and home of the comb write-up. Save as `docs/IDENTITY_BRIEF.md`.

**The repo currently contradicts the umbrella decision.** `CITATION.cff` lists Lyriqal
Digital Media as author, and the public site and README carry Lyriqal branding from the
earlier note. Under today's decision that is wrong, and the CITATION string is the one that
matters most because it appears in every citation anyone ever makes. Grep for it:

```bash
git grep -n -i "lyriqal"
```

Then ask the owner one question before changing anything: does he want the author line to
read **anthro-tech.org**, or his **legal name** with anthro-tech.org as affiliation? Personal
attribution and org attribution are different choices and he has not made it yet. Do not
guess. Once answered, update `CITATION.cff`, the README section, and any site footer or
`<title>` text in one commit.

**Wave 1.1 — the two-floor contradiction (T11 item 4). Blocks T10.**
The chat session could not run anything, so this is where your work starts in earnest.

- Read how each floor is actually computed and what data backs it: the 0.90 page-level
  quality score (0–1) that drives the `LOW_OCR_QUALITY` gap rows, and the published
  word-confidence floor of 60 (0–100) in the header of `scripts/build_investigator.py` and
  in `D.conf_floor`.
- The crux the chat session worked out from the docs, to be confirmed against the data:
  **per-word confidence barely exists.** T2.3 is not started; only ~61 recovered pages are in
  the page-per-row schema with no scores. So the comb's 818 hollow ticks can only come from
  the page-quality flag today. The honest resolution is likely: until T2.3 populates per-word
  confidence corpus-wide, the hollow tick keys off the page-quality flag, is *named* as a
  page-level readability proxy, and is kept explicitly distinct from the per-word display
  floor. Document which and why in `CLAUDE.md` under build invariants.
- Add a `verify_spine.py` assertion that enforces the one meaning, then run it:

```bash
py -3.11 scripts/verify_spine.py
```

If the data says something different from the crux above, the data wins. Say so.

**Wave 1.2 — apply the tokens to the chrome.** Only after the palette yes (§2). Edit
`site/investigator.html` values per `docs/DESIGN_TOKENS.md`. Touch chrome selectors only.
Rebuild and check at a phone width:

```bash
py -3.11 scripts/build_investigator.py --out investigate.html
```

**Wave 1.3 — commit and deploy** as one reviewable change. Verify the Pages deploy with a
cache-busting query string before calling it done — a stale `investigate.html` in the browser
cost real time in the previous session.

Waves 2–4 are in the plan document. Wave 2 (T10 comb) cannot start until 1.1 lands.

---

## 6. Things to check that the chat session could not

Run these early. None of them were run this session.

```bash
git status
```

```bash
wc -c spine/pages.jsonl && git cat-file -s $(git rev-parse HEAD:spine/pages.jsonl)
```

Those two numbers must be identical (the line-ending invariant from `CLAUDE.md`).

```bash
py -3.11 scripts/verify_spine.py
```

---

## 7. Environment gotchas (unchanged, compact)

Full list in §7 of `HANDOFF_2026-09-06_to_chat.md` and in `CLAUDE.md`. The ones that bite:

* `py -3.11` for anything touching archive.org. 3.14 fails the SSL handshake silently.
* Never let git rewrite line endings. `.gitattributes` has `* -text`; leave it.
* Read spine files with an explicit UTF-8 encoding. Windows defaults to cp1252.
* PowerShell `Out-File -Encoding utf8` writes a BOM that breaks `json.load`.
* GitHub Pages serves stale in the browser after a push. Cache-bust before concluding.
* Do not paste tokens into chat. Use the credential manager.
* `investigate.html` is generated output. Edit `site/investigator.html`, then rebuild.

Files outside the repo, easy to lose: `C:\Users\bashs\ia_upload_resume.py`,
`C:\Users\bashs\uploaded.txt`, `C:\Users\bashs\page_images_rendered\`.

---

## 8. Standing constraints

From `CLAUDE.md`, binding on all work: verbatim only, every row cited; absence recorded never
assumed; contradictions side by side never resolved; entities are candidates; Layer 5
derived at query time never stored; flag commercial angles unprompted. Now also binding from
this session: **amber means unreadable and nothing else; the evidence layer is never glass;
no believer tone and no debunker tone — the look is tone too.**

The site stays free. The pipeline is the sellable asset; the comb is the separable IP.
