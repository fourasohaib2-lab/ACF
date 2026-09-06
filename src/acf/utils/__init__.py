"""
Small stdlib-only helper package for ACF: `paths` (project directory
layout), `system` (OS/Python version + project root), `files`
(mkdir/exists), `validators` (file/dir existence checks), `time`
(now()/timestamp() wrappers around `datetime`).

Disclosure (verified by grepping every import across src/ and tests/ on
2026-09-06): none of these five helpers is currently imported by any other
`acf` module - each one is exercised only by its own test file
(tests/test_utils.py, tests/test_utils_helpers.py). Not dead in the sense
of broken or untested, just not yet wired into the rest of the codebase.
Safe to reuse instead of re-implementing the same os.path/pathlib
boilerplate elsewhere.
"""
