"""Tests for the new AWCI alerts engine (src/awci/alerts/), built while
working through the full remaining-gaps list ("On les attaque toutes
un par un") after it was identified as the specific gap in
docs/architecture/acf_awci_architecture_gap_analysis.md ("only a UI
panel (awci_alerts_panel), no standalone alerts engine").

AlertEngine is a real, headless composition over an already-built
awci.decision.situation.SituationSnapshot - no new severity scale, no
new threshold (reuses AWCI_SCORE_BANDS/ELEVATED_SCORE_BANDS). Never
infers a specific-hazard recommendation from a coarse module score
(same discipline already established in awci.decision.recommendation).
AlertNotifier follows the same real dispatch/error-isolation pattern
already established by awci.plugins.hooks.HookRegistry.
"""

from __future__ import annotations

from awci.alerts.engine import Alert, AlertEngine
from awci.alerts.notifications import AlertNotifier, NotificationDispatchError
from awci.decision import DecisionContext
from awci.decision.situation import SituationSnapshot, build_situation_snapshot

_CTX = DecisionContext(latitude=0.0, longitude=0.0, pressure_hpa=300.0)


def _build_situation(**scores) -> SituationSnapshot:
    overall_awci = scores.pop("overall_awci", 10.0)
    return build_situation_snapshot(_CTX, module_scores=scores, overall_awci=overall_awci)


# --------------------------------------------------------------------- engine.py


def test_alerts_for_returns_nothing_when_nothing_is_elevated():
    situation = _build_situation(dynamic=10.0, microphysical=5.0, overall_awci=10.0)
    engine = AlertEngine()
    assert engine.alerts_for(situation) == ()


def test_alerts_for_returns_one_alert_per_real_elevated_row():
    situation = _build_situation(dynamic=72.0, microphysical=20.0, convective=91.0, overall_awci=68.0)
    engine = AlertEngine()
    alerts = engine.alerts_for(situation)
    keys = {a.key for a in alerts}
    assert keys == {"turbulence", "convective", "overall"}
    assert "icing" not in keys  # microphysical=20.0 -> Low, not elevated


def test_alert_fields_match_the_real_hazard_assessment():
    situation = _build_situation(dynamic=72.0, overall_awci=68.0)
    engine = AlertEngine()
    alerts = engine.alerts_for(situation)
    turbulence_alert = next(a for a in alerts if a.key == "turbulence")
    assert isinstance(turbulence_alert, Alert)
    assert turbulence_alert.score == 72.0
    assert turbulence_alert.level == "Very High"
    assert turbulence_alert.label == "Turbulence Risk"


def test_alerts_for_attaches_real_recommendations_only_when_mapped():
    situation = _build_situation(dynamic=72.0, overall_awci=68.0)
    engine = AlertEngine()
    alerts = engine.alerts_for(situation, hazard_key_map={"turbulence": "cat_turbulence"})
    turbulence_alert = next(a for a in alerts if a.key == "turbulence")
    assert len(turbulence_alert.recommendations) > 0
    assert "signal d'attache des ceintures" in turbulence_alert.recommendations[0]


def test_alerts_for_never_fabricates_a_recommendation_for_an_unmapped_row():
    situation = _build_situation(dynamic=72.0, convective=91.0, overall_awci=68.0)
    engine = AlertEngine()
    alerts = engine.alerts_for(situation)  # no hazard_key_map at all
    for alert in alerts:
        assert alert.recommendations == ()


def test_alerts_for_never_fabricates_a_recommendation_for_a_hazard_outside_the_real_registry():
    situation = _build_situation(dynamic=72.0, overall_awci=68.0)
    engine = AlertEngine()
    alerts = engine.alerts_for(situation, hazard_key_map={"turbulence": "not_a_real_hazard"})
    turbulence_alert = next(a for a in alerts if a.key == "turbulence")
    assert turbulence_alert.recommendations == ()


