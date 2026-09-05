"""
Real responsive-sizing regression test for acf.gui.esoc.view_manager.

QComboBox's default `AdjustToContentsOnFirstShow` size-adjust policy
makes its *minimum* size hint wide enough to show its single longest
item in full, with no eliding. ViewManager's two combos
(`combo_view_mode`/`combo_quick_layer`) hold genuinely long descriptive
sentences ("Comparison View (Obs vs Model)", "Sea Ice Concentration &
Thickness"), so left at that default policy they - plus their labels -
floor the whole control bar's own minimumSizeHint() at (800, 30),
which in turn floors ESOCWindow's central widget, and so the whole
ESOC window, at that width regardless of the operator's real screen
size. See `view_manager.py`'s own `_shrink_combo_min_width` docstring
for the fix.
"""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication, QComboBox

from acf.gui.esoc.view_manager import ViewManager


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_view_mode_combo_does_not_adjust_to_its_longest_item(qapp):
    vm = ViewManager()
    assert vm.combo_view_mode.sizeAdjustPolicy() == QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon
    # Real content is untouched - every option is still there, in full.
    assert "Comparison View (Obs vs Model)" in vm.view_modes
    assert vm.combo_view_mode.count() == len(vm.view_modes)


def test_quick_layer_combo_does_not_adjust_to_its_longest_item(qapp):
    vm = ViewManager()
    assert vm.combo_quick_layer.sizeAdjustPolicy() == QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon
    assert "Sea Ice Concentration & Thickness" in vm.scientific_layers
    assert vm.combo_quick_layer.count() == len(vm.scientific_layers)


def test_view_manager_minimum_width_no_longer_floored_by_the_longest_combo_item(qapp):
    vm = ViewManager()
    vm.show()
    # Before this fix, ViewManager's own minimumSizeHint() measured
    # (800, 30) on this exact control bar - driven almost entirely by
    # the two combos' full-content minimum widths. A real, generous
    # regression margin (not a tight pixel-exact pin, which would be
    # fragile across Qt/font versions): still meaningfully narrower.
    assert vm.minimumSizeHint().width() < 750


def test_combo_dropdown_still_shows_every_item_untruncated(qapp):
    """The fix only affects the CLOSED box's minimum width - opening
    the dropdown must still offer every real option, unabridged."""
    vm = ViewManager()
    for i, expected in enumerate(vm.view_modes):
        assert vm.combo_view_mode.itemText(i) == expected
    for i, expected in enumerate(vm.scientific_layers):
        assert vm.combo_quick_layer.itemText(i) == expected
