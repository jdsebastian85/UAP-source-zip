# PURSUE — branding and UX plan

Written 2026-09-06 from a chat session. Companion to `TASKS.md` and `CLAUDE.md`, not a
replacement. `TASKS.md` stays the work queue of record. This file holds the identity and
UX direction and sequences it against the functional work already queued.

## Decisions locked this session

- **Umbrella: anthro-tech.org.** PURSUE keeps its own name and its own credibility. It sits
  beside VISCERA under anthro-tech.org rather than being folded into a product brand. It is
  not under Lyriqal Digital Media, which is the drone and video content brand and the wrong
  audience for a provenance tool.
- **The coverage comb is documented separately as reusable IP under the AI v.Human thesis.**
  The corpus stays PURSUE. The pattern — put the unreadable fraction on every result so a
  reader can tell a true absence from an unread page — is written up on its own, with PURSUE
  as the worked example, so it can travel to other corpora, FOIA readers and e-discovery.
- **Look: restrained instrument aesthetic.** Dark, precise, modern, with depth and glass on
  the chrome only. The evidence layer — transcript, coverage comb, cites — stays flat, high
  contrast and legible. Phone first. Futuristic in feel, archival in discipline.
- **Cadence: interleave.** The brand and design system land together with T11 rather than
  before or after it.

## Standing rules that bind every task below

- `investigate.html` at the repo root is generated. Never edit it directly. Edit
  `site/investigator.html` and rebuild with
  `py -3.11 scripts/build_investigator.py --out investigate.html`.
- Git must never rewrite line endings. `.gitattributes` enforces it. If the transcript ever
  reports "Page record did not parse", check that first.
- Run `py -3.11 scripts/verify_spine.py` after every task that touches data or the build.
- No believer tone and no debunker tone. The look is tone too. **Inside the evidence layer
  the accent hue means one thing only, that a page could not be read, and no other element
  there may use it.** Settled 2026-09-06 as option B of three: the owner chose orange as the
  brand accent, which collided with the earlier reservation of amber, so the rule was kept
  and the hue swapped. The chrome may use the accent freely. See `docs/DESIGN_TOKENS.md` and
  the rendered comparison in `docs/tokens_preview_orange.html`.
- The site stays free. The material is public domain and credibility depends on it.

## A note on the name

PURSUE is anchored to the PURSUE Act and the release initiative, not a coined brand. That
external anchor is a credibility asset, so the name stays. The identity work dresses it, it
does not rename it.

---

## Wave 0 — foundations (doable now, no local shell needed)

The isolated Linux shell on the machine is down this session, so these are done by staging
files up, working on them here, and writing results back with exact git commands.

**Task 0.1 — audit the current investigator source**
- Stage `site/investigator.html` up and inventory the existing colours, type scale, spacing,
  and exactly where the evidence layer is styled versus the chrome.
- Write a one page current-state note: what to keep, and where the present styling already
  fights legibility on a phone.

**Task 0.2 — draft the design tokens**
- Define a small token set as CSS variables: a background scale, one accent, the three comb
  states locked as non-negotiable, a type scale, and spacing.
- Put them in a design note, not into the tool yet, so the system is agreed before the build
  is touched.

**Task 0.3 — identity brief**
- One page: the PURSUE lockup with "an anthro-tech.org project" underneath, the wordmark
  direction, and how it stays distinct from the Lyriqal and AI v.Human marks.
- Name where the AI v.Human comb write-up will live and what it is called.

---

## Wave 1 — T11 and the design system land together

**Task 1.1 — resolve the two-floor contradiction (blocks T10)**
- Inspect how each threshold is actually computed today: the 0.90 page-level quality score on
  0 to 1, and the published word-confidence floor of 60 on 0 to 100, and which data backs
  each. Per-word confidence barely exists yet, only about 61 recovered pages, so this has to
  be settled against what is really populated, not what is planned.
- Decide which measure the comb's hollow tick represents, document which and why in
  `CLAUDE.md` build invariants, and add a `verify_spine.py` assertion that enforces the one
  meaning. Provisional recommendation, to confirm against the data: until T2.3 populates
  per-word confidence corpus wide, the hollow tick keys off the page-quality flag and is
  named as a page-level proxy, kept distinct from the per-word display floor.
