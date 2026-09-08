# ACF RELEASE GOVERNANCE (ACF-G001)

## 1. SEMANTIC VERSIONING & STAGING LIFECYCLE

- **Version Format**: `vMAJOR.MINOR.PATCH` (e.g., `v0.7.0`, `v1.0.0`).
- **Release Stages**: Alpha → Beta → Release Candidate (RC) → Stable → Production (TRL 9).
- **Rollback Strategy**: Git release tags and automated rollbacks of Slurm batch submit scripts.
