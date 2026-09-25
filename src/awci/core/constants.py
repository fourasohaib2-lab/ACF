"""
Atmospheric Complexity Framework (ACF)

AWCI Core - Constants

Real, plain constants - the ``constants.py`` module named in
``docs/architecture/awci_reference_architecture.md`` section 1. Values
taken from this codebase's own already-real, already-shipped AWCI
identity (``acf.awci_app.run()``'s ``--version`` output string, the
only place this project currently prints a real "AWCI" application
name/description) and ``awci.workspace``'s own already-real
directories - not invented.
"""

from __future__ import annotations

#: Same real display name acf.awci_app.run() already prints for
#: `--version`/`--help` - the one place this codebase already names
#: the standalone AWCI application.
APP_NAME = "AWCI"
APP_FULL_NAME = "ACF AWCI (Atmospheric Weather Complexity Index)"

#: Real per-user config/state directory, matching the same real
#: convention awci.workspace.manager.AWCIWorkspaceManager already
#: established for its own recent-projects file (~/.awci/...) - kept
#: separate from ACF's own ~/.acf/ for the same disclosed reason.
USER_CONFIG_DIRECTORY = ".awci"

#: Real default relative directory names, matching
#: awci.workspace.project.AWCI_PROJECT_FOLDERS's own values plus the
#: process-relative directories a real AWCI application looks for
#: (config file, log file) - not re-declared as a separate list here,
#: only the two this package's own lifecycle/logging modules use.
CONFIG_DIRECTORY = "config"
LOG_DIRECTORY = "logs"
