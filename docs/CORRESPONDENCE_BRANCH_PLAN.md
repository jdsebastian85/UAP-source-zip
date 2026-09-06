# Tessera — founding plan

Written 2026-09-06. A new project under the AI v.Human umbrella, with the PURSUE corpus as
the first material it operates on. Companion to `docs/BRANDING_UX_PLAN.md`, which covers the
investigator's own reskin and is unaffected by this.

**Name: Tessera.** A tessera is a single tile in a mosaic. The tile is a real and individual
thing, the picture is assembled from tiles by a person, and no tile claims to be the picture.
That is this tool's governing rule stated as a name: each measurement is a tessera, the
ordering is the mosaic, and the two are never confused for one another. Use the distinction
in the README and in the eventual write-up — it explains the whole epistemic stance in one
sentence, which is worth more than a paragraph of hedging.

---

## 1. What this actually is

It is **T12 lifted out of PURSUE and made corpus agnostic.**

`docs/T12_correspondence.md` already specifies cross-modal correspondence for PURSUE: nine
acceptance criteria, tier rules, sampling policy, queue schema. That work was always going to
be built. Building it as a separate repo is the same work with a harder boundary, so the
split costs setup rather than duplication. That is the answer to "you maintain two things":
you were already going to maintain this one.

What it does, in one line: **given a pile of material with no reliable ordering, measure what
overlaps, and hand a human ranked candidates to promote.**

## 2. The one rule everything hangs off

**Measure the overlap. Never assert the sequence.**

Frame overlap is a measurement, of exactly the same kind as a character count or a page
number: reproducible, checkable by anyone holding the files.

    MEASUREMENT   clips A and B share 47 frames at phash distance ≤4, aligning at offset 12.3s
    CONCLUSION    clips A and B are the same event, and A comes first

The first is storable. The second is a human act, recorded with a name and a date on it, and
reversible. This is why the branch does not violate PURSUE's rules — it is PURSUE's method
pointed at video.

Everything the tool emits is a candidate. Nothing it emits is a finding.

## 3. Interface to PURSUE — one-way trust

The tool reads a corpus and writes only to its own output. It never writes into `spine/`, and
it never writes into PURSUE at all. PURSUE consumes its output by explicit human promotion
into `review/`, and `verify_spine.py` continues to assert that no spine row references a
`review/` file.

This is a stronger boundary than the in-repo version would have been, because it is physical
rather than conventional. Conventions erode; a repo boundary does not.

**Consequence to accept:** the gates live in PURSUE, so the new repo needs its own minimal
verifier from day one — schema check, every emitted row carries its source file and offsets,
no row without a measurement behind it. Do not defer this. A candidate store with no gate
becomes a findings store within a month.

---

## 4. Phase 1 — the matcher, validated before it is trusted

First pass targets one media family, per the scope decision. **Which family matters more than
it sounds**, and the ordering below is deliberate.

**Task 1.1 — start with `DOD_111764*`, eight clips.**
- It contains a known positive control: `DOD_111764189` (the butte orb, 54s) and
  `DOD_111764213` (21s) are recorded in `CLAUDE.md` as the same terrain. You already know the
  answer for that pair, so it validates the matcher rather than testing it.
- The seismograph renders scattered across families are the natural negative control: they
  should match each other and nothing else. A matcher that joins a seismograph render to sky
  footage is broken, and you will see it immediately.
- T4's kinematic pass already targets this family, so the work compounds.

**Task 1.2 — build the measurement, not the verdict.**
- Perceptual hash per sampled frame, plus audio fingerprint where there is audio. Emit
  `overlaps.csv`: `clip_a, clip_b, frames_matched, mean_distance, offset_seconds, method`.
- Every row carries the method and the parameters that produced it, so a later run with
  different settings is distinguishable rather than silently replacing it.

**Task 1.3 — then `DOD_111887*`, fifteen clips.**
- Six are already noted as sharing an identical reticle and annotation symbology, plus
  composites. Composites are assembled from sources, so this family should produce genuine
  many-to-one joins and will stress the schema in a way eight clips will not.

**Deliberately last: `video_2605_DOD_*`, fifty clips.** These are edited presentation products
whose own title cards say "B/W values inverted, picture zoomed". **Naive perceptual hashing
will fail on them and fail quietly** — inverted and rescaled footage does not match its source
under plain phash. That family needs a matcher invariant to inversion and scale, which is a
different build. Running it early would produce a confident empty result and teach you the
wrong thing about your own tool.

