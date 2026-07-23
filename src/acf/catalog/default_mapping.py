from acf.catalog.parameter_mapper import ParameterMapper


def create_default_mapper():

    mapper = ParameterMapper()

    ########################################
    # Temperature
    ########################################

    mapper.register(
        "t2m",
        "T2",
        "TMP",
        "TMP_2m",
        "2T",
        "air_temperature",
        "t_2m"
    )

    ########################################
    # Dew Point
    ########################################

    mapper.register(
        "d2m",
        "TD2",
        "dewpoint",
        "dew_point_temperature"
    )

    ########################################
    # Pressure
    ########################################

    mapper.register(
        "mslp",
        "MSL",
        "PRMSL",
        "MeanSeaLevelPressure"
    )

    ########################################
    # Wind
    ########################################

    mapper.register(
        "u10",
        "U10",
        "UGRD",
        "u_wind_10m"
    )

    mapper.register(
        "v10",
        "V10",
        "VGRD",
        "v_wind_10m"
    )

    ########################################
    # Humidity
    ########################################

    mapper.register(
        "rh",
        "RH",
        "RelativeHumidity"
    )

    mapper.register(
        "q",
        "QVAPOR",
        "specific_humidity"
    )

    ########################################
    # Rain
    ########################################

    mapper.register(
        "tp",
        "RAIN",
        "RAINC",
        "RAINNC",
        "precipitation"
    )

    return mapper
