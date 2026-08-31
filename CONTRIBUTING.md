# Contributing to ACF

Thank you for your interest in contributing to the Atmospheric Complexity Framework (ACF).

## Code of Conduct
Please review and adhere to the [Code of Conduct](CODE_OF_CONDUCT.md) in all project interactions.

## Development Workflow
1. Fork and clone the repository.
2. Create a dedicated feature or bugfix branch: `git checkout -b feature/my-feature`.
3. Set up the development environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -e .
   pip install -r requirements-dev.txt
   ```
4. Implement your changes following scientific rigor and typing standards.
5. Write corresponding unit and integration tests under `tests/`.
6. Verify quality gates:
   ```bash
   pytest
   ruff check .
   mypy src
   ```
7. Submit a clean Pull Request targeting the `develop` branch.
