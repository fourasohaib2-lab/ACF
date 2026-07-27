"""
ACF - Atmospheric Complexity Framework

Sprint 9.26
Tests - Atmospheric Thermodynamics Engine
"""


from acf.model4d.physics.thermodynamics import (
    Thermodynamics,
    ThermodynamicsState
)



# ============================================================
# Test atmospheric state
# ============================================================

def create_state():

    return ThermodynamicsState(
        temperature=300,
        pressure=90000,
        specific_humidity=0.012,
        height=1000
    )



# ============================================================
# Potential temperature
# ============================================================

def test_potential_temperature():

    model = Thermodynamics()

    theta = model.potential_temperature(
        create_state()
    )

    assert theta > 300



# ============================================================
# Virtual temperature
# ============================================================

def test_virtual_temperature():

    model = Thermodynamics()

    tv = model.virtual_temperature(
        create_state()
    )

    assert tv > 300



# ============================================================
# Density
# ============================================================

def test_air_density():

    model = Thermodynamics()

    rho = model.air_density(
        create_state()
    )

    assert rho > 0



# ============================================================
# Dry static energy
# ============================================================

def test_dry_static_energy():

    model = Thermodynamics()

    value = model.dry_static_energy(
        create_state()
    )

    assert value > 300000



# ============================================================
# Moist static energy
# ============================================================

def test_moist_static_energy():

    model = Thermodynamics()

    value = model.moist_static_energy(
        create_state()
    )

    assert value > 300000



# ============================================================
# Enthalpy
# ============================================================

def test_enthalpy():

    model = Thermodynamics()

    value = model.enthalpy(
        create_state()
    )

    assert value > 300000



# ============================================================
# Internal energy
# ============================================================

def test_internal_energy():

    model = Thermodynamics()

    value = model.internal_energy(
        create_state()
    )

    assert value > 200000



# ============================================================
# Dry adiabatic lapse rate
# ============================================================

def test_adiabatic_lapse_rate():

    model = Thermodynamics()

    value = model.adiabatic_lapse_rate()

    assert value > 0



# ============================================================
# Moist lapse rate
# ============================================================

def test_moist_adiabatic_lapse_rate():

    model = Thermodynamics()

    value = model.moist_adiabatic_lapse_rate(
        create_state()
    )

    assert value > 0



# ============================================================
# Lifting condensation level
# ============================================================

def test_lifting_condensation_level():

    model = Thermodynamics()

    value = model.lifting_condensation_level(
        30,
        20
    )

    assert value == 1250



# ============================================================
# Brunt Vaisala frequency
# ============================================================

def test_brunt_vaisala_frequency():

    model = Thermodynamics()

    value = model.brunt_vaisala_frequency(
        0.01
    )

    assert value > 0



# ============================================================
# CAPE
# ============================================================

def test_cape():

    model = Thermodynamics()

    value = model.convective_available_potential_energy(
        305,
        295,
        1000
    )

    assert value > 0



# ============================================================
# CIN
# ============================================================

def test_cin():

    model = Thermodynamics()

    value = model.convective_inhibition(
        2,
        1000
    )

    assert value < 0



# ============================================================
# Stability index
# ============================================================

def test_stability_index():

    model = Thermodynamics()

    value = model.stability_index(
        300,
        310,
        1000
    )

    assert value == 0.01
