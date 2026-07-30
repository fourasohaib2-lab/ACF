"""
Cloud Microphysics Laws
"""

from acf.science.laws.base_law import AtmosphericLaw

MICROPHYSICS_LAWS = [
    AtmosphericLaw(
        key="kessler_autoconversion",
        name="Taux d'Autoconversion de Kessler",
        domain="Microphysique des Nuages",
        equation="P_auto = k_auto * max(qc - qc_crit, 0)",
        variables={
            "P_auto": "Taux de production de pluie par autoconversion",
            "k_auto": "Taux d'autoconversion (ex: 0.001 s⁻¹)",
            "qc": "Contenu en eau liquide du nuage",
            "qc_crit": "Seuil critique d'eau liquide (ex: 0.0005 kg/kg)",
        },
        units={"P_auto": "kg/(kg·s)", "k_auto": "s⁻¹", "qc, qc_crit": "kg/kg"},
        description="Conversion des gouttelettes de nuage en gouttes de pluie lorsque le seuil critique d'eau condensée est dépassé.",
        references=["Kessler, E. (1969). On the Distribution and Continuity of Water Substance in Atmospheric Circulations.", "NOAA Technical Reports"],
        limitations=["Schéma à 1 moment (bulk single-moment microphysics)."],
        compute_func=lambda qc, qc_crit=0.0005, k_auto=0.001: k_auto * max(qc - qc_crit, 0.0),
    ),
    AtmosphericLaw(
        key="collection_coalescence",
        name="Taux de Collection / Coalescence",
        domain="Microphysique des Nuages",
        equation="P_coll = k_coll * qc * qr**0.875",
        variables={
            "P_coll": "Accroissement des gouttes de pluie par capture des gouttelettes",
            "k_coll": "Coefficient de collection (ex: 2.2 s⁻¹)",
            "qc": "Eau liquide nuageuse",
            "qr": "Eau de pluie",
        },
        units={"P_coll": "kg/(kg·s)", "qc, qr": "kg/kg"},
        description="Captation des gouttelettes en suspension par les gouttes de pluie en chute libre.",
        references=["Kessler (1969)", "Rogers & Yau (1989) A Short Course in Cloud Physics"],
        limitations=["Approximation empirique pour schémas bulk."],
        compute_func=lambda qc, qr, k_coll=2.2: k_coll * qc * (qr ** 0.875),
    ),
    AtmosphericLaw(
        key="ice_crystal_nucleation",
        name="Nucléation des Cristaux de Glace",
        domain="Microphysique des Nuages",
        equation="N_ice(T) = N0 * exp(b * (273.15 - T))",
        variables={
            "N_ice": "Concentration de noyaux glaçogènes actifs",
            "T": "Température sous 0°C",
            "N0, b": "Paramètres empiriques d'activation",
        },
        units={"N_ice": "m⁻³", "T": "K"},
        description="Formation de cristaux de glace primaires par congélation hétérogène ou immersion.",
        references=["Fletcher (1962) Physics of Rainclouds", "ECMWF Cloud Microphysics Documentation"],
        limitations=["Fortement dépendant de la présence d'aérosols glaçogènes."],
    ),
]
