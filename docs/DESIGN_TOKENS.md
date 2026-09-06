# Wave 0.2 — design tokens (orange instrument, option B)

The token set for the restrained-instrument reskin. Warm charcoal ground, one orange accent,
dark-first, theme-aware. **Shipped into `site/investigator.html` in Wave 1.2 (commit
`226eb60`); this file documents what is in the build, not a proposal.** Rendered preview with
the alternatives that were rejected: `docs/tokens_preview_orange.html`.

An earlier draft of this file proposed a cool steel-cyan set. The owner chose orange from
three reference landing pages, which forced the decision recorded below. The cool set is
superseded and is not in the build.

## The rule this set is built around

The owner locked a constraint before the palette existed: **one hue is reserved to mean "a
page that could not be read," and appears nowhere else.** Choosing orange as the brand accent
collided with it head-on — at 11px a comb tick cannot be *orange, but not that orange*.

Three ways out were rendered and compared side by side. The decision was **option B: keep the
rule, swap the hue.**

> **Inside the evidence layer, the accent hue means a page that could not be read, and
> nothing else does.** The chrome may use the accent freely — nav, buttons, links, pills.
> The evidence layer holds exactly one saturated colour and that colour is the gap.

Two consequences that are easy to get wrong later:

1. **The human comb's worked tick is not the accent.** It was, before this decision. It is now
   `--worked`, a bone neutral. If it stayed orange, the human row and the machine row's
   unreadable state would be the same colour, and Wave 2 stacks those two rows adjacent.
2. **The search highlight is not warm.** `--mark` is a cool wash in both themes, deliberately,
   so a highlighted run of text never reads as an unreadable-page signal.

## Principles

- Depth and glass live on the chrome only. The evidence layer stays flat and opaque.
- Four roles stay hue-distinct: accent (interactive, and unreadable *in the evidence layer*),
  steel (a machine-stated readable fact), bone (a human-stated fact), red (an error).
- Nothing in the metadata or evidence layer shrinks below 10.5px or drops below AA.

## The variables

Light on bare `:root`; dark overrides in both the `prefers-color-scheme` block and the
`[data-theme="dark"]` block, so the toggle wins in either direction — the structure the tool
already used.

```css
:root{
  --bg:#f6f4f1; --panel:#fff; --panel-2:#efebe6; --line:#ddd6cd;
  --ink:#171412; --dim:#6b625a;
  --accent:#b4560d; --accent-ink:#fff; --accent-soft:#f7e7d8;
  --mark:#cfe3ea; --warn:#a8322a;
  --comb-solid:#5f7f96;    /* machine: page has a text layer */
  --comb-hollow:#a9a096;   /* machine: below the 0.90 page-legibility proxy */
  --comb-unread:#c25e0a;   /* machine: NO text layer — the one saturated hue */
  --worked:#7a6b5d;        /* human: a reader has worked this page */
  --radius:10px; --pad:14px;
  --glass-bg:rgba(255,255,255,.72); --glass-blur:12px;
  --glass-hair:rgba(23,20,18,.07);
  --shadow-1:0 1px 2px rgba(23,20,18,.07);
}
/* dark — in both the media block and [data-theme="dark"] */
--bg:#100e0c; --panel:#191613; --panel-2:#221e1a; --line:#332c26;
--ink:#efeae4; --dim:#9a9086;
--accent:#f57c1f; --accent-ink:#1a0f05; --accent-soft:#2e1c0d;
--mark:#2b3f49; --warn:#e8695f;
--comb-solid:#7f96a8; --comb-hollow:#4a423a; --comb-unread:#f57c1f;
--worked:#c8bdb2;
--glass-bg:rgba(25,22,19,.66); --glass-hair:rgba(255,255,255,.07);
--shadow-1:0 1px 2px rgba(0,0,0,.40);
```

## How the tokens map to the tool

- **Chrome gets glass and depth.** `header` uses `--glass-bg` with
  `backdrop-filter:blur(var(--glass-blur))`, a `--glass-hair` inset highlight and
  `--shadow-1`, with an `@supports not (backdrop-filter)` fallback to an opaque bar. `.card`
  takes `--panel` plus `--shadow-1`. `button.act.primary` is `--accent` with `--accent-ink`.
- **The evidence layer stays flat.** `.pagetext`, `.pageimg`, `ul.cites`, `.conflegend`,
  `.warnbox`, `.unclear` and `.redblk` are opaque, unblurred, full contrast.
- **The combs use the reserved four and nothing else uses them.** Machine row (Wave 2): solid
  fills `--comb-solid`, hollow is transparent with a `--comb-hollow` outline, unreadable fills
  `--comb-unread`. Human row: worked fills `--worked`; a starred tick takes an `--ink` inset
  ring rather than a fill, so star and coverage never compete for the same channel.
- **Tap targets.** Ticks keep an 11×17px visual mark and carry a hit area 4px larger on each
  vertical edge and 3px on each horizontal, with the comb's row gap widened to 9px so hit
  areas do not overlap between rows. Final sizing is a Wave 2 decision, once the machine row
  is actually stacked above the human one.

## Contrast, by role

- `--ink` on `--bg` clears AAA in both themes.
- `--dim` on `--bg` clears AA for body text in both themes.
- `--accent-ink` on `--accent` is high contrast in both themes.
- `--comb-unread` against `--comb-solid` and `--worked` differs in both hue and lightness, so
  the three comb states stay separable for a red-green colourblind reader: the split is
  orange-versus-steel-versus-bone, not red-versus-green.
- `--warn` (red) and `--comb-unread` (orange) are never adjacent — `--warn` appears on pill
  borders and warn boxes, `--comb-unread` only inside a comb.
