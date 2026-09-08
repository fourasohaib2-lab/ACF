"""Unit tests for ACF GUI Application Bootstrap & Environment Configurator."""

import os
import sys
from pathlib import Path

from acf.gui.bootstrap import _detect_project_root, configure_runtime


def test_detect_project_root():
    root = _detect_project_root()
    assert isinstance(root, Path)
    assert root.exists()
    assert (root / "src").exists()


def test_configure_runtime_without_display(monkeypatch):
    monkeypatch.delenv("DISPLAY", raising=False)
    monkeypatch.delenv("WAYLAND_DISPLAY", raising=False)
    monkeypatch.delenv("QT_QPA_PLATFORM", raising=False)

    root = configure_runtime()
    assert root.exists()
    assert os.environ.get("QT_QPA_PLATFORM") == "vnc:size=1280x720:port=5910"
    assert str(root / "src") in sys.path


def test_configure_runtime_with_display(monkeypatch):
    monkeypatch.setenv("DISPLAY", ":0")
    monkeypatch.delenv("QT_QPA_PLATFORM", raising=False)

    configure_runtime()
    # Explicit DISPLAY present, QT_QPA_PLATFORM should not be forced to VNC
    assert os.environ.get("QT_QPA_PLATFORM") != "vnc:size=1280x720:port=5910"


def test_configure_runtime_explicit_qpa(monkeypatch):
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")

    configure_runtime()
    assert os.environ.get("QT_QPA_PLATFORM") == "offscreen"
