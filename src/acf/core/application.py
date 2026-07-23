"""
Atmospheric Complexity Framework (ACF)

Main Application Class
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
