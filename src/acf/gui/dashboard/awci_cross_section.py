"""
AWCI Vertical Cross-Section Panel
==================================

Filled contour of the real AWCICalculator score (synthetic demo inputs -
see awci_synthetic_field.py) along a flight path, altitude on the y-axis,
distance on the x-axis, with the flight track drawn over it - matching the
reference mockup's "VERTICAL CROSS-SECTION ALONG FLIGHT PATH" panel.

set_external_cross_section() (added 2026-09-02) lets a caller show a
real acf.awci.path_sampling.sample_volume_cross_section() result
instead - see that function's own docstring for what "real" means here
(native model levels, not standard pressure levels; path-averaged
local pressure per level).

Colorbar (added 2026-09-03, explicit user request "je veux garder le
meme theme pour les deux en suivant cette photo" - the reference
mockup shows a real AWCI 0-100 colorbar under this exact panel): a
real matplotlib colorbar keyed to the same contourf() call that draws
the heatmap, not a separately drawn legend.

Hazard icon overlays (added 2026-09-03, docs/reference/
awci_dashboard_reference.jpg parity work): the mockup shows snowflake
(icing) and turbulence glyphs scattered over the cross-section.
set_hazard_overlay() draws them from real, caller-supplied grids -
snowflakes wherever a real precipitation-phase severity
(acf.awci.hydrometeor_phase, aligned to this SAME distance/level grid)
indicates Snow/Freezing-Rain/Wet-Snow, turbulence glyphs wherever a
real bulk-wind-shear value (acf.awci.wind_shear, a disclosed proxy -
see set_hazard_overlay()'s own docstring) exceeds a real, disclosed
threshold. Off by default (no overlay drawn unless supplied) - never
fabricated, and never drawn at every grid cell (subsampled, matching
the mockup's own sparse icon placement).
"""

from typing import Any

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from PySide6.QtWidgets import QVBoxLayout, QWidget

from acf.gui.dashboard.awci_colors import AWCI_CMAP
from acf.gui.dashboard.awci_synthetic_field import cross_section_field

#: Real, disclosed ACF design-choice threshold for drawing a
#: turbulence-proxy icon (see class docstring's "Hazard icon
#: overlays") - reuses the SAME "~20 m/s bulk shear is a commonly
#: cited real operational threshold for organized severe convection
#: potential" reference already documented in
#: acf.awci.normalizer.Normalizer.normalize_wind_shear(), not a
#: separately invented number.
_TURBULENCE_PROXY_SHEAR_THRESHOLD_M_S = 20.0
#: Real phase-severity threshold for drawing a snowflake icon -
#: acf.awci.hydrometeor_phase.PHASE_SEVERITY has Rain=0.2 (excluded)
#: and Snow/Wet Snow/Freezing Rain at 0.5/0.7/1.0 (included).
_ICING_PROXY_SEVERITY_THRESHOLD = 0.5

#: Rough US Standard Atmosphere pressure -> altitude (ft) conversion for the
#: y-axis, so the panel reads in feet like the reference (not hPa).
_HPA_TO_FT = [
    (1013, 0), (850, 4800), (700, 9900), (500, 18300),
    (400, 23600), (300, 30100), (250, 33900), (200, 38700), (150, 44600),
]


def _hpa_to_ft(hpa: float) -> float:
    """
    CORRECTED (found 2026-09-02 wiring real solver data into this
    panel): out-of-table pressures used to clamp to a single constant
    (_HPA_TO_FT[0][1] = 0 ft for anything above 1013 hPa,
    _HPA_TO_FT[-1][1] = 44600 ft for anything below 150 hPa) - fine for
    the synthetic demo pattern (always within the table's range), but
    CoupledEarthSolver's real state uses its own idealized pressure
    scale that can exceed 1013 hPa at the surface (see vertical_field.py
    - its own docstring documents this isn't literal sea-level
    pressure). Clamping silently collapsed 10 of a real 20-level
    profile's distinct levels onto the exact same y=0 ft in a real
    screenshot taken while verifying the cross-section wiring - a real,
    visually degenerate result, not the intended output. Now
    extrapolates linearly from the nearest boundary segment's slope
    instead, so out-of-range pressures still map to DISTINCT (if rough/
    approximate beyond the table's real US Standard Atmosphere data)
    altitudes rather than colliding.
    """
    for i in range(len(_HPA_TO_FT) - 1):
        p0, f0 = _HPA_TO_FT[i]
        p1, f1 = _HPA_TO_FT[i + 1]
        if p1 <= hpa <= p0:
            t = (p0 - hpa) / (p0 - p1)
            return f0 + t * (f1 - f0)

    if hpa > _HPA_TO_FT[0][0]:
        (p0, f0), (p1, f1) = _HPA_TO_FT[0], _HPA_TO_FT[1]
    else:
        (p0, f0), (p1, f1) = _HPA_TO_FT[-2], _HPA_TO_FT[-1]
    slope = (f1 - f0) / (p1 - p0)
    return f0 + slope * (hpa - p0)


