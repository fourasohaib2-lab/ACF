"""
Atmospheric Complexity Framework (ACF)

Global Physical Equation Library Module
(GlobalEquationLibrary containing rigorous mathematical formulations across all physical domains)
"""

from dataclasses import dataclass


@dataclass
class PhysicalEquationEntry:
    """Description canonique d'une équation physique dans la bibliothèque ACF."""

    equation_id: str
    name: str
    category: str
    latex_formula: str
    text_formula: str
    si_units_summary: str
    assumptions: list[str]
    validity_domain: str
    variables_map: dict[str, str]
    scientific_references: list[str]


EQUATION_CATALOG: dict[str, PhysicalEquationEntry] = {
    # ----------------------------------------------------
    # FLUID DYNAMICS & PRIMITIVE EQUATIONS
    # ----------------------------------------------------
    "navier_stokes": PhysicalEquationEntry(
        equation_id="navier_stokes",
        name="Navier-Stokes Momentum Equation",
        category="Fluid Dynamics",
        latex_formula=r"\rho \left( \frac{\partial \mathbf{v}}{\partial t} + \mathbf{v} \cdot \nabla \mathbf{v} \right) = -\nabla p + \rho \mathbf{g} - 2\boldsymbol{\Omega} \times (\rho \mathbf{v}) + \mu \nabla^2 \mathbf{v}",
        text_formula="rho * (dv/dt + v . grad(v)) = -grad(p) + rho*g - 2*Omega x (rho*v) + mu * grad^2(v)",
        si_units_summary="N/m^3 (Force per unit volume)",
        assumptions=["Newtonian fluid", "Continuum hypothesis"],
        validity_domain="Full 3D atmospheric and oceanic fluid dynamics",
        variables_map={
            "rho": "Density (kg/m^3)",
            "v": "Velocity vector (m/s)",
            "p": "Pressure (Pa)",
            "g": "Gravity vector (m/s^2)",
        },
        scientific_references=["Navier (1822)", "Stokes (1845)", "Holton & Hakim (2012)"],
    ),
    "continuity_equation": PhysicalEquationEntry(
        equation_id="continuity_equation",
        name="Mass Continuity Equation",
        category="Fluid Dynamics",
        latex_formula=r"\frac{\partial \rho}{\partial t} + \nabla \cdot (\rho \mathbf{v}) = 0",
        text_formula="d(rho)/dt + div(rho * v) = 0",
        si_units_summary="kg/(m^3 s)",
        assumptions=["Mass conservation", "No mass sources/sinks"],
        validity_domain="All fluid flow regimes",
        variables_map={"rho": "Fluid density (kg/m^3)", "v": "Velocity vector (m/s)"},
        scientific_references=["Euler (1757)", "Gill (1982) Atmosphere-Ocean Dynamics"],
    ),
    "hydrostatic_equation": PhysicalEquationEntry(
        equation_id="hydrostatic_equation",
        name="Hydrostatic Balance Equation",
        category="Thermodynamics & Dynamics",
        latex_formula=r"\frac{\partial p}{\partial z} = -\rho g",
        text_formula="dp/dz = -rho * g",
        si_units_summary="Pa/m",
        assumptions=["Vertical acceleration dw/dt << g", "Hydrostatic approximation"],
        validity_domain="Synoptic scale atmospheric motion (dx > 10 km)",
        variables_map={"p": "Pressure (Pa)", "rho": "Air density (kg/m^3)", "g": "Gravity acceleration (m/s^2)"},
        scientific_references=["WMO Atmospheric Dynamics Guide"],
    ),
    "clausius_clapeyron": PhysicalEquationEntry(
        equation_id="clausius_clapeyron",
        name="Clausius-Clapeyron Vapor Pressure Equation",
        category="Thermodynamics",
        latex_formula=r"\frac{d e_s}{dT} = \frac{L_v \cdot e_s}{R_v \cdot T^2}",
        text_formula="des/dT = (Lv * es) / (Rv * T^2)",
        si_units_summary="Pa/K",
        assumptions=["Phase equilibrium", "Ideal gas behavior for water vapor"],
        validity_domain="Water phase transitions (-50°C to +50°C)",
        variables_map={
            "es": "Saturation vapor pressure (Pa)",
            "Lv": "Latent heat of vaporization (J/kg)",
            "T": "Temperature (K)",
        },
        scientific_references=["Clausius (1850)", "Clapeyron (1834)", "Bohren & Albrecht (1998)"],
    ),
    # ----------------------------------------------------
    # RADIATIVE TRANSFER
    # ----------------------------------------------------
    "stefan_boltzmann": PhysicalEquationEntry(
        equation_id="stefan_boltzmann",
        name="Stefan-Boltzmann Blackbody Radiation Law",
        category="Radiation",
        latex_formula=r"E = \sigma T^4",
        text_formula="E = sigma * T^4",
        si_units_summary="W/m^2",
        assumptions=["Blackbody radiator in thermal equilibrium"],
        validity_domain="Thermal emission calculation for Earth and Sun",
        variables_map={"sigma": "Stefan-Boltzmann constant (5.670374e-8 W/m^2/K^4)", "T": "Absolute temperature (K)"},
        scientific_references=["Stefan (1879)", "Boltzmann (1884)"],
    ),
    "planck_law": PhysicalEquationEntry(
        equation_id="planck_law",
        name="Planck Spectral Radiance Law",
        category="Radiation",
        latex_formula=r"B_\lambda(T) = \frac{2 h c^2}{\lambda^5 \left( e^{\frac{h c}{\lambda k_B T}} - 1 \right)}",
        text_formula="B_lambda(T) = (2*h*c^2 / lambda^5) / (exp(h*c / (lambda*kB*T)) - 1)",
        si_units_summary="W/(m^2 sr m)",
        assumptions=["Blackbody spectral emission"],
        validity_domain="Satellite infrared and solar spectrum radiance retrievals",
        variables_map={
            "h": "Planck constant",
            "c": "Speed of light",
            "kB": "Boltzmann constant",
            "lambda": "Wavelength (m)",
        },
        scientific_references=["Planck (1900)", "Liou (2002) Atmospheric Radiation"],
    ),
    # ----------------------------------------------------
    # TURBULENCE & BOUNDARY LAYER
    # ----------------------------------------------------
    "tke_closure": PhysicalEquationEntry(
        equation_id="tke_closure",
        name="Turbulent Kinetic Energy (TKE) Budget Equation",
        category="Turbulence",
        latex_formula=r"\frac{\partial e}{\partial t} + \mathbf{v}\cdot\nabla e = -\overline{u' w'}\frac{\partial u}{\partial z} + \frac{g}{\theta_0}\overline{w'\theta'} - \frac{\partial \overline{w'e'}}{\partial z} - \varepsilon",
        text_formula="de/dt + v.grad(e) = Shear_Production + Buoyancy_Production - Transport - Dissipation",
        si_units_summary="m^2/s^3 or W/kg",
        assumptions=["Boussinesq approximation", "Horizontally homogeneous turbulence"],
        validity_domain="Atmospheric Boundary Layer (ABL)",
        variables_map={"e": "TKE per unit mass (m^2/s^2)", "epsilon": "Viscous dissipation rate (m^2/s^3)"},
        scientific_references=["Stull (1988) Boundary Layer Meteorology"],
    ),
    # ----------------------------------------------------
    # DATA ASSIMILATION
    # ----------------------------------------------------
    "four_d_var_cost_function": PhysicalEquationEntry(
        equation_id="four_d_var_cost_function",
        name="4D-Var Data Assimilation Cost Function",
        category="Data Assimilation",
        latex_formula=r"J(\mathbf{x}_0) = \frac{1}{2}(\mathbf{x}_0 - \mathbf{x}_b)^T \mathbf{B}^{-1} (\mathbf{x}_0 - \mathbf{x}_b) + \frac{1}{2} \sum_{k=0}^N \left( \mathbf{y}_k - \mathcal{H}_k(\mathcal{M}_k(\mathbf{x}_0)) \right)^T \mathbf{R}_k^{-1} \left( \mathbf{y}_k - \mathcal{H}_k(\mathcal{M}_k(\mathbf{x}_0)) \right)",
        text_formula="J(x0) = 0.5*(x0 - xb)^T * B^-1 * (x0 - xb) + 0.5 * sum((y - H(M(x0)))^T * R^-1 * (y - H(M(x0))))",
        si_units_summary="Dimensionless scalar cost",
        assumptions=["Gaussian error distributions", "Linearized observation operator H"],
        validity_domain="Operational 4D-Var at ECMWF IFS and Météo-France ARPEGE",
        variables_map={
            "xb": "Background state",
            "B": "Background error covariance",
            "R": "Observation error covariance",
        },
        scientific_references=["Courtier et al. (1994) QJRMS", "Rabier et al. (2000) QJRMS"],
    ),
}


class GlobalEquationLibrary:
    """
    Bibliothèque d'équations physiques et mathématiques certifiées d'ACF.
    """

    @classmethod
    def get_equation(cls, eq_id: str) -> PhysicalEquationEntry | None:
        return EQUATION_CATALOG.get(eq_id.lower())

    @classmethod
    def list_equations_by_category(cls, category: str) -> list[PhysicalEquationEntry]:
        return [eq for eq in EQUATION_CATALOG.values() if eq.category.lower() == category.lower()]
