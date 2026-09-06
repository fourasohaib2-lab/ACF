"""
acf.workspace - project workspace management (manager.py, project.py,
recent.py, serializer.py - real, tested, already carrying real fix
disclosures: a silent except-pass swallowing a corrupted recent-
projects file, and a save/reopen round-trip that silently discarded
resources/metadata/settings/creation date, both fixed by earlier
passes). exceptions.py/metadata.py/templates.py are empty stubs - see
their own docstrings.

No __all__ re-export here - import from the specific submodule
directly (e.g. `from acf.workspace.manager import WorkspaceManager`).
"""
