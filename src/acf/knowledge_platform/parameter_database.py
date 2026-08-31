"""
Atmospheric Complexity Framework (ACF)

Global Meteorological Parameter Database Module
(GlobalParameterDatabase containing exhaustive 28-field schemas for all meteorological domains)
"""

from acf.knowledge_platform.parameter_schema import MeteorologicalParameterSchema

PARAMETERS_DB: dict[str, MeteorologicalParameterSchema] = {
    # ----------------------------------------------------
    # 1. ATMOSPHERIC STATE
    # ----------------------------------------------------
    "temperature": MeteorologicalParameterSchema(
        key="temperature",
        domain="Atmospheric State",
        official_scientific_name="Air Temperature",
        alternative_names=["Dry Bulb Temperature", "Ambience Temperature"],
        wmo_code="012001",
        cf_convention_name="air_temperature",
        grib2_identifier="0,0,0",
        netcdf_variable="ta",
        bufr_descriptor="0 12 001",
        si_units="K",
        dimensions="[K]",
        valid_ranges="180.0 K to 330.0 K",
        physical_meaning="Measure of the average kinetic energy of dry air molecules.",
        mathematical_definition=r"T = \frac{p}{\rho R_d}",
        full_governing_equations=r"\frac{dT}{dt} = \frac{1}{\rho c_p} \frac{dp}{dt} + \frac{Q}{c_p} + \text{Diff}",
        conservation_equations=r"\rho c_p \left( \frac{\partial T}{\partial t} + \mathbf{v}\cdot\nabla T \right) = \omega + Q",
        diagnostic_equations=r"T = T_v / (1 + 0.61 q)",
        empirical_formulations=["Magnus-Tetens formula", "Goff-Gratch equation"],
        numerical_approximations=["Spectral spherical harmonics TCo1279", "Finite volume AROME 1.3km"],
        model_implementation=["ECMWF IFS", "Météo-France AROME", "DWD ICON", "NOAA GFS"],
        dependencies=["pressure", "density"],
        derived_variables=["potential_temperature", "virtual_temperature", "dew_point"],
        scientific_references=["WMO-No. 8", "Bohren & Albrecht (1998) Atmospheric Thermodynamics"],
        operational_usage="Core state variable for all NWP systems and surface synoptic observations.",
        quality_control_procedures=["Plausibility Check (-90°C to +60°C)", "Spatial Buddy Check"],
        visualization_recommendations="Isotherms contour lines & Color shade palette (Blue to Red)",
        typical_thresholds={"Freezing": "273.15 K", "Heatwave": "308.15 K"},
        forecast_applications=["Surface frost forecasting", "Thermal advection analysis"],
        climate_applications=["Global mean surface temperature anomaly (IPCC AR6)"],
        machine_learning_applications=["GraphCast / GenCast 3D temperature field prediction"],
    ),
    "potential_temperature": MeteorologicalParameterSchema(
        key="potential_temperature",
        domain="Atmospheric State",
        official_scientific_name="Potential Temperature",
        alternative_names=["Theta"],
        wmo_code="012002",
        cf_convention_name="air_potential_temperature",
        grib2_identifier="0,0,2",
        netcdf_variable="theta",
        bufr_descriptor="0 12 002",
        si_units="K",
        dimensions="[K]",
        valid_ranges="200.0 K to 500.0 K",
        physical_meaning="Temperature an air parcel would attain if brought adiabatically to reference pressure 1000 hPa.",
        mathematical_definition=r"\theta = T \left(\frac{p_0}{p}\right)^{R_d/c_p}",
        full_governing_equations=r"\frac{d\theta}{dt} = \frac{\theta}{c_p T} Q",
        conservation_equations=r"\frac{d\theta}{dt} = 0 \quad (\text{for dry adiabatic flow})",
        diagnostic_equations=r"\theta = T (1000/p)^{0.286}",
        empirical_formulations=["Poisson equation for dry air"],
        numerical_approximations=["Conservative dry mass coordinate solver"],
        model_implementation=["IFS", "AROME", "ICON", "WRF"],
        dependencies=["temperature", "pressure"],
        derived_variables=["equivalent_potential_temperature", "brunt_vaisala_frequency"],
        scientific_references=["Poisson (1823)", "Holton & Hakim (2012)"],
        operational_usage="Used for atmospheric stability profiling and isentropic analysis.",
        quality_control_procedures=["Isentropic monotonic increase check with altitude"],
        visualization_recommendations="Isentropic surfaces cross-section",
        typical_thresholds={"Inversion": "dTheta/dz > 0"},
        forecast_applications=["Frontal surface identification", "Gravity wave propagation"],
        climate_applications=["Stratospheric circulation dynamics"],
        machine_learning_applications=["Physics-informed neural networks (PINN) loss constraint"],
    ),
    # ----------------------------------------------------
    # 2. DYNAMICS
    # ----------------------------------------------------
    "relative_vorticity": MeteorologicalParameterSchema(
        key="relative_vorticity",
        domain="Dynamics",
        official_scientific_name="Relative Vorticity",
        alternative_names=["Vertical Vorticity", "Zeta"],
        wmo_code="011041",
        cf_convention_name="atmosphere_relative_vorticity",
        grib2_identifier="0,2,12",
        netcdf_variable="vo",
        bufr_descriptor="0 11 041",
        si_units="s^-1",
        dimensions="[T⁻¹]",
        valid_ranges="-1.0e-3 s^-1 to +1.0e-3 s^-1",
        physical_meaning="Local rotation rate of the horizontal wind field about a vertical axis.",
        mathematical_definition=r"\zeta = \frac{\partial v}{\partial x} - \frac{\partial u}{\partial y}",
        full_governing_equations=r"\frac{d(\zeta + f)}{dt} = -(\zeta + f)\nabla \cdot \mathbf{v}_h + \mathbf{k}\cdot\left(\frac{\partial \mathbf{v}}{\partial z} \times \nabla w\right)",
        conservation_equations=r"\frac{d\eta}{dt} = 0 \quad (\text{Barotropic non-divergent})",
        diagnostic_equations=r"\zeta = \nabla^2 \psi",
        empirical_formulations=["Finite difference curl calculation"],
        numerical_approximations=["Spectral derivative calculation in spherical harmonics"],
        model_implementation=["ECMWF IFS", "Météo-France ARPEGE", "NOAA GFS"],
        dependencies=["u_component", "v_component"],
        derived_variables=["absolute_vorticity", "potential_vorticity"],
        scientific_references=["Rossby (1939)", "Holton & Hakim (2012)"],
        operational_usage="Identification of cyclonic troughs, shortwaves, and jet streak dynamics.",
        quality_control_procedures=["Spatial smoothing filter check"],
        visualization_recommendations="Vorticity advection overlay on 500 hPa geopotential height",
        typical_thresholds={"Cyclonic": "> 1.0e-4 s^-1"},
        forecast_applications=["Cyclogenesis prediction", "Supercell mesocyclone detection"],
        climate_applications=["Synoptic storm track climatology"],
        machine_learning_applications=["Neural vorticity field surrogates"],
    ),
    # ----------------------------------------------------
    # 3. CONVECTION
    # ----------------------------------------------------
    "cape": MeteorologicalParameterSchema(
        key="cape",
        domain="Convection",
        official_scientific_name="Convective Available Potential Energy",
        alternative_names=["CAPE", "Convective Instability Energy"],
        wmo_code="013011",
        cf_convention_name="atmosphere_convective_available_potential_energy",
        grib2_identifier="0,7,6",
        netcdf_variable="cape",
        bufr_descriptor="0 13 011",
        si_units="J/kg",
        dimensions="[L² T⁻²]",
        valid_ranges="0.0 J/kg to 6000.0 J/kg",
        physical_meaning="Vertical integral of positive buoyant energy exerted on a rising parcel from LFC to EL.",
        mathematical_definition=r"\text{CAPE} = \int_{z_{\text{LFC}}}^{z_{\text{EL}}} g \frac{T_{v,\text{parcel}} - T_{v,\text{env}}}{T_{v,\text{env}}} dz",
        full_governing_equations=r"w_{\text{max}} = \sqrt{2 \cdot \text{CAPE}}",
        conservation_equations=r"\Delta E_k = \text{CAPE} - \text{Entrainment Losses}",
        diagnostic_equations=r"\text{CAPE} \approx g \sum \frac{\Delta T_v}{T_v} \Delta z",
        empirical_formulations=["Bolton (1980) pseudo-adiabatic parcel ascent"],
        numerical_approximations=["Vertical integration over discrete pressure levels"],
        model_implementation=["IFS", "AROME", "HRRR", "GFS"],
        dependencies=["temperature", "humidity", "pressure"],
        derived_variables=["maximum_updraft_speed", "significant_severe_parameter"],
        scientific_references=["Moncrieff & Green (1972)", "Emanuel (1994)"],
        operational_usage="Core convective storm severity and thunderstorm probability index.",
        quality_control_procedures=["Comparison with surface moisture values"],
        visualization_recommendations="Color shaded map (1000 to 4000+ J/kg) & Skew-T diagram plot",
        typical_thresholds={"Moderate": "1000 J/kg", "Extreme": "2500 J/kg"},
        forecast_applications=["Severe hail and tornado outbreak forecasting"],
        climate_applications=["Convective instability trends under global warming"],
        machine_learning_applications=["Severe weather risk classification models"],
    ),
    # ----------------------------------------------------
    # 4. OCEANOGRAPHY
    # ----------------------------------------------------
    "sea_surface_temperature": MeteorologicalParameterSchema(
        key="sea_surface_temperature",
        domain="Oceanography",
        official_scientific_name="Sea Surface Temperature",
        alternative_names=["SST", "Skin Temperature Ocean"],
        wmo_code="022011",
        cf_convention_name="sea_surface_temperature",
        grib2_identifier="10,3,0",
        netcdf_variable="sst",
        bufr_descriptor="0 22 011",
        si_units="K",
        dimensions="[K]",
        valid_ranges="271.15 K to 315.0 K",
        physical_meaning="Water temperature close to the ocean surface (skin and foundation SST).",
        mathematical_definition=r"Q_{\text{net}} = Q_{sw} - Q_{lw} - Q_{lh} - Q_{sh}",
        full_governing_equations=r"\rho_w c_w \frac{\partial \text{SST}}{\partial t} = \frac{\partial F_z}{\partial z}",
        conservation_equations=r"\frac{d}{dt} \int \rho_w c_w T dz = \text{Surface Heat Fluxes}",
        diagnostic_equations=r"\text{SST}_{\text{skin}} = \text{SST}_{\text{bulk}} - \Delta T_{\text{cool\_skin}}",
        empirical_formulations=["Fairall et al. (1996) Cool skin model"],
        numerical_approximations=["NEMO 1/12° ocean model grid"],
        model_implementation=["CMEMS", "NEMO", "HYCOM", "ECMWF Ocean"],
        dependencies=["radiation", "wind_speed"],
        derived_variables=["ocean_heat_content", "oni_index"],
        scientific_references=["Donlon et al. (2002)", "IPCC AR6 WG1"],
        operational_usage="Coupled ocean-atmosphere forecasting, tropical cyclone intensification.",
        quality_control_procedures=["SST anomaly sanity check vs climatology"],
        visualization_recommendations="Color gradient palette with 26°C tropical cyclone threshold isotherm",
        typical_thresholds={"Tropical Cyclonogenesis": "300.15 K (27°C)"},
        forecast_applications=["Hurricane track and intensity forecasting"],
        climate_applications=["ENSO Monitoring & Global Warming Trend Indicator"],
        machine_learning_applications=["Neural SST spatial reconstruction"],
    ),
    # ----------------------------------------------------
    # 5. HYDROLOGY
    # ----------------------------------------------------
    "river_discharge": MeteorologicalParameterSchema(
        key="river_discharge",
        domain="Hydrology",
        official_scientific_name="River Discharge",
        alternative_names=["Streamflow", "Volumetric Flow Rate"],
        wmo_code="013060",
        cf_convention_name="water_volume_transport_in_river_channel",
        grib2_identifier="1,0,3",
        netcdf_variable="dis",
        bufr_descriptor="0 13 060",
        si_units="m^3/s",
        dimensions="[L³ T⁻¹]",
        valid_ranges="0.0 m^3/s to 300000.0 m^3/s",
        physical_meaning="Volume of water passing through a river cross-section per unit time.",
        mathematical_definition=r"Q = A \cdot v_{\text{mean}}",
        full_governing_equations=r"\frac{\partial A}{\partial t} + \frac{\partial Q}{\partial x} = q_{\text{lateral}}",
        conservation_equations=r"\text{Saint-Venant 1D Equations (Continuity + Momentum)}",
        diagnostic_equations=r"Q = \frac{1}{n} A R_h^{2/3} S_0^{1/2} \quad (\text{Manning-Strickler})",
        empirical_formulations=["Stage-Discharge Rating Curve Q = a(H-H0)^b"],
        numerical_approximations=["LISFLOOD kinematic wave solver", "HEC-RAS 2D finite volume"],
        model_implementation=["EFAS", "GloFAS", "LISFLOOD", "HEC-RAS", "VIC"],
        dependencies=["runoff", "precipitation"],
        derived_variables=["flood_inundation_depth", "flood_return_period"],
        scientific_references=["Chow (1959) Open-Channel Hydraulics", "Van Der Knijff (2010)"],
        operational_usage="Early warning flood forecasting and water resources management.",
        quality_control_procedures=["Physical bounds check vs rating curve"],
        visualization_recommendations="Hydrograph time-series and river network thickness coding",
        typical_thresholds={"Bankfull Flood": "Q > Q_10_year"},
        forecast_applications=["River flood risk alert generation"],
        climate_applications=["Global freshwater runoff trend analysis"],
        machine_learning_applications=["LSTM River Discharge Surrogate Model"],
    ),
}


class GlobalParameterDatabase:
    """
    Base de données scientifique universelle contenant la totalité des paramètres d'ACF.
    """

    @classmethod
    def get(cls, key: str) -> MeteorologicalParameterSchema | None:
        """Retourne le schéma complet d'un paramètre par sa clé."""
        return PARAMETERS_DB.get(key.lower())

    @classmethod
    def list_all_keys(cls) -> list[str]:
        """Retourne toutes les clés de paramètres enregistrées."""
        return list(PARAMETERS_DB.keys())

    @classmethod
    def get_by_domain(cls, domain: str) -> list[MeteorologicalParameterSchema]:
        """Filtre les paramètres par domaine scientifique."""
        return [p for p in PARAMETERS_DB.values() if p.domain.lower() == domain.lower()]
