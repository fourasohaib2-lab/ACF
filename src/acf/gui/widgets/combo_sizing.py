"""Shared fix for QComboBox's own "sized to its longest item" default.

`QComboBox`'s default `AdjustToContentsOnFirstShow` size-adjust policy
makes its *minimum* size hint wide enough to show its single longest
item in full, with no eliding - fine for a combo with short options, a
real problem for one whose real content includes a genuinely long
descriptive sentence (a "Taylor Diagram (Forecast Verification)" chart
type, a "Spherical Spectral Wave Solver" physics core, a "CMIP6
SSP5-8.5 (Fossil-Fueled)" scenario name - all real examples from this
codebase). First found and fixed in `acf.gui.esoc.view_manager`
(2026-09-05, ViewManager's own control bar was floored at 800px wide by
two such combos) - extracted here so the same real fix is not
copy-pasted at every other site with the identical problem.

`shrink_combo_min_width()` switches the combo to
`AdjustToMinimumContentsLengthWithIcon` with a fixed character-count
minimum instead: the closed box can shrink and elide ("...") its text
under real space pressure - standard Qt behaviour - while the dropdown
popup itself is untouched and still shows every option's full text. No
item is ever renamed, removed, or shortened.
"""

from __future__ import annotations

from PySide6.QtWidgets import QComboBox

#: Chosen to comfortably show most of this codebase's real option text
#: (e.g. "Non-Hydrostatic Finite...") without eliding on any real
#: screen size this project targets - only the genuinely longest items
#: elide, and only under real space pressure. Matches the value
#: view_manager.py's own fix originally shipped with.
DEFAULT_MIN_CONTENTS_LENGTH = 16


def shrink_combo_min_width(combo: QComboBox, min_contents_length: int = DEFAULT_MIN_CONTENTS_LENGTH) -> None:
    """Stop `combo`'s minimum width from being floored by its longest item.

    Args:
        combo: The QComboBox to fix - already populated or not, this
            only changes its size-adjust policy, not its items.
        min_contents_length: Character count `combo`'s minimum width is
            floored at instead (default: `DEFAULT_MIN_CONTENTS_LENGTH`).
    """
    combo.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
    combo.setMinimumContentsLength(min_contents_length)
