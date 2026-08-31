"""
Project exceptions.
"""


class ACFError(Exception):
    """Base exception."""


class ConfigurationError(ACFError):
    """Configuration exception."""


class PluginError(ACFError):
    """Plugin exception."""


class WorkspaceError(ACFError):
    """Workspace exception."""
