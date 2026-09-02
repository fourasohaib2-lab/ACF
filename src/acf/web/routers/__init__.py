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

Deliberately NOT done here (see reports/ACF_MASTER_AUDIT_v2.md's own
update for this phase): migrating the pre-existing `/api/hpc/*` and
`/api/fno/predict_demo` endpoints (acf.web.hpc_dashboard_server) under
this same `/api/v1` prefix - a real, separate, larger refactor
(updating their own tests and the dashboard's own JS fetch() calls)
kept out of this pass per the project's own "travailler par lots
contrôlés" convention, not an oversight.
"""

from acf.web.routers.complexity_router import router as complexity_router
from acf.web.routers.datasets_router import router as datasets_router
from acf.web.routers.events_router import router as events_router
from acf.web.routers.models_router import router as models_router

__all__ = ["complexity_router", "datasets_router", "events_router", "models_router"]
