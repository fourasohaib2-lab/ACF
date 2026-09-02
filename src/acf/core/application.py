"""
Atmospheric Complexity Framework (ACF)

Main Application Class

NOTE (found, NOT changed — RÈGLE D'OR / single source of truth): never
constructed anywhere (confirmed by grep across src/), and pyproject.toml
declares only one console entry point (acf-gui = acf.gui.app:main,
which launches ESOCWindow directly - it never touches this class).
Application.start()/Bootstrap.initialize() form a small, generic,
headless startup sequence (config load, service registration, plugin
discovery) - correct on inspection, just not currently anything's real
entry point. Not deleted per project convention.
"""

from acf.core.bootstrap import Bootstrap


class Application:
    """Main ACF application."""

    def __init__(self):

        self.name = "Atmospheric Complexity Framework"
        self.short_name = "ACF"
        self.version = "0.1.0"

        self.bootstrap = Bootstrap()

    def start(self):

        print("=" * 60)
        print(f"{self.name}")
        print(f"Version : {self.version}")
        print("=" * 60)

        self.bootstrap.initialize()

        print("\nACF started successfully.\n")
