"""
Atmospheric Complexity Framework (ACF)

AI Geological & Seismological Reasoning Engine Module (Phase 17)
(Causal Explanations for Earthquakes, Volcanic Eruptions, Tsunamis, Subduction, Gutenberg-Richter)
"""

from typing import Any


class GeologicalReasoningEngine:
    """
    Moteur d'IA explicative et de raisonnement causal pour la géologie et la sismologie.
    """

    _FAULT_STRESS_REGIMES: dict[str, dict[str, str]] = {
        "subduction megathrust": {
            "stress_regime": "Compressional (convergent plate boundary)",
            "geometry": (
                "Faille inverse à faible pendage (~10-20°) : la plaque océanique subductante plonge sous la plaque "
                "chevauchante, verrouillée par friction sur l'interface de subduction (zone sismogène ~5-50 km)."
            ),
            "causal_chain": (
                "Convergence des Plaques -> Verrouillage de l'Interface de Subduction -> Accumulation de Contrainte "
                "Compressive -> Friction Dépassée -> Rupture le Long du Plan de Chevauchement -> Ondes Sismiques (+ Tsunami possible)"
            ),
        },
        "strike-slip": {
            "stress_regime": "Cisaillement horizontal pur (décrochement, faille quasi-verticale)",
            "geometry": (
                "Faille verticale ou sub-verticale ; les deux blocs coulissent horizontalement l'un contre l'autre "
                "(ex : San Andreas, Anatolie du Nord) sans composante verticale dominante."
            ),
            "causal_chain": (
                "Mouvement Tangentiel des Plaques -> Accumulation de Contrainte de Cisaillement -> Friction Dépassée "
                "-> Rupture par Glissement Horizontal -> Ondes Sismiques"
            ),
        },
        "normal": {
            "stress_regime": "Extensionnel (rifting, divergence)",
            "geometry": (
                "Faille à fort pendage (~45-60°) : le compartiment supérieur (toit) glisse vers le bas par rapport "
                "au compartiment inférieur (mur) sous l'effet d'un étirement crustal."
            ),
            "causal_chain": (
                "Divergence/Extension Crustale -> Amincissement de la Croûte -> Accumulation de Contrainte Tensile "
                "-> Résistance Dépassée -> Affaissement du Toit -> Ondes Sismiques"
            ),
        },
        "reverse": {
            "stress_regime": "Compressionnel (raccourcissement crustal)",
            "geometry": (
                "Faille à pendage modéré à fort (~30-60°) : le compartiment supérieur (toit) chevauche le "
                "compartiment inférieur (mur) sous compression horizontale (ex : chaînes de collision continentale)."
            ),
            "causal_chain": (
                "Convergence/Raccourcissement Crustal -> Accumulation de Contrainte Compressive -> Résistance au "
                "Cisaillement Dépassée -> Chevauchement du Toit -> Ondes Sismiques"
            ),
        },
    }

    @classmethod
    def explain_earthquake_physics(cls, fault_type: str = "Subduction Megathrust") -> dict[str, Any]:
        """Explique la physique des séismes et le cycle d'accumulation/décharge de contrainte.

        NOTE (correction): `fault_type` used to be accepted but never
        referenced - the exact same generic subduction-megathrust
        explanation was returned regardless of the fault type passed in
        (e.g. "Strike-Slip" or "Normal" produced identical output).
        The stress regime and rupture geometry genuinely differ by
        fault type (Reid 1910's elastic-rebound cycle is universal, but
        the mechanical context is not), so the mechanism/causal_chain
        below now vary by `fault_type`. Falls back to the subduction
        megathrust description (still correct in general, just not
        specific) for an unrecognized fault type.
        """
        key = fault_type.strip().lower()
        regime = cls._FAULT_STRESS_REGIMES.get(key, cls._FAULT_STRESS_REGIMES["subduction megathrust"])
        return {
            "phenomenon": "Seismic Rupture & Elastic Rebound",
            "fault_type": fault_type,
            "stress_regime": regime["stress_regime"],
            "physical_mechanism": (
                "Les séismes sont provoqués par la libération soudaine de l'énergie élastique accumulée dans la croûte terrestre "
                "le long d'une faille verrouillée. Lorsque les contraintes tectoniques dépassent la résistance au cisaillement (friction) "
                "de la faille, une rupture se propage à une vitesse de ~2 à 3 km/s, rayonnant des ondes sismiques P et S. "
                f"{regime['geometry']}"
            ),
            "causal_chain": regime["causal_chain"],
            "equations": [r"M_0 = \mu A D", r"M_w = \frac{2}{3}\log_{10} M_0 - 6.07"],
            "references": ["Reid (1910) Elastic Rebound Theory", "Kanamori (1977) JGR"],
        }

    @classmethod
    def explain_volcano_eruption(cls) -> dict[str, Any]:
        """Explique la dynamique des éruptions volcaniques et la dégazage magmatique."""
        return {
            "phenomenon": "Volcanic Eruption & Magmatic Exsolution",
            "physical_mechanism": (
                "Une éruption volcanique se produit lorsque du magma moins dense que les roches environnantes remonte dans la croûte. "
                "Lors de son ascension, la baisse de pression entraîne la décompression et l'exsolution des gaz dissous (H2O, CO2, SO2). "
                "Si la viscosité du magma est élevée (magma andésitique/dacitique), la surpression des bulles provoque une fragmentation explosive (Plinienne)."
            ),
            "causal_chain": "Mantle Melting -> Magma Buoyant Ascent -> Decompression Gas Exsolution -> Overpressure -> Explosive Eruption",
            "references": ["Sparks et al. (1997) Volcanic Plumes"],
        }
