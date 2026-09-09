"""
Root pytest configuration.

Autouse, session-wide QSettings isolation: `acf.gui.map.layer_toggle_panel`'s
real "Settings / Layer Preferences" backend (`QSettings("ACF", "ESOC")`) is
the first real use of QSettings in this codebase (2026-09-05). Most
construction sites do NOT inject a test QSettings explicitly - `ESOCWindow`/
`PanelManager` construct `LayerTogglePanel`/`LayerPreferencesPanel` with no
`settings=` override, matching how every other panel is constructed - so
without this fixture, those would read this real machine's actual
~/.config/ACF/ESOC.conf, making test determinism depend on whatever a real
user has ever saved through the real running app (see
`tests/test_layer_preferences_panel.py`, which injects its own tmp_path
QSettings explicitly for the tests that exercise the feature directly; this
fixture instead covers every OTHER test that merely constructs an
ESOCWindow/PanelManager/LayerTogglePanel in passing).

Redirecting BOTH QSettings.Format.NativeFormat and IniFormat's UserScope
default path for the whole test session to a throwaway temp directory means
every `QSettings(org, app)` construction anywhere in the suite - present or
future - is automatically isolated, with no per-test-file changes required.
NOTE: overriding IniFormat alone is NOT enough on this platform - verified
empirically while building this fixture: the bare 2-arg `QSettings(org,
app)` convenience constructor reports `.format() == Format.NativeFormat`
(a distinct enum value from IniFormat even though it behaves identically on
Unix), and a `setPath` call for IniFormat only left `QSettings("ACF",
"ESOC").fileName()` still pointing at the real
`~/.config/ACF/ESOC.conf` - a real write landed there before this was
caught. Both formats must be redirected for the override to actually take
effect.
"""

import os
import tempfile

# Stable headless Qt platform for the WHOLE suite (2026-09-09):
# intermittent `Fatal Python error: Segmentation fault` crashes at varying
# positions in the AWCI GUI tests were traced to the default display
# platform path in this environment (the same suite passes cleanly
# back-to-back with offscreen; cf. pyproject.toml's own
# "QT_QPA_PLATFORM=offscreen for a headless run" note). Set at the root
# conftest - not tests/gui/conftest.py - so it is in effect before the
# FIRST QApplication is constructed anywhere (the platform binds at that
# moment, not per-test). setdefault so an explicitly chosen platform
# still wins.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtCore import QSettings


@pytest.fixture(autouse=True)
def _close_leaked_pyplot_figures():
    """Close all pyplot figures after every test (2026-09-09).

    The AWCI dashboard's real matplotlib-backed panels (awci_map_panel,
    awci_route_chart, the 3D view, …) each call `plt.figure(...)` when
    constructed, and pyplot retains every figure until explicitly
    closed. A long run therefore accumulates dozens of live native
    figures - pytest itself warns ("More than 20 figures have been
    opened … may consume too much memory") - which contributes to the
    intermittent native segfaults above. Every panel is function-scoped
    (built inside the test via qtbot), so no surviving widget ever needs
    a closed figure again. Test-infrastructure only.
    """
    yield
    try:
        import matplotlib.pyplot as plt

        plt.close("all")
    except Exception:  # pragma: no cover - matplotlib always present in this suite
        pass


@pytest.fixture(autouse=True, scope="session")
def _isolate_qsettings_from_the_real_users_desktop():
    with tempfile.TemporaryDirectory(prefix="acf-test-qsettings-") as tmp_dir:
        QSettings.setPath(QSettings.Format.NativeFormat, QSettings.Scope.UserScope, tmp_dir)
        QSettings.setPath(QSettings.Format.IniFormat, QSettings.Scope.UserScope, tmp_dir)
        yield
