# ACF GIT GOVERNANCE (ACF-G001)

## 1. BRANCH STRATEGY & WORKFLOW

- **Protected Branches**: `master` (production releases), `develop` (integration).
- **Feature Branch Naming**: `feature/ACF-XXX-description`, `fix/ACF-XXX-description`, `docs/ACF-XXX-description`.
- **Commit Message Format**: Standardized Conventional Commits (`feat(hpc): add slurm monitor`, `fix(data): fix fa reader header`).
- **PR Merge Requirement**: All unit & integration tests passing (`pytest tests/`), zero compilation warnings.
