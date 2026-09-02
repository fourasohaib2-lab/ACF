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


class PhysicsError(ACFError):
    """
    Base exception for acf.physics_guard's validation pipeline (docs/
    ROADMAP.md's "Prompt Maître ACF v2.0", section 50's error taxonomy).
    Never caught and silently discarded - a physics violation must
    surface to the caller, not vanish.
    """


class UnitError(PhysicsError):
    """A value's declared/actual unit is missing, unrecognized, or dimensionally incompatible with what was expected."""


class RangeError(PhysicsError):
    """A value falls outside acf.physics_guard.range_check's documented operational bounds for its variable."""


class CoordinateError(PhysicsError):
    """A latitude/longitude pair (or coordinate array) is out of its valid real-world range."""


class DimensionError(PhysicsError):
    """An array's shape doesn't match its declared dimensionality, or two coordinate arrays disagree with a field's shape."""


class VerticalError(PhysicsError):
    """A vertical profile violates a required real physical invariant (e.g. pressure must decrease with altitude)."""


class TimeError(PhysicsError):
    """A forecast's time metadata is inconsistent (e.g. valid_time before its own forecast_reference_time)."""


class ScientificConsistencyError(PhysicsError):
    """Two or more variables in the same state violate a real physical relationship between them (e.g. dew point above air temperature)."""
