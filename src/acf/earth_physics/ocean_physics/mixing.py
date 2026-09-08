"""
Ocean Vertical & Mixed Layer Mixing Module
"""


class OceanVerticalMixing:
    """Modèle de mélange de la couche limite océanique (Turbulent Kinetic Energy TKE)."""

    @classmethod
    def mixed_layer_depth_m(cls, wind_stress: float, heat_flux: float) -> float:
        """
        NOT IMPLEMENTED (documented gap, not faked): this used to
        always return 45.0 regardless of wind_stress/heat_flux — a
        hard-coded fake stub, same bug class as the fake METAR decoder
        found earlier this session.

        Unlike that bug, this one cannot be fixed with a simple
        closed-form correction: real ocean mixed layer depth
        determination needs either (a) a density/temperature profile
        with a threshold criterion (e.g. Delta-sigma > 0.03 kg/m^3
        from the surface), or (b) time-integration of a bulk TKE
        budget model (Kraus & Turner 1967; Price, Weller & Pinkel
        1986) starting from an initial stratification. Neither
        reduces to a single formula of just (wind_stress, heat_flux)
        with no profile and no time dimension. Raises instead of
        returning a number that would look precise but isn't
        physically derived.

        Raises
        ------
        NotImplementedError
            Always, until a real profile-based or time-integrated
            model is implemented.
        """
        raise NotImplementedError(
            "mixed_layer_depth_m() needs a density/temperature profile (threshold criterion) "
            "or time-integration of a bulk TKE model (Kraus & Turner 1967) - not computable from "
            "wind_stress and heat_flux alone. Previously returned a hard-coded fake value (45.0); "
            "removed rather than left silently wrong."
        )
