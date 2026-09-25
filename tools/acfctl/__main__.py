"""``python -m tools.acfctl`` entry point - real, thin wrapper around
``cli.main()``."""

from __future__ import annotations

import sys

from tools.acfctl.cli import main

if __name__ == "__main__":
    sys.exit(main())