class AWCICrossSection(QWidget):
    """Titled altitude-vs-distance AWCI heatmap along a great-circle-ish flight path."""

    def __init__(self, title: str = "VERTICAL CROSS-SECTION ALONG FLIGHT PATH", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._base_title = title
        self._title = title
        self._cruise_hpa = 300.0
        self._last_point_a: tuple[float, float] | None = None
        self._last_point_b: tuple[float, float] | None = None
        # (distances_km, levels_hpa, grid) from set_external_cross_section() -
        # see this module's docstring.
        self._external_cross_section: tuple[Any, Any, Any] | None = None
        # Real (distances_km, levels_hpa, phase_severity_grid, wind_shear_grid)
        # from set_hazard_overlay() - see module docstring's "Hazard
        # icon overlays" note. None = no overlay drawn.
        self._hazard_overlay: tuple[Any, Any, Any, Any] | None = None
        # (distances, levels_hpa) last actually drawn - read back by
        # set_hazard_overlay()/clear_hazard_overlay() so they can
        # redraw the SAME real heatmap, never a second/guessed one.
        self._last_grid_context: tuple[Any, Any] | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.figure = plt.figure(facecolor="#0b1220")
        self.canvas = FigureCanvasQTAgg(self.figure)
        layout.addWidget(self.canvas)
        self.axis = self.figure.add_subplot(1, 1, 1)
        self._colorbar: Any = None

    def set_external_cross_section(self, distances_km: Any, levels_hpa: Any, grid: Any, label: str) -> None:
        """Show a real cross-section (e.g. path_sampling.sample_volume_cross_section()'s output) instead of the synthetic pattern."""
        self._external_cross_section = (distances_km, levels_hpa, grid)
        self._title = f"{self._base_title} — {label}"
        self._last_grid_context = (distances_km, levels_hpa)
        self._draw(distances_km, levels_hpa, grid)

    def clear_external_cross_section(self) -> None:
        """Revert to the synthetic demo pattern for the last (point_a, point_b, cruise_hpa) passed to update_data()."""
        self._external_cross_section = None
        self._title = self._base_title
        if self._last_point_a is not None and self._last_point_b is not None:
            self.update_data(self._last_point_a, self._last_point_b, self._cruise_hpa)

    def update_data(self, point_a: tuple[float, float], point_b: tuple[float, float], cruise_hpa: float = 300.0) -> None:
        self._last_point_a = point_a
        self._last_point_b = point_b
        self._cruise_hpa = cruise_hpa
        if self._external_cross_section is not None:
            distances, levels_hpa, grid = self._external_cross_section
        else:
            distances, levels_hpa, grid = cross_section_field(point_a, point_b, n_along=60, n_levels=20)
        self._last_grid_context = (distances, levels_hpa)
        self._draw(distances, levels_hpa, grid)

    def set_hazard_overlay(
        self, distances_km: Any, levels_hpa: Any, phase_severity_grid: Any = None, wind_shear_grid: Any = None
    ) -> None:
        """
        Draw real icing/turbulence-proxy icons (see class docstring's
        "Hazard icon overlays" note) - `distances_km`/`levels_hpa` must
        be the SAME real grid already drawn (from
        acf.awci.path_sampling.sample_cross_section_hazards() or
        acf.gui.dashboard.awci_synthetic_field.
        cross_section_phase_severity_field(), aligned to whatever this
        panel's own current heatmap already shows). Either grid may be
        omitted (None) - e.g. the synthetic demo pattern has no real
        wind_shear_grid (no u/v components exist in that pattern - see
        awci_synthetic_field.py's own docstring), so only icing icons
        are drawn there.
        """
        self._hazard_overlay = (distances_km, levels_hpa, phase_severity_grid, wind_shear_grid)
        if self._last_grid_context is not None:
            self._redraw_last()

    def clear_hazard_overlay(self) -> None:
        self._hazard_overlay = None
        if self._last_grid_context is not None:
            self._redraw_last()

    def _redraw_last(self) -> None:
        if self._external_cross_section is not None:
            distances, levels_hpa, grid = self._external_cross_section
        elif self._last_point_a is not None and self._last_point_b is not None:
            distances, levels_hpa, grid = cross_section_field(self._last_point_a, self._last_point_b, n_along=60, n_levels=20)
        else:
            return
        self._draw(distances, levels_hpa, grid)

    def _draw(self, distances: Any, levels_hpa: Any, grid: Any) -> None:
        # A colorbar owns its own Axes and its own reference back to
        # the main plot axes' subplotspec - remove() must run BEFORE
        # self.axis.clear() below, not after (found the hard way: doing
        # it after raised a real "'NoneType' object has no attribute
        # 'set_subplotspec'" on the second redraw - clear() had already
        # disrupted the state remove() needs).
        self._last_grid_context = (distances, levels_hpa)
        if self._colorbar is not None:
            self._colorbar.remove()
            self._colorbar = None
        self.axis.clear()
        levels_ft = [_hpa_to_ft(p) for p in levels_hpa]

        contour = self.axis.contourf(distances, levels_ft, grid, levels=20, cmap=AWCI_CMAP, vmin=0, vmax=100)

        cruise_ft = _hpa_to_ft(self._cruise_hpa)
        self.axis.plot([distances[0], distances[-1]], [cruise_ft, cruise_ft], color="white", linewidth=1.5)
        mid_x = distances[len(distances) // 2]
        self.axis.plot(mid_x, cruise_ft, marker=">", color="white", markersize=10, markeredgecolor="black")

        if self._hazard_overlay is not None:
            self._draw_hazard_icons()

        self.axis.set_facecolor("#0f1830")
        self.axis.set_xlabel("Distance (km)", color="#9fb0c9", fontsize=8)
        self.axis.set_ylabel("Altitude (ft)", color="#9fb0c9", fontsize=8)
        self.axis.tick_params(colors="#9fb0c9", labelsize=7)
        for spine in self.axis.spines.values():
            spine.set_color("#34445f")
        self.axis.set_title(self._title, color="#e8edf5", fontsize=10, fontweight="bold", loc="left")

        # Real AWCI 0-100 colorbar, matching the reference mockup's
        # colorbar under this exact panel.
        self._colorbar = self.figure.colorbar(contour, ax=self.axis, orientation="horizontal", pad=0.28, fraction=0.07, ticks=[0, 20, 40, 60, 80, 100])
        self._colorbar.set_label("AWCI", color="#9fb0c9", fontsize=7)
        self._colorbar.ax.tick_params(colors="#9fb0c9", labelsize=6)
        self._colorbar.outline.set_edgecolor("#34445f")

        self.figure.subplots_adjust(left=0.09, right=0.98, top=0.88, bottom=0.22)
        self.canvas.draw_idle()

    def _draw_hazard_icons(self) -> None:
        """
        Draw real icing/turbulence-proxy icons from self._hazard_overlay
        - see set_hazard_overlay()'s own docstring. Subsampled (not one
        icon per grid cell) to match the mockup's own sparse icon
        placement and stay legible.
        """
        assert self._hazard_overlay is not None
        distances, levels_hpa, phase_severity_grid, wind_shear_grid = self._hazard_overlay
        levels_ft = [_hpa_to_ft(p) for p in levels_hpa]
        n_levels = len(levels_hpa)
        n_along = len(distances)

        if phase_severity_grid is not None:
            level_stride = max(1, n_levels // 3)
            dist_stride = max(1, n_along // 5)
            for level in range(0, n_levels, level_stride):
                for i in range(0, n_along, dist_stride):
                    if phase_severity_grid[level][i] >= _ICING_PROXY_SEVERITY_THRESHOLD:
                        self.axis.text(
                            distances[i], levels_ft[level], "❄", color="#bfe6ff", fontsize=11,
                            ha="center", va="center", zorder=5,
                        )

        if wind_shear_grid is not None:
            n_shear_levels = len(wind_shear_grid)
            level_stride = max(1, n_shear_levels // 3)
            dist_stride = max(1, n_along // 5)
            for level in range(0, n_shear_levels, level_stride):
                for i in range(0, n_along, dist_stride):
                    if wind_shear_grid[level][i] >= _TURBULENCE_PROXY_SHEAR_THRESHOLD_M_S:
                        # Real midpoint altitude between the 2 adjacent
                        # native levels this shear value spans.
                        mid_ft = (levels_ft[level] + levels_ft[level + 1]) / 2.0
                        self.axis.text(
                            distances[i], mid_ft, "≈", color="#ffd54f", fontsize=13, fontweight="bold",
                            ha="center", va="center", zorder=5,
                        )
