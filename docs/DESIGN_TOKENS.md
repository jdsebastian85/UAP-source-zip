# Wave 0.2 — design tokens (cool instrument)

The token set for the restrained-instrument reskin. Cool, precise, dark-first, theme-aware.
This is the agreed system, not yet applied to the tool — Wave 1.2 wires it into
`site/investigator.html`. Values are chosen to keep the existing token architecture and the
existing chrome-vs-evidence class split, so applying it is a swap, not a rewrite.

## Principles this set encodes

- Depth and glass live on the chrome only. The evidence layer stays flat and opaque.
- Amber means one thing, a page that could not be read, and appears nowhere else.
- Four hues stay distinct at a glance: cool accent for anything interactive or human, a
  neutral slate for a machine-stated fact, amber for unreadable, red for an error or warning.
- Nothing in the metadata or evidence layer shrinks below 11px or drops below AA contrast.

## The variables

Light lives on bare `:root`; dark overrides in both the `prefers-color-scheme` block and the
`[data-theme="dark"]` block, so the toggle wins in either direction. Same structure the tool
already uses.

```css
:root{
  /* ground + surfaces */
  --bg:#f3f5f8; --panel:#ffffff; --panel-2:#eef1f5; --line:#d3dae3;
  --ink:#131822; --dim:#566277;
  /* interactive / human */
  --accent:#1f6f92; --accent-ink:#ffffff; --accent-soft:#e2eef4;
  /* evidence + state */
  --mark:#cfe6ee;               /* search highlight, cool, never amber */
  --warn:#b23a30; --warn-soft:#f6e4e2;
  /* machine coverage comb (T10) — reserved, used nowhere else */
  --comb-solid:#5f7f96;         /* shipped text layer */
  --comb-hollow:#9aa7b6;        /* below OCR floor — rendered as outline only */
  --comb-amber:#b3701f;         /* no text layer — the one amber in the system */
  /* human coverage comb — worked uses the interactive accent */
  --worked:var(--accent);
  /* shape */
  --radius:10px; --radius-sm:6px; --pad:14px;
  --sp-1:4px; --sp-2:8px; --sp-3:12px; --sp-4:16px; --sp-5:24px;
  /* type */
  --fs-xs:11px; --fs-sm:12.5px; --fs-base:15px; --fs-md:16px; --fs-lg:18px;
  --mono:13px/1.62 ui-monospace,SFMono-Regular,Menlo,monospace;
  /* chrome glass — CHROME ONLY */
  --glass-bg:rgba(255,255,255,.72); --glass-blur:12px;
  --glass-hair:rgba(19,24,34,.08);
  --shadow-1:0 1px 2px rgba(19,24,34,.10);
  --shadow-2:0 6px 20px rgba(19,24,34,.12);
}

@media (prefers-color-scheme:dark){
  :root:not([data-theme="light"]){
    --bg:#0e1116; --panel:#151a21; --panel-2:#1b212b; --line:#283040;
    --ink:#e6ebf2; --dim:#92a0b3;
    --accent:#4aa3c7; --accent-ink:#071016; --accent-soft:#12303c;
    --mark:#244a54;
    --warn:#e0776f; --warn-soft:#2a1a18;
    --comb-solid:#6f8ea3; --comb-hollow:#3a4653; --comb-amber:#d98a3a;
    --glass-bg:rgba(21,26,33,.72); --glass-hair:rgba(255,255,255,.06);
    --shadow-1:0 1px 2px rgba(0,0,0,.40); --shadow-2:0 8px 24px rgba(0,0,0,.50);
  }
}
:root[data-theme="dark"]{
  --bg:#0e1116; --panel:#151a21; --panel-2:#1b212b; --line:#283040;
  --ink:#e6ebf2; --dim:#92a0b3;
  --accent:#4aa3c7; --accent-ink:#071016; --accent-soft:#12303c;
  --mark:#244a54;
  --warn:#e0776f; --warn-soft:#2a1a18;
  --comb-solid:#6f8ea3; --comb-hollow:#3a4653; --comb-amber:#d98a3a;
  --glass-bg:rgba(21,26,33,.72); --glass-hair:rgba(255,255,255,.06);
  --shadow-1:0 1px 2px rgba(0,0,0,.40); --shadow-2:0 8px 24px rgba(0,0,0,.50);
}
```

## How the tokens map to the tool

- **Chrome gets glass and depth.** `header` and `nav` use `--glass-bg` with
  `backdrop-filter:blur(var(--glass-blur))`, a `--glass-hair` top highlight and `--shadow-1`.
  `.card` may use `--panel` with `--shadow-1`, or `--panel-2` when elevated. `button.act.primary`
  uses `--accent` with `--accent-ink` text.
- **The evidence layer stays flat.** `.pagetext`, `.pageimg`, `ul.cites`, `.conflegend` and
  `.warnbox` use `--panel` or `--warn-soft`, opaque, no blur, full contrast.
- **The machine comb (Wave 2) uses the reserved trio.** Solid tick fills `--comb-solid`;
  hollow tick is transparent with a `--comb-hollow` outline; amber tick fills `--comb-amber`
  and that token appears in no other rule. The human comb's worked tick keeps `--worked`
  (the accent), so the two rows never read as the same color.
- **Tap targets.** Comb ticks keep a small visual mark but carry a larger transparent hit
  area, so the second comb row in Wave 2 stays usable on a phone. Target at least a 24px
  square of touchable space per tick.

## Contrast, checked by role

- `--ink` on `--bg` clears AAA in both themes.
- `--dim` on `--bg` clears AA for body text in both themes.
- `--accent-ink` on `--accent` (button text) is high contrast in both themes.
- `--comb-solid`, `--comb-amber`, `--accent` and `--warn` are hue-distinct, so the combs and
  the warnings never collapse into one another for a red-green colorblind reader either —
  they differ in lightness and in blue-versus-orange, not in red-versus-green.
