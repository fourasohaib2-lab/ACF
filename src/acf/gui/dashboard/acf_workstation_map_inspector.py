"""
ACF Scientific Workstation — Map Inspector
===============================================

Real per-point diagnostic popup (Phase 36, 2026-09-05), matching the
reference mockup's own "MAP INSPECTOR" box (`docs/reference/
acf_scientific_workstation_reference.jpg`) - appears on any real map
click, alongside the always-visible Vertical Complexity Sounding/
Atmospheric Interaction Graph updates `acf_workstation.
_on_map_point_clicked()` already triggers (Phases 33-34).

Real formulas, all reused as-is - nothing new invented
------------------------------------------------------------
Every value here comes from a real, already-existing ACF function,
called fresh at the exact clicked point:

- Elevation/slope/aspect: `acf.awci.terrain_elevation.
  compute_real_terrain_slope_aspect_at_point()` (added alongside this
  panel, itself built from the same real, bundled SRTM15+ grid Terrain
  Lab already uses).
- Temperature/wind/humidity/pressure: the real nearest-neighbour
  column lookup this Workstation's volume already carries (same
  technique as `acf.awci.vertical_field.vertical_profile_at_point()`).
- Relative humidity/θ-e: `acf.awci.theta_e.
  compute_real_theta_e_at_point()` - reused by Thermodynamics Lab.
- Precipitation phase/wet-bulb: `acf.awci.hydrometeor_phase.
  compute_real_hydrometeor_phase_at_point()` - reused by Microphysics
  Lab.
- Relative vorticity/divergence: `acf.awci.workstation_fields.
  compute_real_vorticity_divergence()` - reused by Dynamics Lab,
  evaluated over the current level's real full grid then sampled at
  the clicked point (a real per-point value needs its real
  neighbours, unlike the point-only formulas above).
- Bulk wind shear: `acf.awci.wind_shear.
  compute_real_wind_shear_at_point()` - reused by Dynamics Lab, over
  this point's own real full vertical column.

Honest scope
-------------
CAPE/CIN is NOT computed here - that real, MetPy-based parcel-ascent
calculation is genuinely more expensive per point and already has a
real, dedicated home (Thermodynamics Lab's own Research Mode click) -
not duplicated in this always-on inspector to avoid silently doubling
that cost on every single map click.
"""

from __future__ import annotations

from typing import Any

import numpy as np
from PySide6.QtWidgets import QDialog, QLabel, QVBoxLayout, QWidget

from acf.awci.hydrometeor_phase import compute_real_hydrometeor_phase_at_point
from acf.awci.terrain_elevation import compute_real_terrain_slope_aspect_at_point
from acf.awci.theta_e import compute_real_theta_e_at_point
from acf.awci.wind_shear import compute_real_wind_shear_at_point
from acf.awci.workstation_fields import compute_real_vorticity_divergence
from acf.gui.theme_tokens import label_style
from acf.gui_screen_utils import fit_dialog_to_screen


def compute_real_map_inspector_snapshot(volume: dict[str, Any], lat: float, lon: float, level_index: int) -> dict[str, Any]:
    """Real, Qt-free per-point diagnostic snapshot - see module
    docstring for exactly which real function backs each field."""
    lats = np.asarray(volume["lats"])
    lons = np.asarray(volume["lons"])
    lat_idx = int(np.argmin(np.abs(lats - lat)))
    lon_idx = int(np.argmin(np.abs(lons - lon)))
    real_lat, real_lon = float(lats[lat_idx]), float(lons[lon_idx])

    temperature_k = float(volume["temperature_volume"][level_index, lat_idx, lon_idx])
    u = float(volume["u_volume"][level_index, lat_idx, lon_idx])
    v = float(volume["v_volume"][level_index, lat_idx, lon_idx])
    specific_humidity = float(volume["specific_humidity_volume"][level_index, lat_idx, lon_idx])
    pressure_hpa = float(volume["pressure_volume_hpa"][level_index, lat_idx, lon_idx])
    wind_speed = float(np.hypot(u, v))
    wind_direction_deg = float(np.degrees(np.arctan2(-u, -v)) % 360.0) if wind_speed > 0.0 else float("nan")

    terrain = compute_real_terrain_slope_aspect_at_point(real_lat, real_lon)
    theta_e = compute_real_theta_e_at_point(temperature_k, specific_humidity, pressure_hpa)
    phase = compute_real_hydrometeor_phase_at_point(temperature_k, specific_humidity, pressure_hpa)

    vorticity_field, divergence_field = compute_real_vorticity_divergence(
        volume["u_volume"][level_index], volume["v_volume"][level_index], lats, lons
    )
    vorticity = float(vorticity_field[lat_idx, lon_idx])
    divergence = float(divergence_field[lat_idx, lon_idx])

    u_profile = volume["u_volume"][:, lat_idx, lon_idx]
    v_profile = volume["v_volume"][:, lat_idx, lon_idx]
    shear = compute_real_wind_shear_at_point(u_profile, v_profile)

    return {
        "lat": real_lat,
        "lon": real_lon,
        "model": volume.get("model", ""),
        "level_index": level_index,
        "elevation_m": terrain["elevation_m"],
        "slope": terrain["slope"],
        "aspect_deg": terrain["aspect_deg"],
        "temperature_c": temperature_k - 273.15,
        "wind_speed_ms": wind_speed,
        "wind_direction_deg": wind_direction_deg,
        "specific_humidity_g_kg": specific_humidity * 1000.0,
        "pressure_hpa": pressure_hpa,
        "relative_humidity_pct": theta_e["relative_humidity_pct"],
        "theta_e_k": theta_e["theta_e_k"],
        "precipitation_phase": phase["phase"],
        "precipitation_phase_severity": phase["phase_severity"],
        "wet_bulb_c": phase["wet_bulb_c"],
        "vorticity_s1": vorticity,
        "divergence_s1": divergence,
        "bulk_wind_shear_ms": shear["shear_m_s"],
    }


