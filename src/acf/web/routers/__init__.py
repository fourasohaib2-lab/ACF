"""
Domain-organized `/api/v1/*` routers - the Prompt Maître ACF v2.0's
section 21 gap (reports/ACF_MASTER_AUDIT_v2.md: "API: PARTIAL...
`acf.web.hpc_dashboard_server` expose `/api/hpc/*` et
`/api/fno/predict_demo` - pas l'organisation par domaine complète du
§21 (`/api/v1/datasets`, `/models`, `/complexity`, `/events`...)").

Each router below is a thin HTTP layer over an engine this project
already built in an earlier phase - no new computation is invented
here, only real endpoints exposing it:

- `models_router`  -> the Model Adapter Protocol (AROME/ALADIN/ARPEGE/
  ERA5/WRF/ICON/OpenIFS adapters).
- `complexity_router` -> the Complexity Engine (`AWCICalculator`,
  `acf.awci.spatial_field.compute_real_complexity_field()`).
- `events_router` -> the Event Engine (real detectors + `Event`'s own
  enforced lifecycle, held in a real, request-scoped in-memory store -
  see that router's own docstring on why in-memory, not a database).
- `datasets_router` -> the Data Contract (`Dataset.from_real_field()`,
  `Dataset.validate()` via `PhysicsGuard`).
- `hpc_router` -> `acf.hpc_connector.connection_manager.
  HPCConnectionManager` (status/connect/disconnect/WebSocket stream) -
  migrated here from its original unprefixed `/api/hpc/*` +
  `/ws/hpc/status` paths (see its own docstring).
- `fno_router` -> the trained FNO surface-temperature surrogate -
  migrated here from its original unprefixed `/api/fno/predict_demo`
  path (see its own docstring).

`hpc_router`/`fno_router` complete the migration reports/
ACF_MASTER_AUDIT_v2.md's earlier update for this section had
deliberately deferred ("a real, separate, larger refactor... kept out
of this pass") - now done: every real endpoint
`acf.web.hpc_dashboard_server.create_app()` serves lives under
`/api/v1/*`, except the dashboard's own HTML page at `/`.
"""

from acf.web.routers.complexity_router import router as complexity_router
from acf.web.routers.datasets_router import router as datasets_router
from acf.web.routers.events_router import router as events_router
from acf.web.routers.fno_router import router as fno_router
from acf.web.routers.hpc_router import router as hpc_router
from acf.web.routers.models_router import router as models_router

__all__ = ["complexity_router", "datasets_router", "events_router", "fno_router", "hpc_router", "models_router"]
