"""
AWCI Diagnostic Registry (§55)
==================================

docs/ACF_MASTER_PROMPT.md section 55:

    "Chaque diagnostic doit être documenté avec : NAME, DESCRIPTION,
    PHYSICAL MEANING, EQUATION, INPUTS, OUTPUT, UNITS, VALID RANGE,
    ASSUMPTIONS, LIMITATIONS, REFERENCE, TESTS. Aucun 'magic number'
    sans justification."

Found during this session's exhaustive 90-section conformance audit
(reports/ACF_MASTER_AUDIT_v2.md): every real diagnostic this codebase
uses already documents its own name/formula/limitations somewhere -
scattered across each function's own docstring (Normalizer.normalize_*(),
AWCICalculator.calculate_module_scores()/calculate_interaction_scores()),
plus the real scientific-status registry (acf.awci.scientific_status,
built earlier this session, section 77-81) - but never assembled into
one centralized, queryable catalog matching section 55's own exact 12
fields, so answering "what are ALL of ACF's real diagnostics, and is
each one documented per section 55's own checklist" required reading
several files by hand.

Honest scope
-------------
This is a real, additive DOCUMENTATION catalog, not new computation -
every entry describes a real, already-existing formula (verified
against the actual source, not invented here) and never changes any
of them. Covers the diagnostics AWCICalculator's own DEFAULT pipeline
actually uses (the module-input normalizations, the 2 module-
combination formulas, the 2 default interaction terms, the real
uncertainty method) - not every function in acf.science's much larger
library (hundreds of modules, most unrelated to AWCI's own default
scoring path - see §12-16 of this same audit for that separate, real,
disclosed gap between AWCI's simple module set and the richer Science
Engine).

Each entry's `reference` field is honest about what it is: a real
citation for an EXTERNALLY-VALIDATED formula (e.g. Cohen 1960), or - far
more often in this composite index - an explicit "ACF design choice,
not derived from a published formula" for the many entries where that
is simply true (matching the same disclosure already present in each
formula's own docstring/acf.awci.scientific_status entry - never
invented fresh here). `status` cross-references
acf.awci.scientific_status directly (a real function call, not a
duplicated status string) so this catalog can never silently drift out
of sync with the actual scientific-status registry.
"""

from __future__ import annotations

from dataclasses import dataclass

from acf.awci.scientific_status import (
    CLIMATOLOGY_NORMALIZATION_METHOD_STATUS,
    INTERACTION_WEIGHT_STATUS,
    MODULE_WEIGHT_STATUS,
    NORMALIZER_RANGE_STATUS,
    UNCERTAINTY_METHOD_STATUS,
    ThresholdStatus,
    WeightStatusEntry,
)


@dataclass(frozen=True)
class DiagnosticSpec:
    """Real, structured documentation for one real diagnostic formula
    this codebase's AWCI pipeline actually uses - exactly the 12
    fields docs/ACF_MASTER_PROMPT.md section 55 requires (`status`
    added as a 13th, cross-referencing acf.awci.scientific_status
    rather than duplicating it - see module docstring)."""

    name: str
    description: str
    physical_meaning: str
    equation: str
    inputs: list[str]
    output: str
    units: str
    valid_range: str
    assumptions: str
    limitations: str
    reference: str
    tests: list[str]
    #: Cross-referenced from acf.awci.scientific_status - never a
    #: separately hand-written status string that could silently drift
    #: from the real registry.
    status: ThresholdStatus | WeightStatusEntry