---

## 5. Phase 2 — media coverage in the investigator (ships independently)

This is cheap, honest, and does not wait on anything above.

**Task 2.1 — the human row now.**
- "Watched" per clip and per segment, stated by the reader, never inferred from a player
  being opened. Same discipline and the same storage as page coverage, so it exports,
  imports and migrates with the existing marks record.
- A media coverage pill and filter on the media list, matching the document list.

**Task 2.2 — the machine row stays absent, and says so.**
- T12 already established that audio has no readability denominator: a segment where nobody
  spoke and a segment nothing could hear are indistinguishable. So the media comb ships with
  the machine row missing and a line naming the blocker, exactly as a page with no text layer
  says so rather than rendering an empty panel.
- What unblocks it is a per-segment **audibility** measure taken from the signal, not from a
  transcriber's confidence. Name it as separate work; do not let it arrive by accident with ASR.

---

## 6. Phase 3 — the third comb row

The investigator branch's real contribution to the tool.

Today the comb has two rows: what a machine **can** read, and what a human **has** worked. An
agent pass adds a third: what a machine **has actually examined**.

**Task 3.1 — record examination as a claim, not a byproduct.**
- An agent pass writes what it examined, when, under which prompt version, into the candidate
  store. Examined is not the same as understood, and the row says only that the material was
  put in front of a model.

**Task 3.2 — render the three rows and let the disagreements be the finding.**
- Readable but unexamined. Examined but never human-checked. Touched by nobody at all.
- Those gaps are the output. Nothing else on the page needs to argue for them.

**Constraint, non-negotiable:** agent output lands in the candidate tier. An AI investigator
is precisely the reason that gate has to exist before the branch, not after.

---

## 7. Phase 4 — ordering, layered

Built in this sequence because each layer is grounded by the one before it.

**Task 4.1 — clustering from measured joins only.**
- Grounded joins are: enclosure references (PURSUE T6, 251 rows, the page itself points at
  another document), shared entities with page cites, verbatim shared event names, and the
  clip overlaps from Phase 1. Not similarity, not vibes.

**Task 4.2 — chronology inside clusters.**
- Only 117 of 211 documents carry a year token. Undated stretches render as undated. A
  timeline that quietly interpolates is worse than one with visible holes.

**Task 4.3 — the curated queue across clusters.**
- The editorial act, done by hand, that turns a corpus into something readable. This is the
  step that marks the shift from surveying to assembling, and it should stay manual.

---

## 8. Cost profile — read this before scheduling anything

The intuition inverts here, so it is worth stating plainly.

| Work | Compute | Credits |
|---|---|---|
| Clip overlap matching | heavy, a long evening per family | **near zero** — ffmpeg and hashing, no model calls |
| Media coverage UI | trivial | low |
| Ordering layers 4.1 and 4.2 | light, joins over existing spine data | low |
| Agent examination passes | light | **this is the sink, and it scales with material** |

The single control that matters is scope on Phase 3. A family of eight to fifteen clips is
inherently bounded, which is why the media-family choice is the cheap one. Do not let a
Phase 3 pass loose over 8,661 pages without a ceiling agreed in advance.

---

## 9. Open

- **The name.** Candidates: SEAM (where clips join), TESSERA (mosaic tile), CONCORD,
  REGISTER (as in image registration), COLLATE. The repo cannot exist without one.
- **Still pending from the attribution work:** middle name or initial for the citation
  string, and whether to register an ORCID. Both are one-line edits and both apply to this
  repo too, since it will carry its own CITATION.cff.
- **Licence split for the new repo.** Code MIT is obvious. The emitted measurements are a
  derived database like the spine, so CC BY 4.0 is the consistent choice, but decide it once
  rather than inheriting it by habit.

## 10. Commercial note

This is the strongest sellable asset in the whole program, stronger than the coverage comb,
because it produces a hard artifact rather than a convention.

*Given a pile of misordered clips with no reliable timestamps, mechanically determine which
overlap and propose a sequence.* Buyers well outside UAP: newsrooms handed a raw footage leak,
legal teams with body-cam and CCTV in discovery, archives holding undated reels. It replaces
work currently done by a person watching everything twice.

Keeping it in its own repo, corpus agnostic from the first commit, is what makes that
possible. Built inside PURSUE it would have been a PURSUE feature.
