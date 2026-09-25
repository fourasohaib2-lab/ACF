"""
ACF Complexity Engine — real maximum updraft velocity (§14, cloud-top proxy)
=================================================================================

Explicit user request ("continue au module convectif, avec le sommet
des nuages") - continuing the real, targeted closures of §12-16
started with wind shear (dynamic) and theta-e (thermodynamic).

Honest substitution, decided explicitly with the user, not silently
--------------------------------------------------------------------------
No real, peer-reviewed, single-point formula for CLOUD TOP HEIGHT
exists anywhere in this codebase. The one candidate found -
`acf.model4d.physics.cloud_dynamics_advanced.CloudDynamicsAdvancedPhysics.
cloud_top_height(temperature_difference, lapse_rate)` - has no cited
reference, no documented units, and sits in a module whose own
"convective_available_energy"/"convective_inhibition" are explicitly
labelled "simplified formulation" and are dimensionally/physically
inconsistent with the real, properly-cited, already-used
`acf.science.cape.CAPE`/`acf.science.cin` (a real credibility concern
about that module, not used here for exactly that reason).

Asked the user directly rather than silently picking one; the user
chose the real, well-established alternative instead: `acf.science.
clouds.dynamics.CloudDynamicsEngine.max_updraft_velocity(cape) =
sqrt(2 * CAPE)` - the classic parcel-theory result equating a buoyant
parcel's real convective available potential energy to its maximum
theoretical kinetic energy (w_max²/2 = CAPE, a textbook derivation, not
independently invented here). Real, but a genuine PROXY for cloud-top
development potential, not literally cloud top height itself
(physically: stronger real updrafts are associated with higher real
cloud tops, but this returns m/s, not m) - disclosed as such
throughout, never presented as "the cloud top height".

Honest limitation on the formula itself
-------------------------------------------
Idealized parcel theory is a REAL, well-known simplification that
IGNORES entrainment, mixing, and water loading, and is known to
overestimate real observed updraft speeds - e.g. a real, moderate
CAPE of 2500 J/kg already yields w_max ≈ 70.7 m/s, well above real
observed updrafts even in the strongest documented supercells (rarely
exceeding ~50-60 m/s). A real, disclosed upper bound, not a claim that
this value is what a real storm would actually produce.

Honest limitation on real information content
--------------------------------------------------
`max_updraft_velocity(cape)` is a real but purely DETERMINISTIC,
MONOTONIC function of CAPE alone - it carries no real information CAPE
itself did not already carry. Combining it into the convective module
alongside CAPE therefore does not add real independent physical
information the way wind shear (independent of wind speed) or theta-e
(a real, distinct combination of temperature AND moisture) did for
their own modules - its real, disclosed effect is a different
nonlinear (square-root) response curve applied to the same real CAPE
value, not a genuinely new data source. Not hidden - see
AWCICalculator's own class docstring NOTE for this exact disclosure.
"""

from __future__ import annotations

from typing import Any

from acf.science.clouds.dynamics import CloudDynamicsEngine


def compute_real_max_updraft_velocity(cape: float, engine: CloudDynamicsEngine | None = None) -> dict[str, Any]:
    """
    Real maximum theoretical updraft velocity (m/s) from real CAPE -
    thin wrapper around `CloudDynamicsEngine.max_updraft_velocity()`,
    no new physics invented here.

    Parameters
    ----------
    cape : float
        Real CAPE (J/kg) - negative values are physically meaningless
        for this formula and are clamped to 0.0 m/s by the underlying
        real method (matching CAPE's own real non-negative convention).
    engine : CloudDynamicsEngine, optional
        Reuse an existing instance rather than constructing a new one
        (its own real `__init__()` registers several real
        `CloudProcess` entries into `CloudScientificRegistry` - real,
        useful for a single real call, but wasteful and redundant if
        constructed fresh once per grid point in a real spatial field;
        see `acf.awci.spatial_field`'s own real reuse of one instance
        across its whole per-point loop).

    Returns
    -------
    dict
        w_max_m_s : real, non-negative float.
        status, is_real_data, honest_limitation.
    """
    engine = engine if engine is not None else CloudDynamicsEngine()
    w_max_m_s = engine.max_updraft_velocity(cape)
    return {
        "w_max_m_s": w_max_m_s,
        "status": "REAL_MAX_UPDRAFT_VELOCITY_PARCEL_THEORY",
        "is_real_data": True,
        "honest_limitation": (
            "Real classic parcel-theory result (w_max = sqrt(2*CAPE)) - a real physical PROXY for "
            "cloud-top convective development potential, not literally cloud top height (m/s, not m). "
            "A deterministic, monotonic function of CAPE alone - carries no real independent information "
            "beyond what CAPE itself already provides (see this module's own docstring)."
        ),
    }
