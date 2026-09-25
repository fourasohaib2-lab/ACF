"""
Diagnostics
============

SituationDiagnosis: a human-readable synthesis layer aggregating
ACF's already-computed indices (severe weather, visibility, moisture,
stability) into a qualitative situation summary.

IMPORTANT: the "6 weather regimes" classification here is ACF's OWN
operational categorization of a local point-observation situation
(stable / showery / rainy / severe convective / poor visibility /
hazardous-extreme) — it is NOT the formal synoptic-scale "weather
regime" concept from the climate literature (e.g. Vautard 1990's 4
North Atlantic regimes: Zonal, Blocking, Greenland Anticyclone,
Atlantic Ridge), which requires large-scale reanalysis / EOF analysis
over a full basin, not point data. Labeled explicitly to avoid
implying a formal typology this module does not implement.

This module reuses SevereWeather.threat_level(), FogRisk, and other
already-verified indices — it does not introduce new physical
formulas, only thresholds for qualitative labeling (documented as
ACF's own operational convention, same treatment as
awci/calculator.py's interaction terms and severe_weather.py's
classify_threat()).
"""

from dataclasses import dataclass, field


@dataclass
class DiagnosticAlert:
    """One qualitative alert raised by SituationDiagnosis."""

    category: str  # "convection", "visibility", "wind", "precipitation"
    level: str  # "Info", "Advisory", "Warning", "Severe"
    message: str


@dataclass
class SituationDiagnosis:
    """Aggregated qualitative diagnosis of a local weather situation."""

    weather_regime: str
    alerts: list[DiagnosticAlert] = field(default_factory=list)
    explanation: list[str] = field(default_factory=list)

    @staticmethod
    def diagnose(
        cape_j_kg: float = 0.0,
        threat_level: str | None = None,
        precipitation_rate_mm_h: float = 0.0,
        visibility_m: float = 10000.0,
        wind_speed_m_s: float = 0.0,
        wind_gust_m_s: float | None = None,
    ) -> "SituationDiagnosis":
        """
        Build a SituationDiagnosis from a bundle of already-computed
        inputs (typically produced upstream by SevereWeather.summary(),
        PrecipitationIntensity.classify(), etc. — this method does not
        recompute those, it only synthesizes from their outputs).

        Parameters
        ----------
        cape_j_kg : float
            CAPE (J/kg), for convective-regime detection.
        threat_level : str, optional
            SevereWeather.classify_threat() output, if available.
        precipitation_rate_mm_h : float
            Current precipitation rate (mm/h).
        visibility_m : float
            Current visibility (m).
        wind_speed_m_s : float
            Current sustained wind speed (m/s).
        wind_gust_m_s : float, optional
            Current wind gust (m/s), if available.

        Returns
        -------
        SituationDiagnosis
        """
        alerts: list[DiagnosticAlert] = []
        explanation: list[str] = []

        # --- Regime classification (ACF operational convention) ---
        if threat_level in ("Significant tornado potential", "Extreme tornado potential"):
            regime = "Severe Convective"
        elif visibility_m < 1000.0:
            regime = "Poor Visibility"
        elif precipitation_rate_mm_h >= 7.6:
            regime = "Heavy Rain"
        elif cape_j_kg >= 1000.0:
            regime = "Showery/Convective"
        elif precipitation_rate_mm_h > 0.0:
            regime = "Light Rain"
        else:
            regime = "Stable/Fair"

        explanation.append(f"Régime de temps : {regime}")

        # --- Convection ---
        if cape_j_kg >= 2500.0:
            alerts.append(
                DiagnosticAlert("convection", "Severe", f"CAPE extrême ({cape_j_kg:.0f} J/kg) : fort potentiel convectif")
            )
        elif cape_j_kg >= 1000.0:
            alerts.append(
                DiagnosticAlert("convection", "Advisory", f"CAPE modérée à forte ({cape_j_kg:.0f} J/kg)")
            )

        if threat_level:
            level = "Severe" if "Extreme" in threat_level or "Significant" in threat_level else "Info"
            alerts.append(DiagnosticAlert("convection", level, f"Indice composite : {threat_level}"))
            explanation.append(f"Potentiel orageux sévère : {threat_level}")

        # --- Visibility ---
        if visibility_m < 200.0:
            alerts.append(DiagnosticAlert("visibility", "Severe", f"Visibilité très faible ({visibility_m:.0f} m)"))
        elif visibility_m < 1000.0:
            alerts.append(DiagnosticAlert("visibility", "Warning", f"Visibilité réduite ({visibility_m:.0f} m)"))

        # --- Wind ---
        peak_wind = wind_gust_m_s if wind_gust_m_s is not None else wind_speed_m_s
        if peak_wind >= 25.0:
            alerts.append(DiagnosticAlert("wind", "Severe", f"Vent violent ({peak_wind:.0f} m/s)"))
        elif peak_wind >= 15.0:
            alerts.append(DiagnosticAlert("wind", "Warning", f"Vent fort ({peak_wind:.0f} m/s)"))

        # --- Precipitation ---
        if precipitation_rate_mm_h >= 50.0:
            alerts.append(
                DiagnosticAlert("precipitation", "Severe", f"Précipitations violentes ({precipitation_rate_mm_h:.1f} mm/h)")
            )
        elif precipitation_rate_mm_h >= 7.6:
            alerts.append(
                DiagnosticAlert("precipitation", "Warning", f"Précipitations fortes ({precipitation_rate_mm_h:.1f} mm/h)")
            )

        if not alerts:
            explanation.append("Aucune alerte : conditions calmes.")
        else:
            explanation.append(f"{len(alerts)} alerte(s) active(s).")

        return SituationDiagnosis(weather_regime=regime, alerts=alerts, explanation=explanation)

    def highest_alert_level(self) -> str:
        """
        Overall situation severity: the highest level among all alerts
        ("Severe" > "Warning" > "Advisory" > "Info"), or "None" if no
        alerts are present.
        """
        order = {"Severe": 3, "Warning": 2, "Advisory": 1, "Info": 0}
        if not self.alerts:
            return "None"
        return max(self.alerts, key=lambda a: order.get(a.level, 0)).level
