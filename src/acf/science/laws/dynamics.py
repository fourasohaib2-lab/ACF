"""
Atmospheric Dynamics Laws
"""

from acf.science.laws.base_law import AtmosphericLaw

DYNAMIC_LAWS = [
    AtmosphericLaw(
        key="geostrophic_balance",
        name="Équilibre Géostrophique",
        domain="Dynamique Atmosphérique",
        equation="f * vg = 1/rho * dp/dx ; f * ug = -1/rho * dp/dy",
        variables={
            "f": "Paramètre de Coriolis (2*Omega*sin(phi))",
            "ug, vg": "Composantes du vent géostrophique",
            "rho": "Masse volumique de l'air",
            "dp/dx, dp/dy": "Gradients horizontaux de pression",
        },
        units={"f": "s⁻¹", "ug, vg": "m/s", "rho": "kg/m³", "dp": "Pa/m"},
        description="Équilibre exact à grande échelle entre la force du gradient de pression et la force de Coriolis.",
        references=["WMO Atmospheric Dynamics Manual", "ECMWF Scientific Documentation"],
        limitations=["Valable au-dessus de la couche limite atmosphérique à des latitudes extratropicales."],
        compute_func=lambda dp_dx, dp_dy, density, coriolis_f: (
            -dp_dy / (coriolis_f * density),
            dp_dx / (coriolis_f * density),
        ),
    ),
    AtmosphericLaw(
        key="ertel_potential_vorticity",
        name="Vorticité Potentielle d'Ertel (PV)",
        domain="Dynamique Atmosphérique",
        equation="PV = 1/rho * (eta . grad(theta))",
        variables={
            "PV": "Vorticité potentielle (1 PVU = 1e-6 K m² / (kg s))",
            "rho": "Masse volumique",
            "eta": "Vecteur vorticité absolue (zeta + f)",
            "theta": "Température potentielle",
        },
        units={"PV": "PVU", "rho": "kg/m³", "eta": "s⁻¹", "theta": "K"},
        description="Grandeur conservée dans un écoulement adiabatique sans frottement, fondamentale pour le diagnostic des anomalies de tropopause.",
        references=["Hoskins et al. (1985) On the use and significance of PV maps", "ECMWF Technical Reports"],
        limitations=["Conservation exacte valable uniquement hors processus diabatiques et frottements."],
    ),
    AtmosphericLaw(
        key="absolute_vorticity",
        name="Vorticité Absolue",
        domain="Dynamique Atmosphérique",
        equation="eta = zeta + f",
        variables={
            "eta": "Vorticité absolue",
            "zeta": "Vorticité relative (dv/dx - du/dy)",
            "f": "Paramètre de Coriolis",
        },
        units={"eta": "s⁻¹", "zeta": "s⁻¹", "f": "s⁻¹"},
        description="Somme de la vorticité relative du fluide et de la vorticité géoplanétaire due à la rotation de la Terre.",
        references=["NOAA National Weather Service Technical Manual"],
        limitations=["Valable dans le repère tournant terrestre."],
        compute_func=lambda relative_vorticity, coriolis_f: relative_vorticity + coriolis_f,
    ),
    AtmosphericLaw(
        key="thermal_wind",
        name="Équation du Vent Thermique",
        domain="Dynamique Atmosphérique",
        equation="d(Vg)/d(ln p) = -Rd/f * (k x grad(T))",
        variables={
            "Vg": "Vecteur vent géostrophique",
            "p": "Pression",
            "f": "Paramètre de Coriolis",
            "T": "Température",
        },
        units={"Vg": "m/s", "p": "Pa", "T": "K"},
        description="Relie le cisaillement vertical du vent géostrophique au gradient horizontal de température.",
        references=["Holton & Hakim (2012)", "WMO Synoptic Meteorology Guide"],
        limitations=["Presuppose l'équilibre géostrophique et hydrostatique."],
    ),
]
