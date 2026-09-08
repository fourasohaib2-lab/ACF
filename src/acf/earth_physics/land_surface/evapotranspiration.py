"""
Evapotranspiration & Latent Heat Flux Model (simplified proxy)

NOTE (correction — Physics Guard): this module's own title and its
class docstring used to call this "Équation de Penman-Monteith"
(Penman-Monteith equation), but the formula below is a crude linear
proxy in (net_radiation, temperature) alone - it has no vapor pressure
deficit, wind speed, psychrometric constant, or aerodynamic/surface
resistance terms, all of which the real Penman-Monteith equation
requires. Claiming a specific, named, citable method while actually
computing something else is exactly the class of bug this session's
audit exists to catch (see e.g. science/storm_motion.py's Bunkers
motion fix). ACF already has a genuine, reference-verified FAO-56
Penman-Monteith implementation - science/surface_fire.py's
PenmanMonteithFAO56.calculate() (Allen, Pereira, Raes & Smith 1998,
numerically verified against a worked example this session) - callers
needing real Penman-Monteith ET0 should use that instead. This
function's signature (net_radiation, temperature only) cannot be
turned into a real Penman-Monteith call without inventing the missing
required inputs (vapor pressure deficit, wind speed), so it is kept
as an honestly-labeled simplified proxy rather than silently deleted
or fabricated into something it isn't.
"""


class EvapotranspirationModel:
    """Modèle simplifié (proxy linéaire) d'évapotranspiration potentielle - PAS l'équation de
    Penman-Monteith (voir science/surface_fire.py's PenmanMonteithFAO56 pour celle-ci)."""

    @classmethod
    def potential_evapotranspiration_mm_day(cls, net_radiation_wm2: float, temp_c: float) -> float:
        """
        Proxy simplifié (non physique de référence) : PET ~= 0.035*Rn + 0.1*T, en mm/jour.

        Ne prend en compte ni le déficit de pression de vapeur, ni le
        vent, ni la résistance aérodynamique/de surface - CE N'EST PAS
        l'équation de Penman-Monteith. Utiliser
        science/surface_fire.py's PenmanMonteithFAO56.calculate() pour
        un calcul réel de référence FAO-56.
        """
        return max(0.0, net_radiation_wm2 * 0.035 + (temp_c * 0.1))
