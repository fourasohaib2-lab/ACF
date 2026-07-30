"""
Applied Mathematics & Numerical Methods Laws
"""

from acf.science.laws.base_law import AtmosphericLaw

MATHEMATICAL_LAWS = [
    AtmosphericLaw(
        key="vector_gradient",
        name="Gradient Vectoriel",
        domain="Mathématiques Appliquées",
        equation="grad(phi) = (dphi/dx, dphi/dy, dphi/dz)",
        variables={
            "phi": "Champ scalaire atmosphérique (pression, température, géopotentiel)",
            "grad(phi)": "Vecteur gradient caractérisant la variation spatiale maximale",
        },
        units={"phi": "variable", "grad(phi)": "variable/m"},
        description="Opérateur différentiel mesurant le taux et la direction de variation spatiale maximale d'un champ scalaire.",
        references=["WMO Numerical Weather Prediction Manual", "Arfken & Weber (2005) Mathematical Methods"],
        limitations=["Domaine spatial continu et dérivable."],
        compute_func=lambda dphi_dx, dphi_dy, dphi_dz=0.0: (dphi_dx, dphi_dy, dphi_dz),
    ),
    AtmosphericLaw(
        key="vector_divergence",
        name="Divergence Vectorielle",
        domain="Mathématiques Appliquées",
        equation="div(V) = du/dx + dv/dy + dw/dz",
        variables={"V": "Vecteur vitesse (u, v, w)", "div(V)": "Taux d'expansion ou de compression volumique"},
        units={"V": "m/s", "div(V)": "s⁻¹"},
        description="Opérateur mesurant le flux net de matière fluide sortant d'un volume élémentaire.",
        references=["Holton & Hakim (2012)", "WMO Technical Manual"],
        limitations=["Dérivabilité spatiale du champ de vent."],
        compute_func=lambda du_dx, dv_dy, dw_dz=0.0: du_dx + dv_dy + dw_dz,
    ),
    AtmosphericLaw(
        key="vector_curl",
        name="Rotationnel Vectoriel",
        domain="Mathématiques Appliquées",
        equation="curl(V) = (dw/dy - dv/dz, du/dz - dw/dx, dv/dx - du/dy)",
        variables={"V": "Champ de vent (u, v, w)", "curl(V)": "Vecteur rotationnel de circulation fluide"},
        units={"V": "m/s", "curl(V)": "s⁻¹"},
        description="Opérateur mesurant la tendance à la rotation locale (vorticité) d'un fluide en mouvement.",
        references=["Arfken & Weber (2005)", "ECMWF Dynamics Documentation"],
        limitations=["Champ vectoriel continu."],
        compute_func=lambda du_dx, du_dy, du_dz, dv_dx, dv_dy, dv_dz, dw_dx, dw_dy, dw_dz: (
            dw_dy - dv_dz,
            du_dz - dw_dx,
            dv_dx - du_dy,
        ),
    ),
    AtmosphericLaw(
        key="bilinear_interpolation",
        name="Interpolation Bilinéaire Spatiale",
        domain="Mathématiques Appliquées",
        equation="f(x,y) = (1-t)*(1-u)*f00 + t*(1-u)*f10 + (1-t)*u*f01 + t*u*f11",
        variables={
            "f00, f10, f01, f11": "Valeurs aux 4 sommets de la maille",
            "t, u": "Coordonnées relatives normalisées [0, 1]",
        },
        units={"f": "variable", "t, u": "dimensionless"},
        description="Méthode d'interpolation spatiale régulière 2D pour ré-échantillonner des champs météorologiques sur grille.",
        references=["WMO Grid Data Processing Guidelines", "Press et al. (2007) Numerical Recipes"],
        limitations=["Présuppose une variation linéaire le long des axes de grille."],
        compute_func=lambda f00, f10, f01, f11, t, u: (
            (1 - t) * (1 - u) * f00 + t * (1 - u) * f10 + (1 - t) * u * f01 + t * u * f11
        ),
    ),
]
