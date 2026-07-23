import pytest

from acf.science.bulk_richardson_number import (
    BulkRichardsonNumber,
)


def test_brn():

    value = BulkRichardsonNumber.calculate(
        cape=2000,
        shear=20,
    )

    assert value == pytest.approx(10.0)


def test_zero_shear():

    with pytest.raises(ValueError):
        BulkRichardsonNumber.calculate(
            cape=1000,
            shear=0,
        )


def test_category():

    assert BulkRichardsonNumber.category(5) == "Weak"

    assert BulkRichardsonNumber.category(25) == "Supercell"

    assert BulkRichardsonNumber.category(60) == "Multicell"
