from acf.science.severe_weather import SevereWeather


def test_summary():

    result = SevereWeather.summary(
        cape=2500,
        cin=-40,
        shear=28,
        srh=320,
    )

    assert result["cape"] == 2500
    assert result["cin"] == -40
    assert result["bulk_shear"] == 28
    assert result["srh"] == 320