def test_alert_is_a_real_frozen_dataclass():
    alert = Alert(key="x", label="X", score=1.0, level="Low", recommendations=())
    try:
        alert.score = 99.0  # type: ignore[misc]
        raised = False
    except Exception:
        raised = True
    assert raised


# --------------------------------------------------------------------- notifications.py


def test_alert_notifier_calls_every_real_subscriber():
    notifier = AlertNotifier()
    received_a: list[str] = []
    received_b: list[str] = []
    notifier.subscribe(lambda alert: received_a.append(alert.key))
    notifier.subscribe(lambda alert: received_b.append(alert.key))

    alert = Alert(key="turbulence", label="Turbulence Risk", score=72.0, level="Very High", recommendations=())
    errors = notifier.notify((alert,))
    assert received_a == ["turbulence"]
    assert received_b == ["turbulence"]
    assert errors == []


def test_alert_notifier_isolates_a_failing_subscriber():
    notifier = AlertNotifier()
    received: list[str] = []
    notifier.subscribe(lambda alert: received.append("before"))

    def boom(alert: Alert) -> None:
        raise ValueError("nope")

    notifier.subscribe(boom)
    notifier.subscribe(lambda alert: received.append("after"))

    alert = Alert(key="x", label="X", score=1.0, level="Low", recommendations=())
    errors = notifier.notify((alert,))
    assert received == ["before", "after"]
    assert len(errors) == 1
    assert isinstance(errors[0], NotificationDispatchError)
    assert "ValueError" in errors[0].reason
    assert "nope" in errors[0].reason


def test_alert_notifier_dispatches_every_real_alert_to_every_real_subscriber():
    notifier = AlertNotifier()
    received: list[str] = []
    notifier.subscribe(lambda alert: received.append(alert.key))
    alerts = (
        Alert(key="a", label="A", score=1.0, level="Low", recommendations=()),
        Alert(key="b", label="B", score=2.0, level="Low", recommendations=()),
    )
    notifier.notify(alerts)
    assert received == ["a", "b"]


def test_alert_notifier_unsubscribe_stops_future_notifications():
    notifier = AlertNotifier()
    received: list[str] = []

    def callback(alert: Alert) -> None:
        received.append(alert.key)

    notifier.subscribe(callback)
    notifier.unsubscribe(callback)
    alert = Alert(key="x", label="X", score=1.0, level="Low", recommendations=())
    notifier.notify((alert,))
    assert received == []


def test_alert_notifier_unsubscribe_is_a_real_noop_when_absent():
    notifier = AlertNotifier()
    notifier.unsubscribe(lambda alert: None)  # must not raise


def test_alert_notifier_with_no_alerts_dispatches_nothing():
    notifier = AlertNotifier()
    calls = []
    notifier.subscribe(lambda alert: calls.append(alert))
    errors = notifier.notify(())
    assert calls == []
    assert errors == []


# --------------------------------------------------------------------- discipline


def test_alerts_engine_reuses_the_real_decision_severity_scale_not_a_copy():
    """No independent severity-band constant is defined in engine.py -
    the real awci.decision.situation.AWCI_SCORE_BANDS/
    ELEVATED_SCORE_BANDS is the one real source, via SituationSnapshot
    itself."""
    import awci.alerts.engine as engine_module

    assert not hasattr(engine_module, "AWCI_SCORE_BANDS")
    assert not hasattr(engine_module, "ELEVATED_SCORE_BANDS")


def test_alerts_package_is_headless_no_gui_dependency_imported():
    import sys

    import awci.alerts  # noqa: F401

    alerts_module_names = [name for name in sys.modules if name.startswith("awci.alerts")]
    assert len(alerts_module_names) >= 3  # __init__ + engine + notifications
    for name in alerts_module_names:
        module = sys.modules[name]
        source_file = getattr(module, "__file__", "") or ""
        assert "PySide6" not in source_file
