"""
Earth System Physics Core Engine Test Suite (MISSION ACF-DT-001)
"""

import pytest

from acf.earth_physics.atmospheric_dynamics.coriolis import CoriolisParam
from acf.earth_physics.atmospheric_dynamics.geostrophic_balance import GeostrophicBalance
from acf.earth_physics.atmospheric_dynamics.potential_vorticity import ErtelsPotentialVorticity
from acf.earth_physics.atmospheric_dynamics.primitive_equations import AtmosphericPrimitiveEquations
from acf.earth_physics.atmospheric_dynamics.vorticity import VorticityCalculator
from acf.earth_physics.carbon_cycle.carbon_flux import GlobalCarbonFlux
from acf.earth_physics.carbon_cycle.ocean_carbon import OceanCarbonBiologicalPump
from acf.earth_physics.carbon_cycle.terrestrial_carbon import TerrestrialCarbonSink
from acf.earth_physics.coupled_solver.conservation import ConservationEngine
from acf.earth_physics.coupled_solver.earth_solver import EarthSolver
from acf.earth_physics.coupled_solver.timestep_manager import AdaptiveTimestepManager
from acf.earth_physics.cryosphere_physics.glacier_model import GlacierMassBalance
from acf.earth_physics.cryosphere_physics.ice_sheet import IceSheetDynamics
from acf.earth_physics.cryosphere_physics.permafrost import PermafrostThawModel
from acf.earth_physics.cryosphere_physics.sea_ice import SeaIceThermodynamics
from acf.earth_physics.land_surface.albedo import SurfaceAlbedoModel
from acf.earth_physics.land_surface.evapotranspiration import EvapotranspirationModel
from acf.earth_physics.land_surface.soil_model import SoilModel
from acf.earth_physics.land_surface.vegetation import VegetationModel
from acf.earth_physics.ocean_physics.circulation import OceanCirculationModel
from acf.earth_physics.ocean_physics.mixing import OceanVerticalMixing
from acf.earth_physics.ocean_physics.ocean_dynamics import OceanPrimitiveEquations
from acf.earth_physics.ocean_physics.sea_ice_interaction import OceanSeaIceCoupling
from acf.earth_physics.radiation.greenhouse_effect import GreenhouseEffectModel
from acf.earth_physics.radiation.longwave_radiation import LongwaveRadiationModel
from acf.earth_physics.radiation.radiative_balance import RadiativeBalanceSolver
from acf.earth_physics.radiation.solar_radiation import SolarRadiationModel
from acf.earth_physics.thermodynamics.equation_of_state import IdealGasEquationOfState
from acf.earth_physics.thermodynamics.moist_physics import MoistAtmospherePhysics
from acf.earth_physics.thermodynamics.phase_changes import WaterPhaseChanges
from acf.earth_physics.thermodynamics.thermodynamic_equations import ThermodynamicEquations
from acf.hpc.distributed_grid import DistributedGridTopology
from acf.hpc.gpu_acceleration import GPUPhysicsAccelerator
from acf.hpc.mpi_solver import MPIEarthDomainSolver
from acf.hpc.parallel_scheduler import ParallelTaskScheduler


def test_atmospheric_dynamics_core():
    """Test des équations primitives, Coriolis, vorticité et PV d'Ertel."""
    f = CoriolisParam.f_parameter(45.0)
    assert f > 0.0

    du = AtmosphericPrimitiveEquations.solve_momentum(10.0, 5.0, f, 0.01)
    assert "du_dt" in du

    rel_vort = VorticityCalculator.compute_relative_vorticity(0.002, 0.001)
    assert rel_vort == 0.001

    pv = ErtelsPotentialVorticity.compute_pv(f + rel_vort, 0.005)
    assert pv > 0.0

    u_g, v_g = GeostrophicBalance.compute_geostrophic_wind(100.0, -200.0, f)
    assert u_g != 0.0 and v_g != 0.0


def test_thermodynamics_and_radiation():
    """Test de la thermodynamique, de l'état des gaz, du bilan radiatif et du GES."""
    theta = ThermodynamicEquations.potential_temperature(288.15, 85000.0)
    assert theta > 288.15

    rho = IdealGasEquationOfState.density(101325.0, 288.15)
    assert 1.2 < rho < 1.3

    esat = MoistAtmospherePhysics.saturation_vapor_pressure(288.15)
    assert esat > 1000.0

    lh = WaterPhaseChanges.latent_heat_release(1.5)
    assert lh > 0.0

    toa = SolarRadiationModel.top_of_atmosphere_insolation(0.0)
    assert toa == 1361.0

    olr = LongwaveRadiationModel.blackbody_emittance(288.15)
    assert olr > 380.0

    forcing = GreenhouseEffectModel.co2_radiative_forcing(560.0, 280.0)
    assert 3.5 < forcing < 4.0

    net_f = RadiativeBalanceSolver.net_radiative_forcing(340.0, 0.3, 238.0)
    assert net_f == (340.0 * 0.7) - 238.0


