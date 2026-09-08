"""
Permafrost Thaw & Carbon/Methane Release Model
"""


class PermafrostThawModel:
    """Modèle de dégel du permafrost et de libération de méthane et $CO_2$."""

    @classmethod
    def compute_ch4_emission_megatons(cls, thaw_depth_increase_m: float) -> float:
        """
        NOTE (found, NOT changed — Physics Guard, found during the
        post-model4d audit, 2026-09-05): "* 14.5" has no cited source
        and no documented derivation anywhere in this codebase or its
        history. More fundamentally, a real global CH4 release from
        permafrost thaw scales with the AREA of permafrost thawed and
        its soil organic carbon content/microbial decomposition rate -
        not with thaw depth alone, which this function's only
        parameter is. A linear depth-only formula with an unsourced
        coefficient cannot honestly represent a "global" methane
        budget in megatons regardless of what the coefficient's value
        is. Flagged rather than replaced with an equally unfounded
        area-aware formula invented here without a citable source
        (same reasoning already applied to this codebase's other
        undocumented-coefficient findings - see e.g.
        acf.space_weather.ionosphere.ionosphere_engine's M-factor
        NOTE). Kept as an illustrative, order-of-magnitude scaling
        only - not validated against any real permafrost-carbon model
        (e.g. a real implementation would need something like the
        published PInc-CH4/JULES-permafrost parameterizations, keyed
        on area and soil carbon stock, not just depth).
        """
        return thaw_depth_increase_m * 14.5