- Run `verify_spine.py`.

**Task 1.2 — apply the design tokens to the chrome**
- Restyle nav, headers and cards in `site/investigator.html` with the restrained instrument
  look, leaving transcript, comb and cites untouched.
- Rebuild `investigate.html` and check it at a phone width before anything else.

**Task 1.3 — commit and deploy as one reviewable change**
- Exact git commands, one at a time.
- Confirm the Pages deploy with a cache-busting query string before calling it done.

---

## Wave 2 — the co-presence comb and evidence-layer polish (T10)

**Task 2.1 — build the comb payload**
- Emit the per-release run-string of solid, hollow and unreadable states into the payload, roughly
  17.8 KB across all 211 releases. This is the one build change T10 needs.
- Run `verify_spine.py`.

**Task 2.2 — render the comb, non-optional and high contrast**
- Build the co-presence panel per `docs/T10_copresence.md`: three outcomes never two, a zero
  result unable to render without its denominator, never responsive-hidden.
- Style it in the flat evidence-layer discipline with the reserved `--comb-*` tokens, and
  confirm the unreadable tick is unmistakable on a phone in daylight. The human comb's worked
  tick is `--worked` (bone), never the accent, so the two stacked rows stay separable.

**Task 2.3 — commit and deploy**
- Git commands, then a cache-busted deploy check.

---

## Wave 3 — readability and search (open investigator items)

Both are partly blocked on the T2 OCR pass, which needs a machine with tesseract, poppler and
opencv plus the source PDFs. That dependency is real and is called out here rather than hidden.

**Task 3.1 — full-text search across pages**
- Decide Pagefind versus a prebuilt inverted index, after recovered text exists so the index
  is not half empty.
- Wire it in and confirm a search hit jumps to the right page and cite.

**Task 3.2 — three-state readable transcript**
- Raw shipped text, recovered OCR, and a reading layer where every correction renders visibly
  as a correction, derived at render time and never written to the spine.
- Ship only where recovered text exists, and say plainly where it does not.

---

## Wave 4 — launch and positioning

**Task 4.1 — finish the upload and clean the IA item (parked until the upload reports done)**
- Show the exact delete list before running anything: the 1,897 Windows-path images, the
  `(n).pdf` duplicates, the version-history files.
- Fix the mojibake item title after the running process exits, not before, or it gets
  overwritten.

**Task 4.2 — prebuilt summary JSON for first paint**
- Cut the 32 MB that loads before anything renders. Biggest conversion lever available and it
  touches nothing in the spine.

**Task 4.3 — tell someone, on the epistemics angle**
- One honest post describing what is indexed and what is not, aimed where the coverage-comb
  epistemics is the hook rather than the subject matter.
- Publish the comb write-up as a standalone UI pattern under the AI v.Human thesis, PURSUE as
  the worked example.

---

## Commercial notes (standing instruction, surfaced unprompted)

- The pipeline is the sellable asset, not the corpus. Ingest to spine to searchable static
  site is repeatable for any large FOIA or declassification dump. Newsrooms, law firms in
  discovery, academic archives and advocacy orgs all receive dumps with no way to navigate
  them.
- The coverage comb is separable IP. Documenting it away from PURSUE, under the AI v.Human
  thesis, is what lets it be reused and cited on its own.
- Keeping PURSUE under anthro-tech.org rather than badging it as the AI v.Human app protects
  the corpus's credibility. The trade is weaker direct funnel to the app. The comb write-up
  is the bridge that connects the two without coupling their reputations.
- Internet Archive hosting keeps marginal cost near zero, which is what makes the free public
  version sustainable rather than sustainable until a bandwidth bill arrives.

## Dependencies and constraints, at a glance

- T11 blocks T10. Do Wave 1 before Wave 2.
- Wave 3 is blocked on the T2 OCR pass, which needs a toolchain machine and the source PDFs
  out of the Drive zips.
- Wave 4.1 is parked until the page-image upload finishes.
- This session's local Linux shell is down, so execution is staged-file edits plus git
  commands until it is back, or until the work is done directly on the machine.
