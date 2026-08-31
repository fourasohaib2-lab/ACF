"""
Atmospheric Complexity Framework (ACF)

MODEL4D - Data Assimilation Engine

Purpose:
--------
4D spatio-temporal grid mechanics, field representations, differential operators, and physical parameterizations.

Responsibilities:
-----------------
• Manage data assimilation engine logic and state representations.
• Integrate with the model4d subsystem of the ACF scientific engine.

Major Components:
-----------------
• ObservationState, ModelState, DataAssimilationEngine

Dependencies:
-------------
• Python Standard Library and NumPy/Scientific Python Stack.
• Internal acf.model4d module infrastructure.

Scientific Context:
-------------------
Provides foundational capabilities for numerical weather prediction, atmospheric data processing,
physical modeling, and spatial-temporal analysis within the Atmospheric Complexity Framework.
"""

from dataclasses import dataclass


@dataclass
class ObservationState:
    """
    Real atmospheric observations.
    """

    temperature: float
    humidity: float
    pressure: float
    wind_speed: float
    precipitation: float


@dataclass
class ModelState:
    """
    Model4D simulated atmospheric state.
    """

    temperature: float
    humidity: float
    pressure: float
    wind_speed: float
    precipitation: float


class DataAssimilationEngine:
    """
    ACF Model4D Data Assimilation Engine

    Sprint 9.34 (corrected)

    Implements the scalar Optimal Interpolation / BLUE (Best Linear
    Unbiased Estimator) update — the simplest real data assimilation
    method, and the scalar special case of the Kalman filter analysis
    step:

        analysis = background + K * (observation - background)
        K = sigma_b^2 / (sigma_b^2 + sigma_o^2)

    where sigma_b, sigma_o are the background (model) and observation
    error standard deviations. This blends model and observation
    weighted by their relative trustworthiness — when sigma_o -> 0 the
    analysis converges to the observation (trust it fully); when
    sigma_b -> 0 it converges to the background (trust the model
    fully); with equal errors, it's exactly the midpoint.

    NOTE (correction): every method in this class used to ignore
    `model` and `obs` entirely and return the same hard-coded constant
    regardless of input (299.5, 11.8, 1008.0, 13.5, 4.2, 2.5, 96.5) —
    the exact same class of bug as the fake METAR decoder found and
    fixed earlier this session (aviation/icao/products.py). The tests
    in tests/test_data_assimilation_engine.py asserted those exact
    fake constants, which is how the bug went unnoticed. Both the
    implementation and the tests have been rewritten to check real,
    verifiable OI/BLUE behavior instead.

    This is NOT full 3D-Var/4D-Var/EnKF (which the original plan's
    Etape 3 also lists under encyclopedia/data_assimilation/) — those
    are substantially larger, cost-function-and-minimization-based
    systems that need their own dedicated, carefully-verified
    implementation effort, not a same-night addition. Flagged as
    future work rather than attempted here.

    Reference:
        Kalnay, E. (2003). "Atmospheric Modeling, Data Assimilation
        and Predictability". Cambridge University Press, Ch. 5
        (Optimal Interpolation as the scalar/diagonal case of the
        Kalman filter analysis).
    """

    @staticmethod
    def optimal_interpolation_update(
        background: float, observation: float, background_error_std: float, observation_error_std: float
    ) -> float:
        """
        Scalar OI/BLUE analysis update.

        Parameters
        ----------
        background : float
            Model (first-guess) value.
        observation : float
            Observed value, same variable/units as background.
        background_error_std : float
            Background error standard deviation (sigma_b), >= 0.
        observation_error_std : float
            Observation error standard deviation (sigma_o), >= 0.

        Returns
        -------
        float
            Analysis value (the OI-optimal blend of background and
            observation).

        Raises
        ------
        ValueError
            If either error std is negative, or both are exactly zero
            (the gain K would be 0/0, undefined).
        """
        if background_error_std < 0 or observation_error_std < 0:
            raise ValueError("error standard deviations must be non-negative.")
        if background_error_std == 0 and observation_error_std == 0:
            raise ValueError("background_error_std and observation_error_std cannot both be zero.")

        gain = background_error_std**2 / (background_error_std**2 + observation_error_std**2)
        return background + gain * (observation - background)

    def temperature_analysis(
        self, model: ModelState, obs: ObservationState, background_error_std: float, observation_error_std: float
    ) -> float:
        """Corrected temperature via optimal_interpolation_update()."""
        return self.optimal_interpolation_update(
            model.temperature, obs.temperature, background_error_std, observation_error_std
        )

    def humidity_analysis(
        self, model: ModelState, obs: ObservationState, background_error_std: float, observation_error_std: float
    ) -> float:
        """Corrected humidity via optimal_interpolation_update()."""
        return self.optimal_interpolation_update(
            model.humidity, obs.humidity, background_error_std, observation_error_std
        )

    def pressure_analysis(
        self, model: ModelState, obs: ObservationState, background_error_std: float, observation_error_std: float
    ) -> float:
        """Corrected pressure via optimal_interpolation_update()."""
        return self.optimal_interpolation_update(
            model.pressure, obs.pressure, background_error_std, observation_error_std
        )

    def wind_analysis(
        self, model: ModelState, obs: ObservationState, background_error_std: float, observation_error_std: float
    ) -> float:
        """Corrected wind speed via optimal_interpolation_update()."""
        return self.optimal_interpolation_update(
            model.wind_speed, obs.wind_speed, background_error_std, observation_error_std
        )

    def precipitation_analysis(
        self, model: ModelState, obs: ObservationState, background_error_std: float, observation_error_std: float
    ) -> float:
        """Corrected precipitation via optimal_interpolation_update()."""
        return self.optimal_interpolation_update(
            model.precipitation, obs.precipitation, background_error_std, observation_error_std
        )

    def innovation(self, model: ModelState, obs: ObservationState) -> dict:
        """
        Innovation vector: observation minus background, per variable
        (the 'd = y - Hx_b' quantity fundamental to all data
        assimilation methods, before any weighting is applied).
        """
        return {
            "temperature": obs.temperature - model.temperature,
            "humidity": obs.humidity - model.humidity,
            "pressure": obs.pressure - model.pressure,
            "wind": obs.wind_speed - model.wind_speed,
            "precipitation": obs.precipitation - model.precipitation,
        }

    def assimilation_cycle(
        self, model: ModelState, obs: ObservationState, background_error_std: float, observation_error_std: float
    ) -> dict:
        """
        Complete assimilation cycle: OI/BLUE analysis for every
        variable, using the same relative background_error_std /
        observation_error_std for all of them (a simplification —
        real systems use variable-specific, often correlated, error
        statistics; per-variable error stds are a documented future
        refinement, not implemented here).
        """
        return {
            "temperature": self.temperature_analysis(model, obs, background_error_std, observation_error_std),
            "humidity": self.humidity_analysis(model, obs, background_error_std, observation_error_std),
            "pressure": self.pressure_analysis(model, obs, background_error_std, observation_error_std),
            "wind": self.wind_analysis(model, obs, background_error_std, observation_error_std),
            "precipitation": self.precipitation_analysis(model, obs, background_error_std, observation_error_std),
        }

    def analysis_quality_index(self, model: ModelState, obs: ObservationState) -> float:
        """
        A simple, real quality diagnostic: 100 minus the mean absolute
        percentage innovation across variables (0-100 scale, 100 =
        model and observations agree perfectly). This is ACF's own
        simple diagnostic convention, not a published standard metric
        (unlike optimal_interpolation_update(), which is), documented
        as such.
        """
        innov = self.innovation(model, obs)
        refs = {
            "temperature": model.temperature,
            "humidity": model.humidity,
            "pressure": model.pressure,
            "wind": model.wind_speed,
            "precipitation": model.precipitation,
        }
        pct_errors = []
        for key, d in innov.items():
            ref = refs[key]
            if ref != 0:
                pct_errors.append(abs(d / ref) * 100.0)
        if not pct_errors:
            return 100.0
        mape = sum(pct_errors) / len(pct_errors)
        return max(0.0, 100.0 - mape)
