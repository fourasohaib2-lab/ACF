"""
Atmospheric Complexity Framework (ACF)

AWCI Core - Exceptions

Real ``AWCIError`` hierarchy - the ``exceptions.py`` module named in
``docs/architecture/awci_reference_architecture.md`` section 1 ("AWCI
Core"). Deliberately NOT a subclass of ``acf.core.exceptions.ACFError``
- the reference architecture explicitly frames AWCI as "a separate
aviation product/project, built above the ACF scientific core... not
as a subpackage buried inside ACF's own layer 3" (see that document's
own header), so entangling AWCI's own error hierarchy with ACF's would
contradict that framing. The two hierarchies are real siblings, not
parent/child.
"""

from __future__ import annotations


class AWCIError(Exception):
    """Base exception for every real error raised by ``awci.core`` and
    the application-lifecycle layer it coordinates."""


class AWCIConfigurationError(AWCIError):
    """A real AWCI configuration file is missing a required key,
    malformed, or fails the real validation
    ``awci.complexity.config_loader.load_config()`` already performs
    (reused, not reimplemented, by ``awci.core.configuration``)."""


class AWCIServiceError(AWCIError):
    """A real service was requested from ``ServiceRegistry`` that was
    never registered, or a service registration itself was invalid."""


class AWCILifecycleError(AWCIError):
    """A real application-lifecycle operation (start/stop) was
    performed out of order, e.g. stopping an ``AWCIApplication`` that
    was never started."""
