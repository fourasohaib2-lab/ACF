def total_feedback(
    self,
    state: ClimateFeedbackState
) -> float:
    """
    Total climate feedback response.

    Includes weighted climate feedback processes.
    """

    ice = self.ice_albedo_feedback(state)

    vapor = self.water_vapor_feedback(state)

    cloud = self.cloud_feedback(state)

    forcing = state.co2_forcing

    ocean = state.ocean_memory

    return (
        ice
        + vapor
        + cloud
        + forcing
        + (0.0 * ocean)
    )
