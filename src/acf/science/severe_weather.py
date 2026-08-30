"""
Severe Weather Engine
=====================

Composite severe-convection indices combining instability (CAPE/CIN),
vertical wind shear and storm-relative helicity (SRH).

All formulas below were verified against SPC's (NOAA Storm Prediction
Center) official mesoanalysis parameter definitions and/or Hart &
Korotky (1991), not reconstructed from memory alone.

References:
    Hart, J. A., & Korotky, W. (1991). "The SHARP workstation v1.50
    users guide". NWS.
    Thompson, R. L., Edwards, R., Hart, J. A., Elmore, K. L., &
    Markowski, P. (2003). "Close Proximity Soundings within Supercell
    Environments Obtained from the Rapid Update Cycle". Wea.
    Forecasting, 18(6), 1243-1261.
    NOAA SPC Mesoanalysis: Supercell Composite Parameter (SCP) —
    https://www.spc.noaa.gov/exper/mesoanalysis/help/help_scp.html
    NOAA SPC Mesoanalysis: Significant Tornado Parameter (STP) —
    https://www.spc.noaa.gov/exper/mesoanalysis/help/help_stpc.html
"""


class SevereWeather:
    """
    Severe weather diagnostic engine.

    NOTE on parcel types: the composite formulas below (SCP, STP) are
    officially defined using specific parcel choices (most-unstable
    CAPE/CIN for SCP, mixed-layer CAPE/CIN/LCL for STP) and specific
    layers (effective-inflow SRH/shear, or fixed 0-1km/0-6km layers
    for the STP "fixed" variant). This module's public API takes
    generic cape/cin/shear/srh scalars — callers are responsible for
    supplying the parcel/layer values appropriate to the variant they
    are computing (documented per method). No profile-level physics
    (e.g. deriving effective-inflow layers automatically) is done
    here; that belongs in science/radiosonde.py once available.
    """

    @staticmethod
    def energy_helicity_index(cape: float, srh: float) -> float:
        """
        Energy Helicity Index (EHI): EHI = CAPE * SRH / 160000.

        Parameters
        ----------
        cape : float
            CAPE (J/kg), any parcel (commonly SBCAPE or MLCAPE).
        srh : float
            Storm-relative helicity (m^2/s^2) over the layer of choice
            (commonly 0-1 km or 0-3 km).

        Returns
        -------
        float
            EHI (dimensionless). Rule of thumb: >1 some tornado
            potential, >2-2.5 significant potential (SPC guidance).

        Reference
        ---------
        Hart & Korotky (1991).
        """
        return (cape * srh) / 160000.0

    @staticmethod
    def supercell_composite_parameter(
        mucape: float,
        effective_srh: float,
        effective_bulk_shear: float,
        mucin: float,
    ) -> float:
        """
        Supercell Composite Parameter (SCP), per SPC definition.

        SCP = (muCAPE/1000) * (ESRH/50) * (EBWD_term) * (CIN_term)

        Term rules (verified against SPC mesoanalysis help page):
          - EBWD_term: 0 if effective_bulk_shear < 10 m/s;
                       effective_bulk_shear/20 if 10-20 m/s;
                       1.0 if > 20 m/s (capped).
          - CIN_term:  1.0 if mucin > -40 J/kg;
                       otherwise -40/mucin.

        Parameters
        ----------
        mucape : float
            Most-unstable CAPE (J/kg).
        effective_srh : float
            Effective-inflow-layer storm-relative helicity (m^2/s^2).
        effective_bulk_shear : float
            Effective bulk wind difference (m/s).
        mucin : float
            Most-unstable CIN (J/kg, negative or zero).

        Returns
        -------
        float
            SCP (dimensionless). >1 favors right-moving supercells,
            <-1 favors left-moving (anticyclonic) supercells.

        Reference
        ---------
        NOAA SPC Mesoanalysis help_scp.html.
        """
        if effective_bulk_shear < 10.0:
            ebwd_term = 0.0
        elif effective_bulk_shear > 20.0:
            ebwd_term = 1.0
        else:
            ebwd_term = effective_bulk_shear / 20.0

        cin_term = 1.0 if mucin > -40.0 else -40.0 / mucin

        return (mucape / 1000.0) * (effective_srh / 50.0) * ebwd_term * cin_term

    @staticmethod
    def significant_tornado_parameter_fixed(
        sbcape: float,
        sblcl_m: float,
        srh_1km: float,
        shear_6km: float,
    ) -> float:
        """
        Significant Tornado Parameter, fixed-layer variant (no CIN term).

        STP_fixed = (SBCAPE/1500) * ((2000-SBLCL)/1000) * (SRH_1km/150) * (Shear_6km/20)

        Term rules:
          - LCL_term: 1.0 if sblcl_m < 1000 m; 0.0 if sblcl_m > 2000 m;
                      otherwise (2000-sblcl_m)/1000.
          - Shear_term: 0.0 if shear_6km < 12.5 m/s;
                        1.5 if shear_6km > 30 m/s (capped);
                        otherwise shear_6km/20.

        Parameters
        ----------
        sbcape : float
            Surface-based CAPE (J/kg).
        sblcl_m : float
            Surface-based lifting condensation level height (m AGL).
        srh_1km : float
            0-1 km storm-relative helicity (m^2/s^2).
        shear_6km : float
            0-6 km bulk wind shear (m/s).

        Returns
        -------
        float
            STP (dimensionless). >1 increasing potential for
            significant (EF2+) tornadoes (SPC guidance).

        Reference
        ---------
        Thompson, Edwards, Hart, Elmore & Markowski (2003), Wea.
        Forecasting 18(6), 1243-1261. Same LCL/shear capping
        convention as SPC's effective-layer STP formula (verified),
        applied here to the fixed-layer inputs per the original 2003
        formulation.
        """
        if sblcl_m < 1000.0:
            lcl_term = 1.0
        elif sblcl_m > 2000.0:
            lcl_term = 0.0
        else:
            lcl_term = (2000.0 - sblcl_m) / 1000.0

        if shear_6km < 12.5:
            shear_term = 0.0
        elif shear_6km > 30.0:
            shear_term = 1.5
        else:
            shear_term = shear_6km / 20.0

        return (sbcape / 1500.0) * lcl_term * (srh_1km / 150.0) * shear_term

    @staticmethod
    def significant_tornado_parameter_effective(
        mlcape: float,
        mllcl_m: float,
        effective_srh: float,
        effective_bulk_shear: float,
        mlcin: float,
    ) -> float:
        """
        Significant Tornado Parameter, effective-layer variant (with CIN).

        STP = (mlCAPE/1500) * ((2000-mlLCL)/1000) * (ESRH/150) * (EBWD/20) * ((200+mlCIN)/150)

        Term rules (verified against SPC mesoanalysis help page):
          - LCL_term:  1.0 if mllcl_m < 1000 m; 0.0 if mllcl_m > 2000 m;
                       otherwise (2000-mllcl_m)/1000.
          - EBWD_term: 0.0 if effective_bulk_shear < 12.5 m/s;
                       1.5 if effective_bulk_shear > 30 m/s (capped);
                       otherwise effective_bulk_shear/20.
          - CIN_term:  1.0 if mlcin > -50 J/kg;
                       0.0 if mlcin < -200 J/kg;
                       otherwise (200+mlcin)/150.

        Parameters
        ----------
        mlcape : float
            Mixed-layer CAPE (J/kg).
        mllcl_m : float
            Mixed-layer LCL height (m AGL).
        effective_srh : float
            Effective-inflow-layer storm-relative helicity (m^2/s^2).
        effective_bulk_shear : float
            Effective bulk wind difference (m/s).
        mlcin : float
            Mixed-layer CIN (J/kg, negative or zero).

        Returns
        -------
        float
            STP (dimensionless).

        Reference
        ---------
        NOAA SPC Mesoanalysis help_stpc.html.
        """
        if mllcl_m < 1000.0:
            lcl_term = 1.0
        elif mllcl_m > 2000.0:
            lcl_term = 0.0
        else:
            lcl_term = (2000.0 - mllcl_m) / 1000.0

        if effective_bulk_shear < 12.5:
            ebwd_term = 0.0
        elif effective_bulk_shear > 30.0:
            ebwd_term = 1.5
        else:
            ebwd_term = effective_bulk_shear / 20.0

        if mlcin > -50.0:
            cin_term = 1.0
        elif mlcin < -200.0:
            cin_term = 0.0
        else:
            cin_term = (200.0 + mlcin) / 150.0

        return (mlcape / 1500.0) * lcl_term * (effective_srh / 150.0) * ebwd_term * cin_term

    @staticmethod
    def classify_threat(ehi: float, scp: float, stp: float | None) -> str:
        """
        Qualitative threat classification from composite index values.

        Thresholds follow standard SPC interpretive guidance (SCP>1
        favors supercells, STP>1 increasing significant-tornado
        potential, EHI>1 some rotational potential). This is a coarse
        summary label, not a substitute for full sounding analysis.
        """
        if stp is not None and stp >= 3.0:
            return "Extreme tornado potential"
        if stp is not None and stp >= 1.0:
            return "Significant tornado potential"
        if scp >= 1.0:
            return "Supercells favored"
        if ehi >= 1.0:
            return "Some rotational potential"
        return "Low organized-severe potential"

    @staticmethod
    def summary(
        cape: float,
        cin: float,
        shear: float,
        srh: float,
        lcl_m: float | None = None,
    ) -> dict:
        """
        Aggregate severe-weather diagnostic summary.

        Backward compatible: the original 4 keys (cape, cin,
        bulk_shear, srh) are always present and unchanged. New keys
        are added: ehi, scp, stp (None if lcl_m not supplied),
        threat_level.

        The generic cape/cin/shear/srh inputs are used as-is for all
        three composite indices (i.e. treated simultaneously as
        MU-parcel for SCP and as SB/ML-parcel for STP, and shear/srh
        as if they were the appropriate effective/fixed layer for
        each). This is an intentional simplification of this
        aggregate convenience method — for rigorously correct parcel-
        specific composites, call energy_helicity_index(),
        supercell_composite_parameter() and
        significant_tornado_parameter_fixed()/_effective() directly
        with the correct per-formula inputs.

        Parameters
        ----------
        cape : float
            CAPE (J/kg).
        cin : float
            CIN (J/kg, negative or zero).
        shear : float
            Bulk wind shear / effective bulk wind difference (m/s).
        srh : float
            Storm-relative helicity (m^2/s^2).
        lcl_m : float, optional
            LCL height (m AGL). If omitted, "stp" is None (STP needs
            an LCL height that summary()'s original signature did not
            carry).

        Returns
        -------
        dict
        """
        ehi = SevereWeather.energy_helicity_index(cape, srh)
        scp = SevereWeather.supercell_composite_parameter(cape, srh, shear, cin)
        stp = (
            SevereWeather.significant_tornado_parameter_fixed(cape, lcl_m, srh, shear)
            if lcl_m is not None
            else None
        )

        return {
            "cape": cape,
            "cin": cin,
            "bulk_shear": shear,
            "srh": srh,
            "ehi": round(ehi, 2),
            "scp": round(scp, 2),
            "stp": round(stp, 2) if stp is not None else None,
            "threat_level": SevereWeather.classify_threat(ehi, scp, stp),
        }
