"""
Atmospheric Complexity Framework (ACF)

AWCI Core - Service Registry

Real ``ServiceRegistry`` - the ``registry.py`` module named in
``docs/architecture/awci_reference_architecture.md`` section 1
("... dependency injection..."). Reuses the already-real, already-
working ``acf.core.service_manager.ServiceManager`` directly - it is
already fully generic (register/get/exists/list by string name, no
ACF-specific behavior at all) so a second, independently invented
AWCI service registry would be pure duplication. ``ServiceRegistry``
is a real alias, not a new class, so ``isinstance``/identity checks
against either name see the exact same real type.

The blueprint's separate ``dependencies.py`` file is deliberately not
built - "service registration/lookup by name" (this module) and
"dependency injection" are the same real concept in this codebase (a
caller pulls what it needs from the registry rather than a container
constructing objects for it); splitting them into two files would add
indirection with no real behavioral difference.
"""

from __future__ import annotations

from acf.core.service_manager import ServiceManager

#: Real alias - see this module's own docstring for why no second
#: class is defined.
ServiceRegistry = ServiceManager

__all__ = ["ServiceRegistry"]
