"""Tab/stack containers that size to their *current* page only.

Real bug found while auditing the dashboard's responsive resizing
(2026-09-05): `QStackedWidget` and `QTabWidget` both default to Qt's
"StackAll" sizing policy, where `sizeHint()`/`minimumSizeHint()` return
the LARGEST size hint among *every* page they hold, not just the one
actually showing - so a container never shrinks below its single
biggest page, even while a tiny page is selected.

Two concrete, verified instances of this in the codebase:

- `ESOCLayout.bottom_tabs` (44 "Operational Command Panels" tabs):
  measured `minimumSizeHint()` of (941, 650) - driven entirely by the
  "Products" and "Output" tabs - propagates straight up to
  `ESOCWindow`'s own enforced minimum size (Qt floors a QMainWindow's
  minimum size to the sum of its dock widgets' minimums), so the whole
  ESOC window could never shrink below ~941px of dock width no matter
  which of the other 43, much smaller, tabs the operator actually had
  open. Combined with the left/right docks this floors the real window
  around 1314x1053 - larger than plenty of real screens (a 1280x800 or
  1024x768 laptop panel, a modest VNC session) `gui_screen_utils.
  fit_window_to_screen` is supposed to guarantee the window still fits.

- `ACFWorkstation.stack` (15 Lab panels): measured `minimumSizeHint()`
  of (646, 737), matching the widest ("Atmospheric Interaction Engine",
  646) and tallest ("Complexity Explorer", 737) panels respectively -
  again enforced even while the small "Atmosphere State" panel (180x147)
  is the one actually showing.

`CurrentPageStackedWidget`/`CurrentPageTabWidget` are drop-in
replacements (`QStackedWidget`/`QTabWidget` subclasses, same public
API) that instead report only the *currently selected* page's own size
hints, plus - for the tab variant - the real on-screen cost of the tab
bar and frame. `currentChanged` triggers `updateGeometry()` so a parent
layout (a `QMainWindow`'s dock-widget layout included) re-queries the
new, real minimum immediately on every tab/page switch, letting the
window actually shrink to whatever the operator's screen allows while a
small page is active - it only grows back once a genuinely large page
is selected, exactly matching what that page needs.
"""

from __future__ import annotations

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QStackedWidget, QStyle, QTabWidget, QWidget


def _effective_min_size(widget: QWidget) -> QSize:
    """The minimum size `widget` will actually enforce inside a layout.

    A widget's own `minimumSizeHint()` reflects its layout's content, but
    a widget that also calls the explicit `setMinimumSize()` (several
    panels in this codebase do, e.g. `ACFVerticalSoundingWidget` at 260px
    wide) is floored by that instead whenever it is larger - the same
    `expandedTo()` combination Qt's own layout engine uses internally
    (`qSmartMinSize`), reimplemented here because that helper isn't
    exposed to PySide6. An invalid hint (`QSize(-1, -1)`, e.g. a bare
    `QWidget` with no layout) simply drops out of the `expandedTo` max.
    """
    return widget.minimumSizeHint().expandedTo(widget.minimumSize())


class CurrentPageStackedWidget(QStackedWidget):
    """`QStackedWidget` sized to its current page only (see module docstring)."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.currentChanged.connect(lambda _index: self.updateGeometry())

    def sizeHint(self) -> QSize:  # noqa: N802 - Qt override signature
        current = self.currentWidget()
        return current.sizeHint() if current is not None else super().sizeHint()

    def minimumSizeHint(self) -> QSize:  # noqa: N802 - Qt override signature
        current = self.currentWidget()
        return _effective_min_size(current) if current is not None else super().minimumSizeHint()


class CurrentPageTabWidget(QTabWidget):
    """`QTabWidget` sized to its current tab only (see module docstring).

    Accounts for the tab bar and frame - real, visible chrome around
    whichever page is showing - so the reported size never claims less
    space than the tab bar itself actually needs.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.currentChanged.connect(lambda _index: self.updateGeometry())

    def _chrome_size(self) -> QSize:
        # NOTE: the tab bar's own *minimum* size hint, not its (preferred)
        # sizeHint() - with many tabs (ESOC's bottom dock holds 44), the
        # tab bar's sizeHint() is the width needed to show every label at
        # once with no scrolling, which would silently defeat QTabWidget's
        # own default `usesScrollButtons` behaviour (scroll arrows appear
        # instead of shrinking below that) and re-introduce a huge floor
        # from a different source than the one this class exists to fix.
        bar_hint = self.tabBar().minimumSizeHint()
        frame_width = self.style().pixelMetric(QStyle.PixelMetric.PM_DefaultFrameWidth, None, self)
        return QSize(2 * frame_width, bar_hint.height() + 2 * frame_width)

    def _with_chrome(self, page_size: QSize) -> QSize:
        chrome = self._chrome_size()
        min_width = max(page_size.width() + chrome.width(), self.tabBar().minimumSizeHint().width())
        return QSize(min_width, page_size.height() + chrome.height())

    def sizeHint(self) -> QSize:  # noqa: N802 - Qt override signature
        current = self.currentWidget()
        return self._with_chrome(current.sizeHint()) if current is not None else super().sizeHint()

    def minimumSizeHint(self) -> QSize:  # noqa: N802 - Qt override signature
        current = self.currentWidget()
        return self._with_chrome(_effective_min_size(current)) if current is not None else super().minimumSizeHint()
