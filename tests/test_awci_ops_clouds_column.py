import numpy as np

from acf.awci.ops.cloud_profile import load_cloud_profile
from acf.awci.ops.clouds import GENUS_CODES, SPECIES_BITS, column_layers, metar_cloud_group

P = load_cloud_profile()
LEVELS = np.array([1000, 925, 850, 700, 600, 500, 400, 300, 250, 200, 150, 100], dtype=float)
GH = 44330.8 * (1 - (LEVELS / 1013.25) ** 0.190263)


def test_two_layers_and_metar_line() -> None:
    frac = np.zeros(12)
    frac[1], frac[4] = 0.7, 1.0
    genus = np.full(12, -1.0)
    genus[1], genus[4] = GENUS_CODES["St"], GENUS_CODES["Ac"]
    species = np.zeros(12)
    species[4] = SPECIES_BITS["castellanus"]  # per-level species: only the Ac layer carries castellanus
    layers = column_layers(LEVELS, frac, genus, GH, 0.0, 1013.0, species, 0.0, np.nan, 500.0, P)
    assert [lay["genus"] for lay in layers] == ["St", "Ac"]
    assert [lay["etage"] for lay in layers] == ["low", "mid"]
    assert layers[0]["amount"] == "BKN" and layers[1]["amount"] == "OVC"
    assert layers[1]["species"] == ["castellanus"] and layers[0]["species"] == []
    assert layers[0]["base_ft"] == int(GH[1] / 0.3048)
    assert metar_cloud_group(layers) == f"BKN{int(GH[1] / 0.3048) // 100:03d} OVC{int(GH[4] / 0.3048) // 100:03d}"


def test_convective_layer_has_unknown_amount_and_cb_suffix() -> None:
    layers = column_layers(LEVELS, np.zeros(12), np.full(12, -1.0), GH, 200.0, 990.0, np.zeros(12), 4.0, GH[9], 900.0, P)
    assert layers == [layers[0]] and layers[0]["kind"] == "convective" and layers[0]["genus"] == "Cb"
    assert layers[0]["species"] == ["capillatus"] and layers[0]["oktas"] is None
    assert metar_cloud_group(layers) == f"///{int(900.0 / 0.3048) // 100:03d}CB"


def test_clear_column_is_nsc() -> None:
    assert column_layers(LEVELS, np.zeros(12), np.full(12, -1.0), GH, 0.0, 1013.0, np.zeros(12), 0.0, np.nan, 500.0, P) == []
    assert metar_cloud_group([]) == "NSC"
