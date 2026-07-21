"""
Atmospheric Complexity Framework (ACF)

Main entry point.
"""

from acf.core.application import Application


def main() -> None:
    app = Application()

    app.initialize()
    app.start()

    print(f"Status : {app.status()}")

    app.stop()


if __name__ == "__main__":
    main()
