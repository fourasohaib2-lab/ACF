# Atmospheric Complexity Framework (ACF)

## Project Mission
The Atmospheric Complexity Framework (ACF) is a scientific Python platform for numerical weather prediction, atmospheric analysis, visualization, data processing, and AI-assisted meteorological research.

## General Rules

- Always preserve the existing architecture.
- Never remove modules unless explicitly requested.
- Prefer extending existing components over creating duplicates.
- Produce production-quality Python code.
- Follow PEP 8.
- Keep type hints whenever possible.
- Keep functions small and readable.
- Avoid unnecessary dependencies.

## Scientific Rules

- Never invent atmospheric equations.
- Never approximate scientific constants without justification.
- Preserve physical consistency.
- Clearly document every scientific formula.

## Testing

- Update or create tests for every functional modification.
- Run pytest after code changes.
- Never ignore failing tests.

## Documentation

- Update documentation whenever behavior changes.
- Keep docstrings synchronized with implementation.

## Git

- Make small logical changes.
- Never rewrite history.
- Never delete branches.

## Security

- Never expose secrets.
- Never hardcode credentials.
- Validate external inputs.

## Performance

- Avoid unnecessary memory allocations.
- Prefer vectorized NumPy operations.
- Profile before optimizing.

## Before finishing any task

Always provide:

1. Summary
2. Files modified
3. Tests executed
4. Remaining issues
5. Recommendations
