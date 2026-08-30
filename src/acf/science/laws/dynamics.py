"""
Atmospheric Dynamics Laws
"""

from acf.science.laws.base_law import AtmosphericLaw
from acf.science.severe_weather import SevereWeather

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
    AtmosphericLaw(
        key="energy_helicity_index",
        name="Energy Helicity Index (EHI)",
        domain="Convection Sévère",
        equation="EHI = CAPE * SRH / 160000",
        variables={"CAPE": "Énergie potentielle convective disponible", "SRH": "Hélicité relative à la tempête"},
        units={"CAPE": "J/kg", "SRH": "m²/s²", "EHI": "sans dimension"},
        description="Combine instabilité et rotation pour évaluer le potentiel de supercellule/tornade.",
        references=["Hart & Korotky (1991), SHARP workstation v1.50 users guide"],
        limitations=["Indice empirique ; ne remplace pas l'analyse complète du profil vertical."],
        compute_func=lambda cape, srh: SevereWeather.energy_helicity_index(cape, srh),
    ),
    AtmosphericLaw(
        key="supercell_composite_parameter",
        name="Supercell Composite Parameter (SCP)",
        domain="Convection Sévère",
        equation="SCP = (muCAPE/1000) * (ESRH/50) * EBWD_term * CIN_term",
        variables={
            "muCAPE": "CAPE de la particule la plus instable",
            "ESRH": "Hélicité relative à la tempête, couche d'afflux effective",
            "EBWD": "Cisaillement effectif du vent en masse",
            "muCIN": "CIN de la particule la plus instable",
        },
        units={"muCAPE": "J/kg", "ESRH": "m²/s²", "EBWD": "m/s", "muCIN": "J/kg", "SCP": "sans dimension"},
        description="SCP > 1 favorise les supercellules cycloniques (droitières) ; SCP < -1 les supercellules anticycloniques.",
        references=["NOAA SPC Mesoanalysis, help_scp.html (formule vérifiée à la source)"],
        limitations=["Nécessite les couches effectives (ESRH/EBWD), pas les couches fixes 0-6km/0-1km."],
        compute_func=lambda mucape, effective_srh, effective_bulk_shear, mucin: (
            SevereWeather.supercell_composite_parameter(mucape, effective_srh, effective_bulk_shear, mucin)
        ),
    ),
    AtmosphericLaw(
        key="significant_tornado_parameter_fixed",
        name="Significant Tornado Parameter (STP, couche fixe)",
        domain="Convection Sévère",
        equation="STP = (SBCAPE/1500) * ((2000-SBLCL)/1000) * (SRH_1km/150) * (Shear_6km/20)",
        variables={
            "SBCAPE": "CAPE de surface",
            "SBLCL": "Altitude du niveau de condensation par ascension, particule de surface",
            "SRH_1km": "Hélicité relative à la tempête 0-1km",
            "Shear_6km": "Cisaillement du vent en masse 0-6km",
        },
        units={"SBCAPE": "J/kg", "SBLCL": "m", "SRH_1km": "m²/s²", "Shear_6km": "m/s", "STP": "sans dimension"},
        description="STP > 1 : potentiel croissant de tornades significatives (EF2+).",
        references=[
            "Thompson, Edwards, Hart, Elmore & Markowski (2003), Wea. Forecasting 18(6), 1243-1261",
            "NOAA SPC Mesoanalysis, help_stpc.html (bornes des termes vérifiées à la source)",
        ],
        limitations=["Variante couche fixe : ne tient pas compte de la CIN (voir variante effective)."],
        compute_func=lambda sbcape, sblcl_m, srh_1km, shear_6km: (
            SevereWeather.significant_tornado_parameter_fixed(sbcape, sblcl_m, srh_1km, shear_6km)
        ),
    ),
    AtmosphericLaw(
        key="significant_tornado_parameter_effective",
        name="Significant Tornado Parameter (STP, couche effective, avec CIN)",
        domain="Convection Sévère",
        equation="STP = (mlCAPE/1500) * ((2000-mlLCL)/1000) * (ESRH/150) * (EBWD/20) * ((200+mlCIN)/150)",
        variables={
            "mlCAPE": "CAPE couche de mélange",
            "mlLCL": "Altitude LCL, particule couche de mélange",
            "ESRH": "Hélicité relative à la tempête, couche d'afflux effective",
            "EBWD": "Cisaillement effectif du vent en masse",
            "mlCIN": "CIN couche de mélange",
        },
        units={"mlCAPE": "J/kg", "mlLCL": "m", "ESRH": "m²/s²", "EBWD": "m/s", "mlCIN": "J/kg", "STP": "sans dimension"},
        description="Variante complète du STP incluant le terme de CIN.",
        references=["NOAA SPC Mesoanalysis, help_stpc.html (formule et bornes vérifiées à la source)"],
        limitations=["Nécessite les couches effectives, pas les couches fixes."],
        compute_func=lambda mlcape, mllcl_m, effective_srh, effective_bulk_shear, mlcin: (
            SevereWeather.significant_tornado_parameter_effective(
                mlcape, mllcl_m, effective_srh, effective_bulk_shear, mlcin
            )
        ),
    ),
]
