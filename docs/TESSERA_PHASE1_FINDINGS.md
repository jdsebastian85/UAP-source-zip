# Tessera — Phase 1 first run, findings

Run 2026-09-06 in the cloud container. Material: `DOD_111764189` (53.77s, 1613 frames) and
`DOD_111764213` (21.33s, 640 frames), both 1920x1080 @ 30fps, pulled from Drive by file id.
Durations match `media.csv` exactly.

**Everything below is a measurement. Nothing here concludes that any two clips are the same
event.** Two features were tested against controls before either was believed.

---

## 1. Perceptual hashing works, and cannot do the job alone

Implementation verified: identical frames hash to Hamming distance 0.

But on a fixed camera at dusk, **every frame looks like every other frame.** In a synthetic
control cut from a single clip, **3,480 of 3,600 frame pairs fell inside the match threshold**
and the offset scan could not localise the true lag. There is no diagonal in the distance
matrix because there is no temporal signal to form one.

> pHash reliably detects **literal frame reuse** and nothing else. It cannot establish
> sequence on static-sensor footage, and it should never be the only feature behind a
> proposed join.

## 2. The motion signature is sound — proven, not assumed

Per-frame motion energy, cross correlated over all lags. Tested on a slice of a single
decoded stream, where the true answer is known by construction:

    self-slice control   true lag +20.00s   ->   recovered +20.00s   r = 1.000

Exact recovery. The feature is real.

## 3. Re-encoding destroys the signal — and this is the important one

The same control, run on excerpts that had been **transcoded** (libx264 crf 18) rather than
sliced from one decode:

    transcoded control   true lag +20.00s   ->   recovered  -3.20s   r = 0.301

Same footage, same true offset, and the method fails. Compression noise dominates the motion
signal and decorrelates it from the source.

**Consequence for the corpus.** The `video_2605_DOD_*` family — fifty clips, the most tempting
target because their own title cards advertise re-presented footage — are **edited products,
re-encoded, inverted and zoomed**. That is precisely the condition that just defeated the
feature under controlled test. The plan already put this family last on general grounds. It is
now last on measured grounds.

## 4. What the real pair actually shows

    pHash   189 vs 213:  min distance 20, median 26, ZERO pairs within 8 of 4,644
    motion  189 vs 213:  best lag +0.90s, r = 0.817 over the full 21.2s

No shared frames. Literal reuse would show pHash distances near 0, and there are none.
The motion correlation is consistent with two separate recordings of the same location at the
same time of day — similar scene dynamics, not shared footage.

That agrees with what `CLAUDE.md` records: "same terrain". Same terrain was never a claim of
shared frames, and this run is the measurement that shows the difference.

**A correction to my own method:** I called 189/213 a positive control in the plan. It is not
one. It is a same-scene pair, not a same-footage pair. A positive control has to be a pair
known to share frames, and the only reliable source of that is synthetic — slice one clip.

## 5. Correlation scores need a null before any of them mean anything

The motion signature's lag-1 autocorrelation is **0.944**. It is a smooth, slowly varying
signal, so cross correlations between *any* two such signals run high by construction. An
r of 0.817 is not impressive against that baseline; it may not be distinguishable from chance.

> Before Tessera reports a single correspondence score, it must build a **null distribution**
> from clip pairs known to be unrelated — the NASA seismograph renders against sky footage,
> for instance — so that a score can be read against chance rather than against intuition.

Without this, the tool will emit confident numbers that mean nothing, which is worse than
emitting none.

---

## What changes in the plan

1. **Two features, not one.** pHash for literal frame reuse, motion signature for temporal
   alignment. Neither alone. A join needs agreement from both.
2. **Every control must be synthetic and encoding-matched.** Slice one decode. Never transcode
   a control, and never treat a same-scene pair as a positive control.
3. **Add a null-distribution step before any scoring is reported.** This is now a gate, not a
   refinement.
4. **Re-encoded material needs a third feature.** `video_2605` will not yield to either of
   these. Candidates: object-track correspondence (T4's centroid trajectory is a temporal
   signature that survives re-encoding), or transform-invariant keypoint matching.
5. **The clip families divide by encoding provenance, not by subject.** Original-encode
   families are tractable now. Edited families are a separate research problem.

## Cost

Two file pulls totalling 9.7 MB, and roughly four minutes of local compute. **Zero model calls
in the analysis itself.** The cost model in the founding plan holds: this work is compute, not
credits.
