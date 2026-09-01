"""
Atmospheric Complexity Framework (ACF)

Scientific Anomaly Module
"""

from typing import Any


class AnomalyCalculator:
    """Calculateur d'anomalies climatologiques."""

    @classmethod
    def compute_anomaly(
        cls, val: float, climatology_val: float, climatological_std_dev: float | None = None
    ) -> dict[str, Any]:
        """
        NOTE (correction): standardized_anomaly_sigma used to divide the
        raw anomaly by a hardcoded "1.5" with no physical basis (not the
        real climatological standard deviation of the parameter being
        evaluated), so it always looked like a genuine z-score while
        actually being fabricated for every parameter/location. The
        module also claimed "Anomaly Correlation Coefficient (ACC)" in
        its docstring, but no correlation was ever computed here (ACC
        is genuinely implemented in
        acf.verification.nwp_metrics.NWPVerificationMetrics.acc).

        Fix: standardized_anomaly_sigma is now only computed when a real
        climatological_std_dev is supplied by the caller; otherwise it
        is honestly reported as None instead of a fabricated value.
        """
        anomaly = val - climatology_val
        standardized_anomaly_sigma = (
            anomaly / climatological_std_dev if climatological_std_dev not in (None, 0) else None
        )
        return {"anomaly": anomaly, "standardized_anomaly_sigma": standardized_anomaly_sigma}
