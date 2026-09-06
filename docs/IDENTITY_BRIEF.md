# Wave 0.3 — identity brief

One page on how PURSUE presents itself, what it must not be mistaken for, and where the
reusable idea inside it lives. Written 2026-09-06, after the umbrella and palette decisions.
Companion to `docs/BRANDING_UX_PLAN.md`; `docs/DESIGN_TOKENS.md` holds the shipped values.

## What is being branded

A provenance instrument over a public-domain document release. Its entire value proposition
is that it tells you what it cannot tell you. Every identity decision below follows from
that: the mark has to read as an instrument, not as a campaign, a channel, or a claim.

## The name stays

PURSUE is anchored to the PURSUE Act and the release initiative, not coined. That external
anchor is a credibility asset — the name points at a public thing a reader can check, which
is the same move the corpus makes with every cite. The identity work dresses the name; it
does not rename it.

## The lockup

```
PURSUE
an anthro-tech.org project
```

- **PURSUE** in the tool's own voice: heavy weight, wide tracking (~0.30em), all caps. The
  investigator header already sets this tone and the palette preview renders it.
- **The affiliation line** sits beneath at small size in `--dim`, sentence case, never
  competing. It is an attribution, not a co-brand: anthro-tech.org vouches for PURSUE, and
  PURSUE keeps its own credibility.
- **One accent mark only.** A single orange terminal period after the wordmark
  (`PURSUE.`) is the whole of the brand's colour. Outside the chrome, orange is spent on
  one thing — a page nobody could read — so the mark must not spend it twice.
- **Never a tagline about UAP.** No "declassified", no "the truth about", no "revealed". The
  subject matter is the one thing that could make an archival instrument read as advocacy.

## What it must not be mistaken for

| | What it is | How PURSUE stays clear of it |
|---|---|---|
| **Lyriqal Digital Media** | Drone and video content brand. Angular mark, lime and purple. | Different palette entirely (warm charcoal, single orange), different letterforms, no angular geometry. Lyriqal's name now appears nowhere in this repo — it was removed from `CITATION.cff` and `LICENSE` on 2026-09-06. |
| **AI v.Human** | The thesis and its app. | PURSUE is not badged as an AI v.Human product and carries no app chrome. The relationship runs the other way: the thesis cites PURSUE as a worked example. |
| **A UAP disclosure site** | Advocacy, in either direction. | No believer tone and no debunker tone. The look is tone: flat evidence layer, published gaps, no imagery of craft or lights, no dark-conspiracy palette. |

The trade is deliberate and worth stating: keeping PURSUE under anthro-tech.org rather than
badging it as the AI v.Human app weakens the funnel to the app and protects the corpus's
credibility. The comb write-up below is the bridge that connects the two without coupling
their reputations.

## The separable idea, and where it lives

The reusable asset is not the corpus. It is the pattern the corpus demonstrates:

> **The Coverage Comb** — put the unreadable fraction on every result, so a reader can tell a
> true absence from a page nobody has read.

Any search interface over partially machine-readable scanned records reports hits without
reporting the unreadable denominator, which makes a null result and a blind spot look
identical. That is a general failure and the fix is general. In this corpus 1,719 of 8,661
pages carry no text layer — a null result over a 20% blind spot, presented as a null result,
is a false statement about the record.

**Name:** the Coverage Comb.
**Home:** written up under the AI v.Human thesis as a standalone UI pattern, with PURSUE as
the worked example — not as a PURSUE feature. `docs/T10_copresence.md` already says this in
its own words and is the source text.
**What travels with it:** the three-state tick (readable / poorly readable / unreadable), the
rule that the comb cannot be suppressed at any viewport, and the rule that a zero result and
its denominator ship together or neither ships. All three are enforced in this build and can
be cited as implemented rather than proposed.

**Still the owner's call:** the exact URL it lives at, and whether the write-up is published
under the AI v.Human thesis site or at `anthro-tech.org` with the thesis linking to it. The
decision that matters — that it is documented away from PURSUE — is already made.

## Attribution, as shipped

`CITATION.cff` names Joshua D. Sebastian with `anthro-tech.org` as affiliation; `LICENSE`
names him as copyright holder. The public site footer carries the holder, the affiliation, the
public-domain status of the underlying releases, the CC BY / MIT split and a paste-ready
citation string — because CC BY was chosen over CC0 specifically so the work is cited, and a
licence that asks for attribution while the page never says how to give it is asking for
nothing.

The middle initial is settled: **Joshua D. Sebastian**, cited as `Sebastian, J. D. (2026)`.
An ORCID is being registered; `CITATION.cff` carries a commented `orcid:` line showing exactly
where it goes, so adding it is a one-line edit.
