"""
Tests for AWCIDashboard's "🔔 Alerts" button wiring - real elevated-
risk state and real cross-dialog sharing of live METAR data with the
"📨 Message" button.
"""

from unittest.mock import patch

import pytest
from PySide6.QtWidgets import QApplication

from acf.aviation.icao.live_source import LiveStationBundle
from acf.aviation.icao.metar_decoder import METARDecoder
from acf.awci.vertical_field import compute_real_complexity_volume
from acf.gui.dashboard.awci_dashboard import AWCIDashboard


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _real_volume(**overrides):
    kwargs = dict(model="ALADIN", n_lat=8, n_lon=12, n_levels=6, steps=2, perturbation_scale=2.0, seed=1)
    kwargs.update(overrides)
    return compute_real_complexity_volume(**kwargs)


def _fake_bundle(icao: str) -> LiveStationBundle:
    bundle = LiveStationBundle(icao_code=icao)
    raw = f"METAR {icao} 030000Z 12025G45KT 9999 TSRA SCT020 20/18 Q1013"
    bundle.metar.raw_text = raw
    bundle.metar.decoded = METARDecoder.decode(raw)
    return bundle


def test_alerts_button_badge_matches_the_real_computed_count(qapp):
    """The demo synthetic pattern may genuinely have an elevated risk
    at its default point of interest - the badge must match whatever
    that real computation actually produces, not assume zero."""
    dashboard = AWCIDashboard()
    module_scores, overall_awci, physical_score, forecast_score = dashboard._last_risk_inputs
    from acf.gui.dashboard.awci_alerts_panel import count_active_alerts

    expected = count_active_alerts(module_scores, overall_awci, physical_score, forecast_score, None)
    if expected:
        assert dashboard.alerts_button.text() == f"🔔 Alerts ({expected})"
    else:
        assert dashboard.alerts_button.text() == "🔔 Alerts"


def test_alerts_button_reflects_real_elevated_risk_after_real_physics(qapp):
    dashboard = AWCIDashboard()
    volume = _real_volume()
    dashboard._on_real_physics_ready(volume)
    # _last_risk_inputs was set for real by the same call - the badge
    # must reflect whatever that real computation actually produced,
    # not a fixed/fabricated number.
    module_scores, overall_awci, _phys, _fcst = dashboard._last_risk_inputs
    from acf.gui.dashboard.awci_alerts_panel import count_active_alerts

    expected = count_active_alerts(module_scores, overall_awci, _phys, _fcst, None)
    if expected:
        assert f"({expected})" in dashboard.alerts_button.text()
    else:
        assert dashboard.alerts_button.text() == "🔔 Alerts"


def test_open_alerts_creates_and_reuses_the_same_dialog(qapp):
    dashboard = AWCIDashboard()
    dashboard._open_alerts()
    first = dashboard._alerts_window
    assert first is not None
    dashboard._open_alerts()
    assert dashboard._alerts_window is first


def test_alerts_dialog_sees_live_data_after_a_message_fetch(qapp):
    """Real cross-dialog sharing: once 📨 Message has fetched real
    data, 🔔 Alerts' "Live station conditions" section must reflect it
    - not stay stuck at "no live data fetched yet"."""
    with patch(
        "acf.gui.dashboard.awci_messages_panel.fetch_and_decode_station",
        side_effect=lambda icao, timeout=8.0: _fake_bundle(icao),
    ), patch("acf.gui.dashboard.awci_messages_panel.fetch_active_sigmets", return_value=[]):
        dashboard = AWCIDashboard()
        dashboard._open_messages()

        import time

        deadline = time.time() + 15
        while dashboard._messages_window.last_bundles is None and time.time() < deadline:
            QApplication.processEvents()
            time.sleep(0.02)

        assert dashboard._messages_window.last_bundles is not None

        dashboard._open_alerts()

        live_text = dashboard._alerts_window.live_rows_container.itemAt(0).widget().text()
        assert "Thunderstorm" in live_text or "Strong wind gusts" in live_text
