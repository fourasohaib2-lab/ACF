---
name: acf-dashboard-design
description: Design-system rules for ACF's PySide6/matplotlib GUI (ESOC chrome + AWCI dashboard) — the real token system, what Qt/QSS can and cannot actually do, and the matplotlib-chart-must-match-chrome convention. Use before any "modernize"/"improve the UI"/"make it look better" request touching src/acf/gui/, and before writing any new panel or QSS.
---

# ACF/AWCI dashboard design system

This is a **desktop PySide6/matplotlib application**, not a web app — many
"modern dashboard" techniques (CSS blur, arbitrary box-shadow, DOM
transitions) do not translate literally. This skill says what the real,
already-built system offers and how to extend it correctly.

## 1. There is already a real token system — use it, don't invent a new one

`src/acf/gui/theme_tokens.py` (`_Tokens` dataclass, `TOKENS` instance) is
the **single source of truth** for color/spacing/radius/typography, shared
by ESOC's chrome (`resources/themes/{dark,light}.qss`) and the AWCI
dashboard. It already has:

- Surfaces: `bg_root` → `bg_surface` → `bg_surface_alt` → `bg_card`
  (darkest to lightest, use in that role order for depth).
- Text: `text_primary`/`text_secondary`/`text_muted`.
- Accents: `accent_primary`(+`_hover`)/`accent_secondary`/`accent_real`
  (marks a genuine-data affordance, e.g. Real Physics/Real Archive, as
  visually distinct from demo/synthetic — use it on purpose, not
  decoratively) + `accent_gradient_css()` for a real 2-stop gradient fill.
- Status: `success`/`warning`/`danger`.
- Geometry: `radius_sm/md/lg`, `spacing_xs/sm/md/lg/xl` (4/8/12/16/24).
- Typography: `font_family`, `font_size_xs/sm/md/lg/xl`.
- Helpers: `label_style()`, `dashboard_stylesheet()`, `card_frame_style()`,
  `accent_gradient_css()`, `apply_elevation()`.

**Before adding a new color/spacing/size value anywhere in `acf.gui`,
check whether an existing token already means it.** A hardcoded hex
literal in a panel file is drift, not a style choice — this repo has a
documented history of exactly this drift (two incompatible dark palettes
before `theme_tokens.py` existed; a second wave found in 5 of 7 matplotlib
chart panels in `gui/dashboard/awci_*.py`, closed 2026-09-11).

## 2. Qt/QSS real capabilities (know what's actually available)

- **Real elevation/shadow exists**: `theme_tokens.apply_elevation(widget,
  blur_radius, y_offset, opacity)` attaches a real
  `QGraphicsDropShadowEffect` — a genuine blurred drop shadow, not a
  border simulation. Already applied to the 7 main AWCI panels
  (`awci_dashboard.py`, search `apply_elevation(`). Use it for any new
  card-like panel that should read as "floating" above the root
  background.
- **Real hover/pressed/disabled states**: QSS supports `:hover`,
  `:pressed`, `:disabled`, `:selected` pseudo-states — already used
  throughout `dashboard_stylesheet()` (buttons, sliders, scrollbars,
  tabs, menus) and per-widget click patterns (`_RiskRow`, `_ComponentRow`
  — a `QFrame` with `mousePressEvent()`/hover styling, not a
  `QPushButton`, when a custom row layout is needed).
- **What QSS does NOT have**: no arbitrary CSS `box-shadow` (use
  `apply_elevation()` instead), no `blur()`/backdrop-filter, no CSS
  transitions/keyframe animation (use `QPropertyAnimation` if a real
  animated transition is worth the complexity — most of this dashboard
  deliberately does not, favoring instant, predictable state changes).
- **Gradients**: `qlineargradient` only, normalized `[0,1]` coordinates,
  not a CSS angle — use `accent_gradient_css()` rather than hand-rolling
  the QSS syntax.

## 3. Matplotlib charts must match the Qt chrome — they don't automatically

Matplotlib figures are painted independently of QSS; a chart's own
`facecolor`/text/spine colors need to be set explicitly from `TOKENS` or
they silently drift to whatever palette was hardcoded when that panel was
written. **Established, precedented mapping** (from
`awci_evolution_chart.py`/`awci_model_spread_chart.py`, the two panels
built already-tokenized — follow this exact pattern in any new or edited
chart panel):

```python
from acf.gui.theme_tokens import TOKENS

self.figure = plt.figure(facecolor=TOKENS.bg_root)
self.axis.set_facecolor(TOKENS.bg_card)          # plot area, one shade up
self.axis.set_title(..., color=TOKENS.text_primary)
self.axis.set_xlabel(/set_ylabel(/tick_params(..., color/colors=TOKENS.text_secondary)
for spine in self.axis.spines.values():
    spine.set_color(TOKENS.border)
# empty/no-data state:
self.axis.text(0.5, 0.5, "No real <thing> yet", transform=self.axis.transAxes,
                ha="center", va="center", color=TOKENS.text_muted, fontsize=9)
```

**Exception — real data-series accents, not chrome.** A chart's own data
curve/fill/icon color (e.g. the radar's orange fill, the cross-section's
icing/turbulence glyph colors) is a deliberate visual choice, often
matching `docs/reference/*.jpg`'s own reference mockup — don't fold those
into chrome tokens just because they're also a hex literal. Only unify
colors playing a chrome role (background, border, generic text, grid).

## 4. Pixel-fidelity vs. modernization — know which one you're doing

Several AWCI panels were built to match `docs/reference/
awci_dashboard_reference.jpg` **pixel-for-pixel** (an explicit master-
prompt priority — see `docs/awci/AWCI_IMPLEMENTATION_STATUS.md`'s
"Design decisions"). A request to "modernize" or "improve" the UI is a
real, deliberate departure from that priority, not a bug fix — confirm
scope with the user (layout/structure preserved vs. genuinely open) before
changing anything a reference-fidelity test
(`tests/test_awci_map_panel_reference_fidelity.py` and friends) asserts
on.

## 5. Empty/loading/error states — the existing convention

This codebase already has a real, if inconsistent, convention: `⏳ <verb>ing
…` for async status labels (`awci_dashboard.py`,
`awci_messages_panel.py`), a dedicated `_draw_empty()` method for charts
with no data yet (`awci_evolution_chart.py`, `awci_model_spread_chart.py`),
and honest "not available — no real X computed yet" labels in detail
dialogs rather than a blank/misleading widget. When adding a new panel
that can legitimately have no data, follow this pattern — and be careful
that an uninitialized numeric widget (e.g. a radar/gauge defaulting all
values to 0) doesn't read as a real "zero" measurement instead of "no
data yet": prefer an explicit empty-state message over a populated-looking
zero.
