from dataclasses import dataclass


@dataclass(slots=True)
class AtmosphericDynamicsState:
    """
    Etat dynamique atmosphérique Model 4D
    """

    jet_stream_speed: float
    vorticity: float
    divergence: float
    convergence: float
    warm_advection: float
    cold_advection: float
    upper_troposphere_forcing: float
    lower_troposphere_energy: float


class AdvancedAtmosphericDynamicsEngine:
    """
    Atmospheric Complexity Framework

    Sprint 9.43
    Advanced Atmospheric Dynamics Engine

    Analyse:
    - Jet stream
    - Vorticité
    - Divergence altitude
    - Convergence basse couche
    - Advection thermique
    - Couplage troposphérique
    """

    def jet_stream_analysis(
        self,
        state: AtmosphericDynamicsState,
    ) -> float:

        return round(
            state.jet_stream_speed * 0.45,
            2,
        )


    def vorticity_analysis(
        self,
        state: AtmosphericDynamicsState,
    ) -> float:

        return round(
            state.vorticity * 0.80,
            2,
        )


    def dynamic_lift_index(
        self,
        state: AtmosphericDynamicsState,
    ) -> float:

        value = (
            state.divergence
            + state.convergence
            + state.upper_troposphere_forcing
        )

        return round(
            value / 3,
            2,
        )


    def thermal_advection_balance(
        self,
        state: AtmosphericDynamicsState,
    ) -> float:

        return round(
            (
                state.warm_advection
                - state.cold_advection
            )
            * 0.75,
            2,
        )


    def tropospheric_coupling(
        self,
        state: AtmosphericDynamicsState,
    ) -> float:

        return round(
            (
                state.upper_troposphere_forcing
                + state.lower_troposphere_energy
            )
            / 2,
            2,
        )


    def atmospheric_instability(
        self,
        state: AtmosphericDynamicsState,
    ) -> float:

        total = (
            self.vorticity_analysis(state)
            + self.dynamic_lift_index(state)
            + self.thermal_advection_balance(state)
            + self.tropospheric_coupling(state)
        )

        return round(
            total / 3.75,
            2,
        )


    def circulation_regime(
        self,
        state: AtmosphericDynamicsState,
    ) -> str:

        index = self.atmospheric_instability(state)

        if index >= 70:
            return "ACTIVE_DYNAMIC_REGIME"

        if index >= 40:
            return "MODERATE_DYNAMIC_REGIME"

        return "STABLE_DYNAMIC_REGIME"


    def dynamics_update(
        self,
        state: AtmosphericDynamicsState,
    ) -> dict:

        return {
            "jet_stream":
                self.jet_stream_analysis(state),

            "vorticity":
                self.vorticity_analysis(state),

            "dynamic_lift":
                self.dynamic_lift_index(state),

            "thermal_balance":
                self.thermal_advection_balance(state),

            "tropospheric_coupling":
                self.tropospheric_coupling(state),

            "instability":
                self.atmospheric_instability(state),

            "regime":
                self.circulation_regime(state),
        }
