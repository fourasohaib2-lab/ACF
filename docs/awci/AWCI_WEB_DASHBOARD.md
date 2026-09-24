# AWCI Web Dashboard

**Date:** 2026-09-24. Documents the real Next.js/React/TypeScript
dashboard at the repository root (`app/`, `components/dashboard/`,
`lib/`) — genuinely distinct from the PySide6 desktop GUI documented
elsewhere in `docs/awci/`/`docs/architecture/`. Originally generated
by v0.dev on branch `v0/awci-dashboard-reference` with 100% static/
simulated data (`lib/data.ts`, still present but unreferenced by any
component — kept per this repo's "never remove modules unless
explicitly requested" rule), then wired panel-by-panel to the real
AWCI FastAPI backend (`src/awci/api/`) across this session. Every
number the running dashboard displays is a real backend result;
`lib/data.ts`'s mocks are dead code, not a fallback path.

## Running it

Two real processes, no others:

```bash
# 1. Backend (from the repo root, with the project's venv active)
.venv/bin/python -m uvicorn awci.api.app:create_app --factory --host 127.0.0.1 --port 8010

# 2. Frontend (a separate terminal)
pnpm install   # first time only
pnpm dev       # or: pnpm build && pnpm start for a production build
```

`NEXT_PUBLIC_API_URL` (see `.env.example`) points the frontend at the
backend; defaults to `http://127.0.0.1:8010` when unset. The backend's
`CORSMiddleware` (`src/awci/api/app.py`) allows `http://localhost:3000`
and `http://127.0.0.1:3000` by default — override via
`AWCI_API_CORS_ORIGINS` (comma-separated) for another real deployment
origin.

## Architecture

```
app/page.tsx
└─ ComplexityFieldProvider          (lib/hooks/use-complexity-field.tsx)
   └─ RouteWeatherProvider          (lib/hooks/use-route-weather.tsx)
      ├─ DashboardHeader            (real model name + UTC clock)
      ├─ ControlBar                 (route / model / grid-resolution selectors)
      ├─ KpiBar                     (mean/max AWCI, affected area, forecast confidence)
      ├─ GlobalMap / RegionalMap    (Leaflet + georaster-layer-for-leaflet)
      ├─ VerticalCrossSection       (own fetch: GET /complexity/vertical-profile)
      ├─ RadarComplexity            (5 real AWCICalculator physical modules)
      ├─ RouteProfile               (AWCI sampled along the real route)
      ├─ RiskPanel                  (real per-station METAR/ceiling)
      └─ FooterBar                  (real data sources + real grid spacing)
```

`ComplexityFieldProvider` and `RouteWeatherProvider` are the 2 shared
data sources — each makes exactly one real backend call per
route/model/resolution change and every panel below reads from that
same fetch (`useComplexityField()` / `useRouteWeather()`), instead of
each panel re-triggering its own redundant physics run.
`VerticalCrossSection` is the one panel with its own fetch
(`GET /complexity/vertical-profile`), because its sample point (the
route's own great-circle midpoint) and 3D-volume cost are distinct
from the 2D field the other panels share.

## Real endpoints each panel depends on (`lib/api.ts`)

| Panel | Endpoint | Real backend engine |
|---|---|---|
| KpiBar, RadarComplexity, GlobalMap, RegionalMap, FooterBar, DashboardHeader | `GET /complexity/field` | `awci.complexity.spatial_field.compute_real_complexity_field()` |
| VerticalCrossSection | `GET /complexity/vertical-profile` | `awci.complexity.vertical_field.compute_real_complexity_volume()` + `vertical_profile_at_point()` |
| RouteProfile, RiskPanel, ControlBar's route markers | `GET /flights/route-weather` | `awci.flight.route_weather.build_route_weather_briefing()` |
| ControlBar's airport selects | `GET /airports` | `awci.knowledge.airports.airport_database.AirportDatabase.all_airport_infos()` |

`lib/api.ts`'s exported TypeScript interfaces mirror the real Python
dataclass each route returns field-for-field (verified against the
live server's actual JSON, not written from the Python source alone —
see that file's own module docstring). No endpoint synthesizes a
fallback on failure: a non-2xx response throws `ApiError`, and
backend dataclasses that carry their own `is_real_data`/`status`
field are passed through unchanged so the UI renders an honest error/
empty state.

## The map stack

`components/dashboard/complexity-map.tsx` (Leaflet, dynamically
imported client-side only — Leaflet cannot run during Next.js's SSR
pass): OpenStreetMap tiles (CSS-filtered dark, `.map-tiles-dark`),
`georaster-layer-for-leaflet` rendering the real field via
`lib/build-georaster.ts` (a real `GeoRaster` built from
`ComplexityField`, `null`/non-finite cells become the real
`noDataValue`, never a fabricated 0), the real route as a polyline
with real departure/arrival markers, and a live cursor readout
(`sampleFieldAt()`, `lib/complexity-stats.ts`) - a real nearest-grid
lookup, the same convention the backend's own
`vertical_profile_at_point()` uses.

MapLibre GL JS + deck.gl were evaluated (2026-09-24, in response to a
detailed architecture proposal from the user) as the eventual right
choice for large-scale raster/vector rendering (millions of points, a
full-resolution AROME grid, animated multi-model comparison) — not
adopted now because the dashboard's current real data volume (a few
thousand grid points, one route, a handful of markers) does not
justify it, and the explicit user decision was to finish wiring the
existing Next.js/Leaflet dashboard first rather than rewrite it.
Revisit if/when a real feature needs it (e.g. serving the model's
true native resolution instead of a coarse override).

## Real, disclosed current limitations

- **Convective/Microphysical/Topographic modules read 0** under the
  dashboard's default field request: `compute_real_complexity_field()`
  only feeds `AWCICalculator` temperature/wind/humidity/pressure by
  default — CAPE/CIN/wind-shear require the real, more expensive
  `compute_convective_energy=True`/`compute_wind_shear=True` opt-ins
  (see that function's own docstring), not requested by
  `src/awci/api/routes/complexity.py`'s `/field` route today. This is
  correct, not a bug — verified live (task #8's own screenshot
  comparison, `git log` on `feat(web): wire GlobalMap...`).
- **No forecast time-stepping**: `/complexity/field` and
  `/complexity/vertical-profile` are single real physics snapshots
  (`CoupledEarthSolver` run once per request) — there is no real
  animated timeline to scrub (the original v0 mockup's fake `+12h`
  scrubber on RegionalMap was removed for this reason, see the
  `feat(web): wire GlobalMap...` commit).
- **Grid resolution is a manual override**, not each model's true
  native grid (`ControlBar`'s 3 presets — Coarse 12×24/Standard
  24×48/Fine 48×96 — are real but coarser than AROME's real 90×180
  `MODEL_CONFIGS` entry, chosen for interactive response time; see
  `control-bar.tsx`'s own measured-cost comment).
- **Single route/model/resolution at a time** — no multi-route or
  multi-model-comparison view yet (the ChatGPT-proposed "Model
  Comparison" module in the user's 2026-09-24 architecture message is
  not built).
- **`lib/data.ts` and `components/heatmap-canvas.tsx`** (the original
  v0-generated mock data and its procedural pseudo-random canvas) are
  unreferenced dead code, kept rather than deleted per this project's
  "never remove modules unless explicitly requested" rule.

## Tests

`tests/test_awci_api.py` covers every backend route the dashboard
calls (FastAPI `TestClient`, real network-calling connectors
monkeypatched per `tests/test_awci_observations_hub.py`'s own
established convention) — 21 tests as of this writing. The frontend
has no automated test suite yet (`vitest`/Playwright component tests
were not set up this session); every frontend change in this session
was instead verified by building (`pnpm build`) and exercising the
real running app in a real headless Chromium session (Playwright),
screenshotting the actual rendered result against the reference
mockup (`docs/reference/awci_dashboard_reference.png`) rather than
assuming the code was correct.
