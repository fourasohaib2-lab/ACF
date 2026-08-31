"""
Atmospheric Complexity Framework (ACF)

Visualization Layer Stack Test Suite
(Layer, LayerCollection, LayerGroup, LayerManager)

These 4 modules previously had 0% coverage - no test file imported
any of them. All confirmed genuinely correct real state-management
code (no fabrication) while writing these tests.
"""

import pytest
from PySide6.QtWidgets import QApplication

from acf.visualization.layer import Layer
from acf.visualization.layer_collection import LayerCollection
from acf.visualization.layer_group import LayerGroup
from acf.visualization.layer_manager import LayerManager


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_layer_defaults_and_visibility_toggle():
    layer = Layer(name="Temperature", variable="t2m")
    assert layer.visible is True
    assert layer.opacity == 1.0
    assert layer.colormap == "viridis"

    layer.hide()
    assert layer.visible is False
    layer.show()
    assert layer.visible is True
    layer.toggle()
    assert layer.visible is False


def test_layer_set_opacity_is_clamped():
    layer = Layer(name="Wind")
    layer.set_opacity(1.5)
    assert layer.opacity == 1.0
    layer.set_opacity(-0.5)
    assert layer.opacity == 0.0
    layer.set_opacity(0.4)
    assert layer.opacity == 0.4


def test_layer_summary_and_repr():
    layer = Layer(name="Precip", variable="tp")
    summary = layer.summary()
    assert summary["name"] == "Precip"
    assert summary["variable"] == "tp"
    assert "Precip" in repr(layer)


def test_layer_collection_add_get_remove():
    coll = LayerCollection()
    l1 = coll.add(Layer(name="A"))
    l2 = coll.add(Layer(name="B"))
    assert len(coll) == 2
    assert coll.get(l1.id) is l1
    assert coll.by_name("B") is l2

    coll.remove(l1.id)
    assert len(coll) == 1
    assert coll.get(l1.id) is None


def test_layer_collection_visible_hidden_and_summary():
    coll = LayerCollection()
    visible_layer = coll.add(Layer(name="Visible", visible=True))
    hidden_layer = coll.add(Layer(name="Hidden", visible=False))

    assert coll.visible() == [visible_layer]
    assert coll.hidden() == [hidden_layer]
    assert coll.names() == ["Visible", "Hidden"]

    summary = coll.summary()
    assert summary["count"] == 2
    assert summary["visible"] == 1
    assert summary["hidden"] == 1


def test_layer_collection_iteration_and_indexing():
    coll = LayerCollection()
    layer = coll.add(Layer(name="Only"))
    assert list(coll) == [layer]
    assert coll[0] is layer

    coll.clear()
    assert len(coll) == 0


def test_layer_group_hierarchy_show_hide():
    parent = LayerGroup("Parent")
    child = parent.add_group(LayerGroup("Child"))
    layer = parent.add_layer(Layer(name="L1"))
    child_layer = child.add_layer(Layer(name="L2"))

    parent.hide()
    assert parent.visible is False
    assert layer.visible is False
    assert child.visible is False
    assert child_layer.visible is False

    parent.show()
    assert parent.visible is True
    assert child_layer.visible is True


def test_layer_group_get_and_remove_group():
    parent = LayerGroup("Root")
    parent.add_group(LayerGroup("Sub"))
    assert parent.get_group("Sub") is not None
    parent.remove_group("Sub")
    assert parent.get_group("Sub") is None


def test_layer_group_summary_and_len():
    group = LayerGroup("G")
    group.add_layer(Layer(name="X"))
    assert len(group) == 1
    summary = group.summary()
    assert summary["name"] == "G"
    assert summary["layers"]["count"] == 1


def test_layer_manager_add_and_current_layer(qapp):
    manager = LayerManager()
    l1 = manager.create_layer("First", "t2m")
    assert manager.current_layer() is l1
    assert manager.current_layer_id() == l1.id

    l2 = manager.create_layer("Second", "tp")
    # current layer stays the first one added (only set when None)
    assert manager.current_layer() is l1
    assert manager.count() == 2
    assert l2 in manager.layers()


def test_layer_manager_remove_reassigns_current(qapp):
    manager = LayerManager()
    l1 = manager.create_layer("First", "t2m")
    l2 = manager.create_layer("Second", "tp")

    manager.remove_layer(l1.id)
    assert manager.current_layer() is l2
    assert manager.count() == 1

    manager.remove_layer(l2.id)
    assert manager.current_layer() is None
    assert manager.count() == 0


def test_layer_manager_show_hide_and_visible_layers(qapp):
    manager = LayerManager()
    l1 = manager.create_layer("Vis", "t2m")
    l2 = manager.create_layer("Hid", "tp")
    manager.hide_layer(l2.id)

    assert manager.visible_layers() == [l1]
    manager.show_layer(l2.id)
    assert l2 in manager.visible_layers()


def test_layer_manager_move_layer(qapp):
    manager = LayerManager()
    l1 = manager.create_layer("A", "v1")
    l2 = manager.create_layer("B", "v2")
    manager.move_layer(0, 1)
    assert manager.layers() == [l2, l1]

    # Out-of-range indices are ignored, not raised
    manager.move_layer(-1, 5)
    assert manager.layers() == [l2, l1]


def test_layer_manager_set_current_and_status(qapp):
    manager = LayerManager()
    manager.create_layer("A", "v1")
    l2 = manager.create_layer("B", "v2")
    manager.set_current_layer(l2.id)
    assert manager.current_layer() is l2

    status = manager.status()
    assert status["layers"] == 2
    assert status["current_layer"] == "B"
    assert status["names"] == ["A", "B"]


def test_layer_manager_get_by_name_and_clear(qapp):
    manager = LayerManager()
    manager.create_layer("Findme", "v1")
    assert manager.get_layer_by_name("Findme") is not None
    assert manager.get_layer_by_name("Nope") is None

    manager.clear()
    assert manager.count() == 0
    assert manager.current_layer() is None