DIAGNOSTIC_REGISTRY: dict[str, DiagnosticSpec] = {
    "normalize_wind": DiagnosticSpec(
        name="normalize_wind",
        description="Normalizes surface wind speed to [0, 1] for the dynamic module.",
        physical_meaning="Higher wind speed contributes more to dynamic complexity.",
        equation="clip(value, 0, 50) / 50",
        inputs=["wind_speed (m/s)"],
        output="dynamic module input, [0, 1]",
        units="m/s -> dimensionless",
        valid_range="0 to 50 m/s",
        assumptions="Linear scaling - no physical saturation curve applied.",
        limitations="Naive min-max, not climatology/percentile-based (docs/ACF_MASTER_PROMPT.md section 20 - "
        "see Normalizer.normalize_percentile() for the real, opt-in alternative built for this exact limitation).",
        reference="ACF design choice - not sourced from a specific climatology (Normalizer's own docstring).",
        tests=["tests/test_awci_calculator.py::test_normalizer_methods"],
        status=NORMALIZER_RANGE_STATUS["wind"],
    ),
    "normalize_wind_shear": DiagnosticSpec(
        name="normalize_wind_shear",
        description="Real, opt-in normalization of bulk wind shear magnitude to [0, 1] - feeds the dynamic "
        "module alongside wind speed when a real value is supplied (added 2026-09-03, explicit user request "
        "'commence par le module dynamique, avec le cisaillement de vent').",
        physical_meaning="Higher vertical wind shear contributes to dynamic complexity (docs/ACF_MASTER_PROMPT.md "
        "section 12 explicitly lists 'cisaillement vertical' among the dynamic module's own candidate variables).",
        equation="clip(value, 0, 50) / 50",
        inputs=["wind_shear (m/s) - see acf.awci.wind_shear.compute_real_wind_shear_at_point() for the real formula that produces it"],
        output="dynamic module input (50% weight when supplied - see dynamic_module_combination below), [0, 1]",
        units="m/s -> dimensionless",
        valid_range="0 to 50 m/s",
        assumptions="Same envelope as normalize_wind, for internal consistency - linear scaling, no physical saturation curve.",
        limitations="Real bulk shear across whatever native model levels were supplied, not a fixed physical "
        "layer (e.g. 0-6 km) - see acf.awci.wind_shear's own module docstring.",
        reference="ACF design choice - same envelope as normalize_wind, not sourced from a specific climatology.",
        tests=["tests/test_awci_calculator_wind_shear.py", "tests/test_awci_wind_shear.py"],
        status=NORMALIZER_RANGE_STATUS["wind_shear"],
    ),
    "normalize_temperature": DiagnosticSpec(
        name="normalize_temperature",
        description="Normalizes air temperature to [0, 1] for the thermodynamic module.",
        physical_meaning="Temperature extremes (either direction from the [-30, 50] degC envelope) increase thermodynamic complexity.",
        equation="T_c = value - 273.15 (if Kelvin); clip(T_c, -30, 50); (T_c + 30) / 80",
        inputs=["temperature (K, or degC via is_kelvin=False)"],
        output="thermodynamic module input (before combining with humidity), [0, 1]",
        units="K or degC -> dimensionless",
        valid_range="-30 to +50 degC",
        assumptions="Linear scaling across the full envelope, not a real freezing/heat-stress threshold curve.",
        limitations="Naive min-max, plausible global extremes, not sourced per region/season (same real "
        "limitation as normalize_wind).",
        reference="ACF design choice - plausible global extremes, not climatologically sourced (Normalizer's own docstring).",
        tests=["tests/test_awci_calculator.py::test_normalizer_methods"],
        status=NORMALIZER_RANGE_STATUS["temperature"],
    ),
    "normalize_humidity": DiagnosticSpec(
        name="normalize_humidity",
        description="Normalizes specific humidity to [0, 1] - feeds the thermodynamic module alongside temperature.",
        physical_meaning="Higher moisture content contributes to thermodynamic complexity (alongside temperature).",
        equation="clip(value, 0, 0.03) / 0.03",
        inputs=["specific_humidity (kg/kg)"],
        output="thermodynamic module input (before combining with temperature), [0, 1]",
        units="kg/kg -> dimensionless",
        valid_range="0 to 0.03 kg/kg",
        assumptions="Linear scaling; 0.03 kg/kg envelope covers very warm/humid tropical surface conditions.",
        limitations="Naive min-max, not sourced from a specific climatology.",
        reference="ACF design choice - plausible but not sourced (Normalizer's own docstring).",
        tests=["tests/test_awci_calculator.py::test_normalizer_methods"],
        status=NORMALIZER_RANGE_STATUS["humidity"],
    ),
    "normalize_theta_e": DiagnosticSpec(
        name="normalize_theta_e",
        description="Real, opt-in normalization of equivalent potential temperature (theta-e) to [0, 1] - "
        "REPLACES (not blends with) the naive temperature/humidity combination in the thermodynamic module "
        "when a real value is supplied (added 2026-09-03, explicit user request 'continue au module "
        "thermodynamique, avec theta-e').",
        physical_meaning="Theta-e is a real, physically complete single measure of an air parcel's combined "
        "thermal and moisture energy content (docs/ACF_MASTER_PROMPT.md section 13 explicitly lists "
        "'température potentielle équivalente' among the thermodynamic module's own candidate variables).",
        equation="clip(value_k, 250, 380) / 130  (after subtracting 250: (clip(value_k,250,380)-250)/130)",
        inputs=["theta_e (K) - see acf.awci.theta_e.compute_real_theta_e_at_point() for the real Bolton (1980) formula that produces it"],
        output="thermodynamic module score directly (see thermodynamic_module_combination below for the real replace-not-blend disclosure), [0, 1]",
        units="K -> dimensionless",
        valid_range="250 to 380 K",
        assumptions="Linear scaling across a real, generously wide operational envelope, for internal "
        "consistency with the other Normalizer ranges.",
        limitations="The underlying real theta-e VALUE uses the CONFIRMED, published Bolton (1980) formula - "
        "only this normalization RANGE's own bounds are HYPOTHESIS (not sourced from a specific climatology), "
        "same as every other Normalizer range in this registry.",
        reference="Normalization range: ACF design choice. Underlying theta-e formula: Bolton, D. (1980), "
        "'The Computation of Equivalent Potential Temperature', Monthly Weather Review 108(7), 1046-1053 - a "
        "real, published, operationally standard formula (also used by MetPy/SHARPpy), not invented here.",
        tests=["tests/test_awci_calculator_theta_e.py", "tests/test_awci_theta_e.py"],
        status=NORMALIZER_RANGE_STATUS["theta_e"],
    ),
    "normalize_cape": DiagnosticSpec(
        name="normalize_cape",
        description="Normalizes CAPE to [0, 1] for the convective module.",
        physical_meaning="Higher convective available potential energy indicates higher convective POTENTIAL - "
        "docs/ACF_MASTER_PROMPT.md section 14 explicitly warns never to confuse this with GUARANTEED convection.",
        equation="clip(value, 0, 5000) / 5000",
        inputs=["cape (J/kg)"],
        output="convective module input (70% weight in the module combination), [0, 1]",
        units="J/kg -> dimensionless",
        valid_range="0 to 5000 J/kg",
        assumptions="Linear scaling across a plausible extreme-CAPE envelope.",
        limitations="Real potential, not real observed/predicted convection (section 14's own explicit distinction, "
        "not enforced elsewhere in the calculation itself).",
        reference="ACF design choice - plausible extreme CAPE, not sourced from a specific climatology (Normalizer's own docstring).",
        tests=["tests/test_awci_calculator.py::test_normalizer_methods"],
        status=NORMALIZER_RANGE_STATUS["cape"],
    ),
    "normalize_updraft_velocity": DiagnosticSpec(
        name="normalize_updraft_velocity",
        description="Real, opt-in normalization of maximum theoretical updraft velocity to [0, 1] - BLENDS "
        "into the convective module's own CAPE/CIN combination when a real value is supplied (added "
        "2026-09-03, explicit user request 'continue au module convectif, avec le sommet des nuages').",
        physical_meaning="A real physical PROXY for cloud-top convective development potential (docs/"
        "ACF_MASTER_PROMPT.md section 14 lists 'hauteur/sommet des nuages' among the convective module's own "
        "candidate variables) - not literally cloud top height itself (m/s, not m). No real, peer-reviewed "
        "single-point cloud-top-HEIGHT formula exists in this codebase (the one candidate found was uncited "
        "and sat alongside a CAPE/CIN duplicate inconsistent with the real one used here); the user was asked "
        "directly and chose this real, well-established parcel-theory alternative instead.",
        equation="clip(value_m_s, 0, 70) / 70",
        inputs=["updraft_velocity (m/s) - see acf.awci.updraft.compute_real_max_updraft_velocity() for the "
        "real w_max=sqrt(2*CAPE) classic parcel-theory formula that produces it"],
        output="convective module input (50% weight when supplied - see convective_module_combination below), [0, 1]",
        units="m/s -> dimensionless",
        valid_range="0 to 70 m/s",
        assumptions="Linear scaling across a real, generously wide envelope covering both real observed "
        "extreme-storm updrafts and idealized parcel theory's own known tendency to overestimate.",
        limitations="w_max=sqrt(2*CAPE) is a real, classic, textbook parcel-theory result, but a purely "
        "DETERMINISTIC, MONOTONIC function of CAPE alone - it carries no real independent information beyond "
        "what CAPE itself already provides (honest disclosure, unlike normalize_wind_shear/normalize_theta_e "
        "above - see convective_module_combination below and acf.awci.updraft's own module docstring).",
        reference="Normalization range: ACF design choice. Underlying formula: classic parcel theory "
        "(w_max^2/2 = CAPE, a textbook derivation - acf.science.clouds.dynamics.CloudDynamicsEngine."
        "max_updraft_velocity()), not invented here.",
        tests=["tests/test_awci_updraft.py", "tests/test_awci_calculator_updraft.py"],
        status=NORMALIZER_RANGE_STATUS["updraft_velocity"],
    ),
    "normalize_cin": DiagnosticSpec(
        name="normalize_cin",
        description="Normalizes the magnitude of CIN to [0, 1] - feeds the convective module alongside CAPE.",
        physical_meaning="Higher convective inhibition magnitude contributes to convective-module complexity.",
        equation="clip(|value|, 0, 500) / 500",
        inputs=["cin (J/kg, sign-agnostic - absolute value taken)"],
        output="convective module input (30% weight in the module combination), [0, 1]",
        units="J/kg -> dimensionless",
        valid_range="0 to 500 J/kg (absolute value)",
        assumptions="Linear scaling on |CIN|; sign is discarded (CIN is conventionally negative or zero).",
        limitations="Naive min-max, not sourced from a specific climatology.",
        reference="ACF design choice - plausible, not sourced (Normalizer's own docstring).",
        tests=["tests/test_awci_calculator.py::test_normalizer_methods"],
        status=NORMALIZER_RANGE_STATUS["cin"],
    ),
    "normalize_precipitation": DiagnosticSpec(
        name="normalize_precipitation",
        description="Normalizes precipitation rate to [0, 1] for the microphysical module.",
        physical_meaning="Higher precipitation rate contributes to microphysical complexity.",
        equation="clip(value, 0, 50) / 50",
        inputs=["precipitation (mm/h)"],
        output="microphysical module input, [0, 1]",
        units="mm/h -> dimensionless",
        valid_range="0 to 50 mm/h",
        assumptions="Linear scaling across a plausible extreme-rate envelope.",
        limitations="Precipitation RATE only - see normalize_precipitation_phase_severity below (added "
        "2026-09-03) for the real, opt-in precipitation PHASE signal section 15 also names "
        "('hydrométéores'); hail/eau surfondue/contenu en glace remain real, disclosed, still-open gaps "
        "(this session's own exhaustive audit, section 15 - no real per-column hydrometeor species exist in "
        "CoupledEarthSolver's state to derive them from without fabrication).",
        reference="ACF design choice - plausible extreme rate, not sourced (Normalizer's own docstring).",
        tests=["tests/test_awci_calculator.py::test_normalizer_methods"],
        status=NORMALIZER_RANGE_STATUS["precipitation"],
    ),
    "normalize_precipitation_phase_severity": DiagnosticSpec(
        name="normalize_precipitation_phase_severity",
        description="Real, opt-in normalization (identity clamp) of ACF-assigned surface precipitation-phase "
        "severity to [0, 1] - BLENDS into the microphysical module's own precipitation-rate score when a real "
        "value is supplied (added 2026-09-03, continuing the §12-16 module-extension work after wind shear, "
        "theta-e, and maximum updraft velocity).",
        physical_meaning="Surface precipitation PHASE (rain/snow/wet snow/freezing rain) is a real, distinct "
        "aviation-operational hazard axis from precipitation RATE (docs/ACF_MASTER_PROMPT.md section 15 "
        "explicitly lists 'hydrométéores' among the microphysical module's own candidate variables) - freezing "
        "rain/ice pellets in particular is a real, well-documented severe aircraft-icing hazard regardless of "
        "rate.",
        equation="clip(value, 0, 1)",
        inputs=["precipitation_phase_severity ([0, 1]) - see acf.awci.hydrometeor_phase."
        "compute_real_hydrometeor_phase_at_point() for the real formula chain (Stull 2011 wet-bulb "
        "temperature composed with the real, self-disclosed HydrometeorType.classify() heuristic) and "
        "acf.awci.hydrometeor_phase.PHASE_SEVERITY for the real, disclosed ACF phase->severity ranking that "
        "produces it"],
        output="microphysical module input (50% weight when supplied - see microphysical_module_combination "
        "below), [0, 1]",
        units="dimensionless (already [0, 1] by construction)",
        valid_range="0 to 1",
        assumptions="The clip is a real safety net for an out-of-range caller-supplied value, not a real "
        "independent physical scaling - `value` already IS the target [0, 1] range by construction.",
        limitations="The underlying real phase CLASSIFICATION is itself an explicitly self-disclosed surface-"
        "only HEURISTIC (acf.science.precipitation.HydrometeorType's own docstring: 'NOT a single validated "
        "physical formula' - cannot reliably separate freezing rain from ice pellets/sleet without a real "
        "vertical-profile method like Bourgouin 2000, not implemented here). The phase->severity RANKING order "
        "reflects a real, well-documented aviation icing-hazard fact; the exact numeric values (0.2/0.5/0.7/1.0) "
        "are still an ACF design choice, not a published severity index.",
        reference="Underlying phase classification: a real, published wet-bulb approximation (Stull, R. (2011), "
        "'Wet-Bulb Temperature from Relative Humidity and Air Temperature', Journal of Applied Meteorology and "
        "Climatology) composed with a real, self-disclosed heuristic (HydrometeorType.classify()). "
        "Phase->severity ranking: ACF design choice grounded in real aviation-operational icing-hazard "
        "knowledge (see acf.awci.hydrometeor_phase's own module docstring), not a published numeric index.",
        tests=["tests/test_awci_hydrometeor_phase.py", "tests/test_awci_calculator_precipitation_phase.py"],
        status=NORMALIZER_RANGE_STATUS["precipitation_phase_severity"],
    ),
    "normalize_topographic": DiagnosticSpec(
        name="normalize_topographic",
        description="Normalizes altitude to [0, 1] for the topographic module.",
        physical_meaning="Higher terrain altitude contributes to topographic-module complexity - a real, but "
        "static, proxy (section 16 explicitly wants relief to be a dynamic wind/turbulence MODIFIER, only "
        "partially captured today via the real wind_topo_interaction term - see that entry below).",
        equation="clip(value, 0, max_altitude) / max_altitude   (max_altitude defaults to 3000 m)",
        inputs=["altitude (m)"],
        output="topographic module input, [0, 1]",
        units="m -> dimensionless",
        valid_range="0 to 3000 m (default, caller-overridable via max_altitude)",
        assumptions="Linear scaling; a static altitude value, not a real dynamic relief-modifier of wind/turbulence.",
        limitations="Section 16's own real gap: relief as a static altitude proxy, not yet the dynamic modifier "
        "(orographic waves, wind acceleration) the master prompt describes.",
        reference="ACF design choice, caller-overridable (Normalizer's own docstring).",
        tests=["tests/test_awci_calculator.py::test_normalizer_methods"],
        status=NORMALIZER_RANGE_STATUS["topographic"],
    ),
    "normalize_confidence": DiagnosticSpec(
        name="normalize_confidence",
        description="Normalizes forecast confidence percentage to [0, 1] for the confidence (forecast) module.",
        physical_meaning="Lower confidence -> higher forecast-uncertainty contribution (1 - normalize_confidence(...) "
        "is what calculate_module_scores() actually uses).",
        equation="clip(value, 0, 100) / 100",
        inputs=["confidence (%)"],
        output="confidence module input (before the 1 - x inversion), [0, 1]",
        units="% -> dimensionless",
        valid_range="0 to 100%",
        assumptions="None beyond the unit definition itself.",
        limitations="None beyond forecast_score's own general limitations (see AWCICalculator's class docstring).",
        reference="A real, exact unit definition (0-100%), not an empirical choice - the one CONFIRMED entry in the "
        "whole real Normalizer range registry.",
        tests=["tests/test_awci_calculator.py::test_normalizer_methods"],
        status=NORMALIZER_RANGE_STATUS["confidence"],
    ),
    "normalize_percentile": DiagnosticSpec(
        name="normalize_percentile",
        description="Real empirical percentile-rank normalization against a caller-supplied climatological sample "
        "(docs/ACF_MASTER_PROMPT.md section 20's own real, opt-in alternative to the naive min-max functions above).",
        physical_meaning="A value's normalized complexity contribution reflects where it actually falls within a "
        "REAL local/seasonal climatology, not a generic global envelope.",
        equation="count(sample <= value) / len(sample)",
        inputs=["value (native units)", "climatology (list of real historical values, same native units)"],
        output="empirical percentile rank, [0, 1] (0.5 when climatology is empty - a real, documented neutral default)",
        units="native units -> dimensionless",
        valid_range="N/A - rank-based, not a fixed physical range",
        assumptions="The supplied climatology sample is representative of the real local/seasonal context the "
        "caller cares about - not verified by this function itself.",
        limitations="No built-in season/region/altitude stratification - the caller must pre-filter the sample "
        "(acf.awci.calculator's own AWCICalculator._normalize() docstring, section 20).",
        reference="Real, standard statistical technique (empirical CDF) - see "
        "acf.awci.scientific_status.CLIMATOLOGY_NORMALIZATION_METHOD_STATUS for this METHOD's own real status "
        "as an AWCI application choice among section 20's several listed alternatives.",
        tests=[
            "tests/test_awci_calculator.py::test_normalizer_percentile_empty_climatology_is_neutral",
            "tests/test_awci_calculator.py::test_normalizer_percentile_known_ranking",
            "tests/test_awci_calculator_climatology_normalization.py",
        ],
        status=CLIMATOLOGY_NORMALIZATION_METHOD_STATUS,
    ),
    "dynamic_module_combination": DiagnosticSpec(
        name="dynamic_module_combination",
        description="Combines normalized wind speed with normalized wind shear (when supplied) into the "
        "dynamic module score - added 2026-09-03, explicit user request 'commence par le module dynamique, "
        "avec le cisaillement de vent'.",
        physical_meaning="Dynamic complexity is driven by wind speed alone by default; when a real bulk wind "
        "shear value is supplied, it is weighted equally alongside wind speed (section 12's own explicit "
        "'cisaillement vertical' candidate variable).",
        equation="normalize_wind(wind_speed) if 'wind_shear' not in data else "
        "0.5 * normalize_wind(wind_speed) + 0.5 * normalize_wind_shear(wind_shear)",
        inputs=["wind_speed (m/s)", "wind_shear (m/s, optional)"],
        output="dynamic module score, [0, 1]",
        units="dimensionless",
        valid_range="[0, 1]",
        assumptions="Equal 50/50 weighting when wind_shear is supplied - a real, disclosed ACF design choice, "
        "matching the same internal convention as the thermodynamic module's own 50/50 temperature/humidity "
        "blend, not derived from a published formula for this composite index. Omitting wind_shear entirely "
        "keeps the dynamic module wind-speed-only - zero behavior change for every caller that doesn't supply it.",
        limitations="Real bulk shear only (magnitude between two levels) - not gradients/variability/vertical "
        "structure/temporal evolution/relief-convection-stability interactions section 12 also names as real "
        "candidate dynamic-module study directions (this session's own audit, sections 12-16 - a real, disclosed "
        "gap, not claimed closed by this one addition).",
        reference="ACF design choice - not derived from a published formula.",
        tests=["tests/test_awci_calculator_wind_shear.py"],
        status=MODULE_WEIGHT_STATUS["dynamic"],
    ),
    "thermodynamic_module_combination": DiagnosticSpec(
        name="thermodynamic_module_combination",
        description="Combines normalized temperature and humidity into the thermodynamic module score by "
        "default, or REPLACES that blend with real, opt-in equivalent potential temperature (theta-e, added "
        "2026-09-03) when a caller supplies one.",
        physical_meaning="Thermodynamic complexity depends on both temperature and moisture, weighted equally "
        "by default; theta-e, when supplied, is a real, physically complete single quantity already combining "
        "both (section 13's own explicit candidate variable).",
        equation="if 'theta_e' not in data: 0.5 * normalize_temperature(temperature) + 0.5 * normalize_humidity(specific_humidity); "
        "else: normalize_theta_e(theta_e)",
        inputs=["temperature (K)", "specific_humidity (kg/kg)", "theta_e (K, optional)"],
        output="thermodynamic module score, [0, 1]",
        units="dimensionless",
        valid_range="[0, 1]",
        assumptions="Equal 50/50 weighting between temperature and humidity in the default case - no real "
        "physical derivation combines them that way. Theta-e REPLACES rather than blends with this default "
        "combination when supplied - additively stacking it would double-count the same underlying "
        "temperature/humidity information theta-e already incorporates (a real, disclosed design choice).",
        limitations="Default case: a simple linear blend, not a real thermodynamic diagnostic. Opt-in theta-e "
        "case: a real single-point value, not a real vertical theta-e gradient/advection diagnostic (section "
        "12-16's own broader, still-open scope) - see normalize_theta_e's own entry for the real, published "
        "Bolton (1980) reference behind the theta-e value itself.",
        reference="Default combination: ACF design choice, not derived from a published formula. Theta-e "
        "replacement: see normalize_theta_e's own reference.",
        tests=["tests/test_awci_calculator.py::test_calculate_module_scores", "tests/test_awci_calculator_theta_e.py"],
        status=MODULE_WEIGHT_STATUS["thermodynamic"],
    ),
    "convective_module_combination": DiagnosticSpec(
        name="convective_module_combination",
        description="Combines normalized CAPE and CIN into the convective module score by default, and BLENDS "
        "in real, opt-in maximum updraft velocity (added 2026-09-03) alongside that CAPE/CIN combination when "
        "a caller supplies one.",
        physical_meaning="Convective complexity is driven primarily by available energy (CAPE), moderated by "
        "inhibition (CIN); maximum updraft velocity, when supplied, is a real physical PROXY for cloud-top "
        "development potential (section 14's own explicit candidate variable) that this combination weighs "
        "equally alongside the CAPE/CIN base.",
        equation="cape_cin_base = 0.7 * normalize_cape(cape) + 0.3 * normalize_cin(cin); "
        "if 'updraft_velocity' not in data: cape_cin_base; "
        "else: 0.5 * cape_cin_base + 0.5 * normalize_updraft_velocity(updraft_velocity)",
        inputs=["cape (J/kg)", "cin (J/kg)", "updraft_velocity (m/s, optional)"],
        output="convective module score, [0, 1]",
        units="dimensionless",
        valid_range="[0, 1]",
        assumptions="70/30 CAPE/CIN weighting, then 50/50 with updraft_velocity when supplied - real, disclosed "
        "ACF design choices, not derived from a published formula. Unlike wind_shear/theta_e in the other two "
        "modules, updraft_velocity is a deterministic, monotonic function of CAPE alone (w_max=sqrt(2*CAPE)) - "
        "blending it in therefore adds a real nonlinear response curve applied to the same CAPE value, not "
        "genuinely independent information (honestly disclosed, not hidden - see normalize_updraft_velocity's "
        "own entry and acf.awci.updraft's own module docstring). Omitting updraft_velocity entirely keeps the "
        "convective module exactly the CAPE/CIN blend - zero behavior change for every caller that doesn't "
        "supply it.",
        limitations="Does not distinguish convective POTENTIAL from real observed/forecast convection (section "
        "14's own explicit warning). Opt-in updraft_velocity case: a real physical proxy for cloud-top "
        "development potential, not literally cloud top height (m/s, not m) - no real, peer-reviewed "
        "single-point cloud-top-HEIGHT formula exists in this codebase (see normalize_updraft_velocity's own "
        "entry for why this substitution was made, explicitly with the user).",
        reference="ACF design choice - not derived from a published formula.",
        tests=["tests/test_awci_calculator.py::test_calculate_module_scores", "tests/test_awci_calculator_updraft.py"],
        status=MODULE_WEIGHT_STATUS["convective"],
    ),
    "microphysical_module_combination": DiagnosticSpec(
        name="microphysical_module_combination",
        description="Normalizes precipitation rate into the microphysical module score by default, and BLENDS "
        "in real, opt-in precipitation-phase severity (added 2026-09-03) alongside that rate when a caller "
        "supplies one.",
        physical_meaning="Microphysical complexity is driven by precipitation rate by default; precipitation "
        "PHASE, when supplied, is a real, genuinely independent aviation-operational hazard axis (section 15's "
        "own explicit 'hydrométéores' candidate variable) - phase is not a deterministic function of rate, "
        "unlike updraft_velocity/CAPE in the convective module.",
        equation="precip_norm = normalize_precipitation(precipitation); "
        "if 'precipitation_phase_severity' not in data: precip_norm; "
        "else: 0.5 * precip_norm + 0.5 * normalize_precipitation_phase_severity(precipitation_phase_severity)",
        inputs=["precipitation (mm/h)", "precipitation_phase_severity ([0, 1], optional)"],
        output="microphysical module score, [0, 1]",
        units="dimensionless",
        valid_range="[0, 1]",
        assumptions="50/50 weighting when precipitation_phase_severity is supplied - a real, disclosed ACF "
        "design choice, matching the same internal convention as the dynamic module's own 50/50 wind/wind_shear "
        "blend, not derived from a published formula for this composite index. Omitting "
        "precipitation_phase_severity entirely keeps the microphysical module exactly the precipitation-rate-"
        "only score - zero behavior change for every caller that doesn't supply it.",
        limitations="Real precipitation rate and real, self-disclosed surface phase heuristic only - hail size, "
        "supercooled liquid water content, and ice content (section 15's own other explicit candidate "
        "variables) remain real, disclosed, still-open gaps (no real per-column hydrometeor species exist in "
        "CoupledEarthSolver's state to derive them from without fabrication - see "
        "normalize_precipitation_phase_severity's own entry).",
        reference="ACF design choice - not derived from a published formula.",
        tests=["tests/test_awci_calculator.py::test_calculate_module_scores", "tests/test_awci_calculator_precipitation_phase.py"],
        status=MODULE_WEIGHT_STATUS["microphysical"],
    ),
    "wind_topo_interaction": DiagnosticSpec(
        name="wind_topo_interaction",
        description="Real, general interaction-term engine's default pairwise term (docs/ACF_MASTER_PROMPT.md section 22).",
        physical_meaning="Strong wind over complex terrain produces disproportionately more turbulence/mountain-"
        "wave complexity than either factor alone would suggest.",
        equation="module_scores['dynamic'] * module_scores['topographic']",
        inputs=["dynamic module score [0, 1]", "topographic module score [0, 1]"],
        output="interaction score, [0, 1]",
        units="dimensionless",
        valid_range="[0, 1]",
        assumptions="A real, defensible physical pairing (wind x relief), combined by simple multiplication - "
        "not derived from a published interaction formula for this composite index.",
        limitations="One of only 2 real interaction terms active by default - the real, general engine "
        "(AWCICalculator.__init__()'s own interaction_terms/interaction_weights parameters) supports more, "
        "including higher-order terms, but none are enabled by default (section 22's own explicit warning "
        "against inventing untested interaction terms).",
        reference="ACF design choice - not derived from an external published formula (AWCICalculator's own docstring).",
        tests=[
            "tests/test_awci_calculator.py::test_calculate_interaction_scores_directly",
            "tests/test_awci_calculator_interaction_engine.py",
        ],
        status=INTERACTION_WEIGHT_STATUS["wind_topo_interaction"],
    ),
    "conv_thermo_interaction": DiagnosticSpec(
        name="conv_thermo_interaction",
        description="Real, general interaction-term engine's second default pairwise term (section 22).",
        physical_meaning="Strong convective potential compounded with strong thermodynamic instability increases "
        "severe-convection complexity faster than a linear sum of the two module scores.",
        equation="module_scores['convective'] * module_scores['thermodynamic']",
        inputs=["convective module score [0, 1]", "thermodynamic module score [0, 1]"],
        output="interaction score, [0, 1]",
        units="dimensionless",
        valid_range="[0, 1]",
        assumptions="Same real disclosure as wind_topo_interaction - a defensible pairing, simple multiplication, "
        "not a published formula for this index.",
        limitations="Same as wind_topo_interaction.",
        reference="ACF design choice - not derived from an external published formula (AWCICalculator's own docstring).",
        tests=[
            "tests/test_awci_calculator.py::test_calculate_interaction_scores_directly",
            "tests/test_awci_calculator_interaction_engine.py",
        ],
        status=INTERACTION_WEIGHT_STATUS["conv_thermo_interaction"],
    ),
    "calculate_with_uncertainty": DiagnosticSpec(
        name="calculate_with_uncertainty",
        description="Real per-realization AWCI recomputation from real ensemble/multi-model data (section 64).",
        physical_meaning="A single AWCI score without context can hide real forecast disagreement - re-scoring "
        "each real ensemble/model realization independently reveals the real spread across that disagreement.",
        equation="{calculate(data | {variable: values[i] for each variable, values in realizations}) for i in range(n)}, "
        "then real sample mean/std/min/max/class-probabilities over the n real resulting scores",
        inputs=["data (same as calculate())", "ensemble_members and/or model_realizations: dict[str, list[float]]"],
        output="awci_mean/awci_std/awci_min/awci_max/awci_member_scores/awci_class_probabilities",
        units="AWCI points (0-100) and dimensionless class fractions",
        valid_range="awci_* in [0, 100]; class probabilities in [0, 1], summing to 1.0",
        assumptions="Each supplied realization is independently substituted into an otherwise-unchanged real "
        "scenario - no covariance/correlation between simultaneously-varying real variables is modeled.",
        limitations="Requires at least 2 real realizations to produce a real distribution - honestly reports "
        "uncertainty_available=False otherwise, never a fabricated band from confidence alone (section 61).",
        reference="Real per-realization substitution is a real, defensible ACF design choice - not an externally "
        "validated or published uncertainty-quantification technique for this composite index.",
        tests=["tests/test_awci_calculator_uncertainty.py"],
        status=UNCERTAINTY_METHOD_STATUS,
    ),
}


def get_diagnostic(name: str) -> DiagnosticSpec:
    """Real lookup by name.

    Raises
    ------
    KeyError
        If `name` isn't a real, registered diagnostic - never a guessed default.
    """
    return DIAGNOSTIC_REGISTRY[name]


def list_diagnostic_names() -> list[str]:
    """Real, sorted list of every diagnostic name this registry documents."""
    return sorted(DIAGNOSTIC_REGISTRY)
