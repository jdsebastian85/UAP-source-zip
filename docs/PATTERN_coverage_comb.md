# The Coverage Comb

**A UI pattern for search over partially machine-readable archives.**
Put the unreadable fraction on every result, so a reader can tell a true absence from a page
nobody has read.

Written up as a standalone pattern. PURSUE is the worked example, not the subject — the
pattern applies to any corpus of scanned records where some fraction resists OCR.

---

## The failure it fixes

Search a scanned archive for a name. You get nothing back. What did you just learn?

Two very different things produce that same empty screen:

1. The name is genuinely not in the record.
2. The name is on a page the machine could not read, and the index has never seen it.

Almost every archive interface renders these identically. The reader is handed an absence
and left to assume it is the first kind, because nothing on screen suggests the second
exists. That is not a display shortcoming; it is the interface making a claim about the
world that its data cannot support.

The scale is not marginal. In the PURSUE corpus, **1,719 of 8,661 pages carry no text layer
at all** — just under 20%. A null result presented as a null result, over a blind spot that
size, is a false statement about the record.

## The pattern

Alongside every result, render one **tessera** — a single tile — per unit of the corpus in
scope. Each tessera carries one of three states:

| State | Means | Rendering |
|---|---|---|
| **Readable** | the machine read this unit | filled, neutral |
| **Poorly readable** | text exists but scored below the legibility floor | outline only |
| **Unreadable** | no text was ever extracted | filled, **the one reserved hue** |

The strip they form is the comb. The metaphor is exact rather than decorative: the corpus is
a mosaic assembled from fragments, and a mosaic with tiles missing announces its own
incompleteness without needing a legend. That is the whole idea. A reader who sees a third
of the tesserae in the reserved hue does not need to be told the result is unreliable.

## The rules that make it work

These are not styling preferences. Drop any one and the pattern stops making its claim.

**1. Scope includes the unreadable units.** The denominator is every unit where the answer
*could* have been, not every unit the machine managed to read. Reporting coverage against the
readable subset quietly shrinks the denominator and restores the original problem.

**2. A zero result and its denominator ship together, or neither ships.** An absence
statement rendered without its comb is the exact failure the pattern exists to prevent, so it
must be unbuildable rather than discouraged. In PURSUE this is enforced at render: a panel
found without its comb replaces itself with a failure notice.

**3. The comb cannot be suppressed.** Not behind a collapse control, not behind a media
query, not dropped at any viewport width. On a narrow screen it subsamples at a stated
stride and says so. It never hides — the small screen is where a reader is *most* likely to
accept an empty result at face value.

**4. One hue, one meaning.** The unreadable state gets a saturated colour reserved across the
entire interface. Nothing else may use it. This is the rule most often broken by accident:
the moment a brand accent, a warning state or a hover uses the same family, the alarm becomes
decoration. PURSUE hit this directly — an orange brand accent collided with the reserved hue,
and the resolution was to keep the rule and move the accent's meaning, not to relax it.

**5. It is a coverage measure, not a quality score.** The comb says *whether* a unit was read,
never how good the content is or how relevant it might be. Conflating the two turns an honest
instrument into a ranking signal.

## Implementation notes

Measured on the PURSUE build, so these are costs rather than estimates.

**Run-length encoding, not one character per unit.** Readability clusters — scans fail in
runs, not at random — so an RLE string per document (`R41,L3,N12,R29`) compresses hard. All
211 releases and 8,661 pages cost **7,929 bytes** embedded, against a 17.8 KB budget set by
a one-character-per-page estimate.

**Gate the encoding against itself.** Every run-string must expand back to the state sequence
it was built from, cover exactly the unit count the source holds, and match the published
totals. In PURSUE all three are fatal at build time. The third matters most: those totals also
appear in the citation record and the README, so drift means a published claim has gone stale
rather than merely an internal mismatch.

**Subsample with a fixed, stated stride.** Past roughly 500 tesserae, sample at a fixed
interval and state it, along with the fact that the counts are over the whole scope and not
the sample. Never re-normalise the counts to the sample.

**Choose the reserved hue for the colourblind case.** The three states must separate on
lightness and on a blue-versus-orange axis, not red-versus-green. Outline-only for the middle
state does useful work here: it differs in form as well as colour.

**Give each tessera a hit area larger than its mark.** A tessera is a few pixels wide by
design — density is the point — so the touchable region has to exceed the visual one.

## Worked example: PURSUE

An index over a declassified UAP document release: 211 releases, 8,661 pages.

- **6,124** pages carry a publisher's text layer
- **818** carry one below the legibility floor
- **1,719** carry no text layer at all

Selecting a subject renders the comb across every page of every release where that subject
appears — unreadable pages included, because that is the set where a co-mention could have
existed. For one person in the corpus the scope is 629 pages across four releases, of which
**130 could not be read**. The panel reports partners against all 629, and the comb shows why
the answer is provisional. A reader can see, before reading a word, that roughly one page in
five of the relevant record has never been read by anything.

Live: [jdsebastian85.github.io/pursue-corpus/investigate.html](https://jdsebastian85.github.io/pursue-corpus/investigate.html)

## Where else it applies

Anywhere a corpus is searched but only partly machine-readable:

- **FOIA and declassification releases** — the closest analogue, and the case where the
  epistemics matter most, because absence is routinely read as evidence.
- **E-discovery** — a privilege or responsiveness review over scanned exhibits, where "not
  found" carries procedural weight and an unreported blind spot is a defensible-process
  problem.
- **Newsroom document dumps** — leaked or released archives with no time to OCR everything,
  where a reporter's null result becomes a published claim.
- **Academic and genealogical archives** — handwritten and degraded material, where the
  unreadable fraction is often the majority and is almost never surfaced.

In every one of these, the current default is to report hits and stay silent about the
denominator. The comb is a small piece of interface that makes the silence impossible.

---

*The Coverage Comb is documented here as a reusable pattern, separate from the corpus that
demonstrates it. Implementation: `docs/T10_copresence.md` is the governing spec;
`site/investigator.html` is the working build.*