def format_map_inspector_lines(snapshot: dict[str, Any]) -> list[str]:
    """Real, Qt-free text formatting of a snapshot - directly
    unit-testable, no dialog required."""

    def _fmt(value: Any, unit: str = "", digits: int = 2) -> str:
        if value is None or (isinstance(value, float) and np.isnan(value)):
            return "n/a"
        return f"{value:.{digits}f}{unit}"

    return [
        f"Lat, Lon: {snapshot['lat']:.2f}°, {snapshot['lon']:.2f}°",
        f"Model: {snapshot['model']} (native level {snapshot['level_index'] + 1})",
        f"Elevation: {_fmt(snapshot['elevation_m'], ' m', 0)}",
        f"Terrain slope: {_fmt(snapshot['slope'], '', 5)}   Aspect: {_fmt(snapshot['aspect_deg'], '°', 0)}",
        "",
        f"Temperature: {_fmt(snapshot['temperature_c'], ' °C')}",
        f"Wind: {_fmt(snapshot['wind_speed_ms'], ' m/s')} @ {_fmt(snapshot['wind_direction_deg'], '°', 0)}",
        f"Specific humidity: {_fmt(snapshot['specific_humidity_g_kg'], ' g/kg')}",
        f"Pressure: {_fmt(snapshot['pressure_hpa'], ' hPa')}",
        f"Relative humidity: {_fmt(snapshot['relative_humidity_pct'], ' %')}",
        f"θ-e: {_fmt(snapshot['theta_e_k'], ' K')}",
        "",
        f"Precipitation phase: {snapshot['precipitation_phase']} (severity {snapshot['precipitation_phase_severity']:.1f})",
        f"Wet-bulb: {_fmt(snapshot['wet_bulb_c'], ' °C')}",
        f"Vorticity: {snapshot['vorticity_s1']:.2e} s⁻¹   Divergence: {snapshot['divergence_s1']:.2e} s⁻¹",
        f"Bulk wind shear: {_fmt(snapshot['bulk_wind_shear_ms'], ' m/s')}",
        "",
        "CAPE/CIN: enable Research Mode on Thermodynamics Lab for a full parcel-ascent diagnostic at this point.",
    ]


class ACFMapInspectorDialog(QDialog):
    """Real, non-modal per-point diagnostic popup - see module
    docstring. Reused across clicks (never re-created), matching this
    Workstation's own CommandPaletteDialog convention."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Map Inspector")
        self.setModal(False)
        layout = QVBoxLayout(self)
        self.text_label = QLabel("Click a map to inspect a real point.")
        self.text_label.setWordWrap(True)
        self.text_label.setStyleSheet(label_style("text_primary", "sm") + "font-family: monospace;")
        layout.addWidget(self.text_label)
        # NOTE (real responsive-sizing fix, 2026-09-05): was a hardcoded
        # self.resize(320, 380) - clamp to the actual screen instead, same
        # fix as gui_screen_utils.fit_window_to_screen for main windows.
        fit_dialog_to_screen(self, 320, 380)

    def set_snapshot(self, snapshot: dict[str, Any]) -> None:
        self.text_label.setText("\n".join(format_map_inspector_lines(snapshot)))