def test_ocean_cryosphere_and_land_physics():
    """Test de la physique océanique, cryosphérique et de surface terrestre."""
    p_grad = OceanPrimitiveEquations.hydro_pressure_gradient(1025.0, 10.0)
    assert p_grad > 0.0

    amoc = OceanCirculationModel.amoc_transport_sverdrup()
    assert amoc["amoc_strength_sv"] == 17.5

    # CORRECTED: mixed_layer_depth_m used to always return the
    # hard-coded fake value 45.0 regardless of input. Real MLD needs a
    # density profile or time-integrated bulk model, neither available
    # from (wind_stress, heat_flux) alone - now raises instead of
    # faking precision.
    with pytest.raises(NotImplementedError):
        OceanVerticalMixing.mixed_layer_depth_m(0.1, 100.0)

    heat_ice = OceanSeaIceCoupling.compute_heat_flux_to_ice(2.0)
    assert heat_ice > 0.0

    mass_bal = GlacierMassBalance.net_mass_balance(2.5, 3.0)
    assert mass_bal == -0.5

    slr_contrib = IceSheetDynamics.sea_level_equivalent_contribution(361.8)
    assert slr_contrib == 1.0

    ice_growth = SeaIceThermodynamics.ice_growth_rate_m_s(-10.0)
    assert ice_growth > 0.0

    ch4 = PermafrostThawModel.compute_ch4_emission_megatons(0.5)
    assert ch4 > 0.0

    smi = SoilModel.soil_moisture_index(0.35, 0.45)
    assert 0.7 < smi < 0.8

    lai = VegetationModel.lai_from_ndvi(0.6)
    assert lai > 0.0

    alb = SurfaceAlbedoModel.compute_effective_albedo("Forest", 50.0)
    assert 0.4 < alb < 0.5

    pet = EvapotranspirationModel.potential_evapotranspiration_mm_day(200.0, 25.0)
    assert pet > 0.0


def test_carbon_cycle_and_coupled_solver():
    """Test du cycle du carbone, du résolveur couplé et de la conservation."""
    budget = GlobalCarbonFlux.get_annual_carbon_budget_gtc()
    assert budget["fossil_emissions_gtc_yr"] == 9.8

    uptake = OceanCarbonBiologicalPump.ocean_co2_uptake_rate(420.0, 380.0, 8.0)
    assert uptake > 0.0

    npp = TerrestrialCarbonSink.net_primary_productivity_gtc_yr(15.0, 1000.0)
    assert npp > 0.0

    # CORRECTED: step_forward performs no real computation (no
    # simulation state is even passed in) - used to falsely report
    # "TIMESTEP_SOLVED_CONSERVED" regardless. Now honestly reports it
    # didn't solve anything.
    step_res = EarthSolver.step_forward(3600.0)
    assert step_res["solver_status"] == "PLACEHOLDER_NO_REAL_SOLVE_PERFORMED"
    assert step_res["is_real_data"] is False

    dt_cfl = AdaptiveTimestepManager.compute_cfl_timestep(10000.0, 50.0)
    assert dt_cfl == 100.0

    # CORRECTED: verify_conservation_laws took no before/after state to
    # compare - a "verification" that always passes regardless of what
    # it's checking is a false-assurance bug, worse than no check at
    # all. Now honestly reports it didn't verify anything.
    verif = ConservationEngine.verify_conservation_laws()
    assert verif["conservation_status"] == "NOT_VERIFIED_NO_SIMULATION_STATE_PROVIDED"
    assert verif["mass_conservation_delta_kg"] is None


def test_hpc_and_parallel_acceleration():
    """Test de la sous-couche HPC, MPI et accélération GPU."""
    mpi_topo = MPIEarthDomainSolver.get_mpi_topology(64)
    assert mpi_topo["num_processes"] == 64

    gpu_stat = GPUPhysicsAccelerator.get_gpu_status()
    assert gpu_stat["acceleration_status"] == "CUDA_ACCELERATED"

    halos = DistributedGridTopology.exchange_halos()
    assert halos["status"] == "HALO_EXCHANGE_COMPLETE"

    sched = ParallelTaskScheduler.schedule_tasks(16)
    assert sched["scheduled_tasks_count"] == 16
