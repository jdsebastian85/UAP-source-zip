# Wave 0.1 — investigator current-state audit

Source read: `site/investigator.html` (the template; `investigate.html` is the built output).
This is the note the plan's Wave 0.1 asked for: what to keep, and where the styling fights
legibility. Grounded in the actual CSS, not assumptions.

## The good news

The tool is already built on CSS variables and is already theme-aware done correctly: a bare
`:root` light palette, a `prefers-color-scheme` dark block guarded with
`:not([data-theme="light"])`, and a `[data-theme="dark"]` block so the toggle wins both ways.
The reskin is therefore a token swap plus selective chrome treatment, not a rewrite. That is
the single most important finding: we change values, we do not restructure.

The class split we need for "glass on the chrome only" already exists in the markup:

- **Chrome** (safe to give depth, translucency, glass): `header`, `nav`, the search input,
  `.card`, `.pill`, `button.act`, `footer`, the theme toggle.
- **Evidence layer** (stays flat, opaque, high contrast, never glass): `.pagetext` (the
  monospace transcript), `.comb` (coverage ticks), `.unclear` (dimmed sub-floor words),
  `.redblk` (redaction blocks), `mark` (search highlight), `.pageimg` (the scan),
  `ul.cites`, `.conflegend`, and `.warnbox` (the honest error and absence states).

Because the split is already clean in the code, the discipline is enforceable rather than
aspirational.

## Current palette, and the mood it sets

Light: warm off-white ground (`#fbfaf8`), sienna accent (`#8a4b2a`), a manila highlight
(`#fde8b8`), dark-red warn (`#8a2a2a`). Dark: near-black warm ground (`#16151a`), a tan accent
(`#d9926a`). The present identity is **warm archival** — paper, folders, ink. It reads as a
records archive, not as anything sci-fi, which already serves credibility.

That matters for the restrained-instrument direction, because "instrument" usually pulls
cool and technical — slate, near-black, a single cool accent — which is a real mood change
away from the warm archive it is today. That choice is the one thing the token draft needs
settled first, and it is below in the open decision.

## What to keep, without exception

- The token architecture and the theme-aware structure. Extend, do not replace.
- Every honest-state element: `.warnbox`, `.unclear`, `.redblk`, the "no shipped text" and
  "no image host configured" messages. This is the credibility layer. It stays flat and high
  contrast in both themes.
- The coverage-comb semantics and the stated-not-inferred discipline.
- The accessibility already present: `aria-selected` on tabs, `aria-pressed` on worked
  buttons, `alt` text on scans and triage strips, `viewport-fit=cover` with safe-area insets.

## Where styling fights legibility, phone first

1. **Comb tap targets are too small.** Ticks are 11px wide by 17px tall. That is well under a
   comfortable touch target, and it gets worse in Wave 2 when the T10 machine-readability comb
   lands as a second row directly above the human comb. Two rows of tiny ticks on a phone is
   the legibility risk in this whole tool. The reskin should grow the hit area even if the
   visual tick stays small.
2. **Amber is not yet spoken for, and must be reserved now.** There is no amber anywhere in
   the current CSS. The T10 spec reserves amber to mean exactly one thing, a page that could
   not be read. So the new token set must add a dedicated amber that collides with nothing —
   not the accent, not the dark-red warn — and the machine comb's three states (solid, hollow,
   amber) need three reserved values that are distinct at a glance and pass contrast in both
   themes.
3. **One accent carries many meanings.** Links, the active tab, worked ticks, primary buttons
   and "marked" pills all use `--accent`. That is fine today, but once the machine comb adds
   its own three states we must make sure comb color never reads as "accent" or "warn", or the
   rows stop being legible as separate claims.
4. **Small type has no room to shrink.** Pills at 10.5px and metadata at 12px are near the
   floor already. A glass or low-contrast treatment applied here would break them, which is
   the concrete reason the evidence and metadata layers stay flat.
5. **The two combs will sit adjacent with no separation designed yet.** The whole point of
   T10 is the disagreement between the machine row and the human row. They need distinct labels
   and deliberate spacing so that disagreement reads, rather than looking like one noisy strip.

## Handoff into Wave 0.2

The token draft is mechanical once the mood is chosen: background scale, one or two accents,
the three reserved comb states, a type scale, spacing, and the glass treatment values for the
chrome only. The one decision that gates it is warm-archival evolution versus cool instrument.
