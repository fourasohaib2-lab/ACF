"""
acf.core - application plumbing, not physics.

Real, stdlib(+PyYAML/loguru)-only infrastructure: `config` (YAML config
loading), `logger` (loguru wrapper), `plugin_manager`/`service_manager`
(a small registry pair), `constants`/`environment`/`exceptions`/`version`/
`metadata` (plain constants and error types), `application`/`bootstrap`
(a headless startup sequence - see application.py's own docstring: never
actually constructed anywhere, `acf-gui` launches `ACFWorkstationWindow`
directly instead), `parameter`/`parameter_registry` (compatibility re-exports of
`acf.parameters`), `contracts` (the real Dataset/VariableContract/
Provenance data contract - see contracts/__init__.py's own docstring for
what it does and does not yet cover), and, added 2026-09-21 to close
the blueprint's own remaining `core/` gaps: `events` (`EventBus`/
`Event` - generic app-lifecycle pub/sub), `registry` (`Registry` - a
real alias for `service_manager.ServiceManager`), `lifecycle`
(`Lifecycle` - a real alias for `bootstrap.Bootstrap`), `context`
(`ApplicationContext` - bundles `Registry`+`EventBus`).

No NumPy dependency here and no claim of "integrating with a scientific
engine" - the actual physics lives in acf.science/acf.model4d/
acf.earth_physics, which this package does not touch.
"""
