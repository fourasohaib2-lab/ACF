#!/usr/bin/env bash
set -Eeuo pipefail

# ============================================================
# ACF FULL REPAIR AUTOPILOT
# ============================================================
#
# Objectif :
#   Scanner et réparer progressivement l'ensemble du projet ACF
#   avec AGY, en validant chaque cycle.
#
# Philosophie :
#   SCAN -> FIX -> TEST -> FIX -> TEST -> ... -> VALIDATE
#
# IMPORTANT :
#   Le script ne déclare JAMAIS ACF "réparé" uniquement parce
#   qu'AGY a terminé. La validation locale décide.
# ============================================================

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="$PROJECT_ROOT/logs/agy_acf_repair"
STATE_DIR="$LOG_DIR/state"

mkdir -p "$LOG_DIR" "$STATE_DIR"

TIMESTAMP="$(date '+%Y%m%d_%H%M%S')"
LOG="$LOG_DIR/repair_${TIMESTAMP}.log"

MAX_CYCLES="${MAX_CYCLES:-100}"
AGY_TIMEOUT="${AGY_TIMEOUT:-7200}"

if [ -d "$PROJECT_ROOT/.venv" ]; then
    export PATH="$PROJECT_ROOT/.venv/bin:$PATH"
    PYTHON_BIN="${PYTHON_BIN:-$PROJECT_ROOT/.venv/bin/python}"
elif command -v python >/dev/null 2>&1; then
    PYTHON_BIN="${PYTHON_BIN:-python}"
elif command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="${PYTHON_BIN:-python3}"
else
    echo "ERROR: Aucun Python trouvé dans PATH"
    exit 1
fi

export PYTHONPATH="$PROJECT_ROOT/src${PYTHONPATH:+:$PYTHONPATH}"

exec > >(tee -a "$LOG") 2>&1

cd "$PROJECT_ROOT"

echo
echo "============================================================"
echo " ACF FULL REPAIR AUTOPILOT"
echo "============================================================"
echo "PROJECT : $PROJECT_ROOT"
echo "START   : $(date)"
echo "LOG     : $LOG"
echo "MAX     : $MAX_CYCLES cycles"
echo "============================================================"
echo

# ------------------------------------------------------------
# 0. Vérifications
# ------------------------------------------------------------

command -v git >/dev/null || {
    echo "ERROR: git introuvable"
    exit 1
}

command -v agy >/dev/null || {
    echo "ERROR: agy introuvable dans PATH"
    exit 1
}

command -v "$PYTHON_BIN" >/dev/null || {
    echo "ERROR: Python introuvable"
    exit 1
}

echo "[INFO] AGY:"
agy --version || true

echo "[INFO] Python:"
"$PYTHON_BIN" --version

echo "[INFO] Git:"
git status --short

# ------------------------------------------------------------
# 1. Snapshot de sécurité
# ------------------------------------------------------------

SNAPSHOT="$STATE_DIR/baseline_${TIMESTAMP}.patch"

echo
echo "[1/10] Création du snapshot Git..."

git diff --binary > "$SNAPSHOT" || true

echo "[OK] Snapshot: $SNAPSHOT"

git rev-parse HEAD > "$STATE_DIR/baseline_commit_${TIMESTAMP}.txt"

# ------------------------------------------------------------
# 2. Inventaire complet
# ------------------------------------------------------------

echo
echo "[2/10] Scan du dépôt..."

find . \
    -type f \
    -not -path './.git/*' \
    -not -path './.venv/*' \
    -not -path './venv/*' \
    -not -path './node_modules/*' \
    -not -path './__pycache__/*' \
    | sort > "$STATE_DIR/all_files_${TIMESTAMP}.txt"

TOTAL_FILES="$(wc -l < "$STATE_DIR/all_files_${TIMESTAMP}.txt")"

PY_FILES="$(find . -type f -name '*.py' \
    -not -path './.git/*' \
    -not -path './.venv/*' \
    -not -path './venv/*' \
    | wc -l)"

SH_FILES="$(find . -type f \( -name '*.sh' -o -name '*.bash' \) \
    -not -path './.git/*' \
    | wc -l)"

TEST_FILES="$(find tests -type f 2>/dev/null | wc -l || true)"

echo "[INFO] Total files : $TOTAL_FILES"
echo "[INFO] Python      : $PY_FILES"
echo "[INFO] Shell       : $SH_FILES"
echo "[INFO] Tests       : $TEST_FILES"

# ------------------------------------------------------------
# Fonctions de validation
# ------------------------------------------------------------

run_ruff() {
    echo
    echo "---------------- RUFF ----------------"

    if command -v ruff >/dev/null 2>&1; then
        ruff check . --output-format=concise
    else
        echo "[WARN] ruff non disponible"
        return 0
    fi
}

run_compile() {
    echo
    echo "---------------- PYCOMPILE ----------------"

    "$PYTHON_BIN" -m compileall -q src tests
}

run_import_smoke() {
    echo
    echo "---------------- IMPORT SMOKE ----------------"

    "$PYTHON_BIN" - <<'PY'
import sys

print("Python:", sys.version)

try:
    import acf
    print("OK: import acf")
except Exception as exc:
    print("ERROR: import acf:", repr(exc))
    raise

modules = [
    "acf.core",
    "acf.data",
    "acf.models",
    "acf.ai",
    "acf.maps",
    "acf.gui",
    "acf.hpc_workflow",
    "acf.science",
    "acf.verification",
    "acf.space_weather",
]

for name in modules:
    try:
        __import__(name)
        print("OK:", name)
    except ModuleNotFoundError:
        print("WARN: module not present:", name)
    except Exception as exc:
        print("ERROR:", name, repr(exc))
        raise
PY
}

run_pytest() {
    echo
    echo "---------------- PYTEST ----------------"

    if [ ! -d tests ]; then
        echo "[WARN] tests/ absent"
        return 0
    fi

    "$PYTHON_BIN" -m pytest -q
}

# ------------------------------------------------------------
# 3. Baseline validation
# ------------------------------------------------------------

echo
echo "[3/10] Validation initiale..."

BASELINE_STATUS=0

run_compile || BASELINE_STATUS=1
run_ruff || BASELINE_STATUS=1
run_import_smoke || BASELINE_STATUS=1
run_pytest || BASELINE_STATUS=1

echo "$BASELINE_STATUS" > "$STATE_DIR/baseline_status"

# ------------------------------------------------------------
# 4. Prompt AGY
# ------------------------------------------------------------

PROMPT_FILE="$STATE_DIR/agy_master_prompt.txt"

cat > "$PROMPT_FILE" <<'PROMPT'
You are the principal software-repair engineer for the ACF
(Atmospheric Complexity Framework) repository.

Your mission is to repair the repository comprehensively.

IMPORTANT:
- Do NOT assume that the repository is correct.
- Do NOT limit yourself to one directory.
- Inspect the complete repository.
- Respect the existing architecture.
- Do NOT delete working functionality merely to make tests pass.
- Do NOT replace scientific implementations with fake placeholders.
- Do NOT weaken tests.
- Do NOT skip failing tests.
- Do NOT silence errors with broad exception handlers.
- Do NOT randomly rewrite large parts of the architecture.
- Preserve scientific correctness.
- Preserve public APIs unless a broken API must be repaired.
- Preserve backward compatibility where practical.
- Fix root causes rather than symptoms.

FIRST:
1. Inspect the complete repository.
2. Inspect git status and recent changes.
3. Build an inventory of Python modules, packages, tests, scripts,
   configuration files and documentation.
4. Run the available test and static-analysis tools.
5. Identify missing modules, broken imports, syntax errors,
   circular imports, undefined names, incorrect APIs,
   bad paths, configuration errors, typing errors,
   runtime errors and test failures.

THEN:
Repair the repository in controlled batches.

For every batch:
1. Diagnose.
2. Modify the minimum necessary files.
3. Run targeted tests.
4. Run static checks.
5. Fix regressions.
6. Continue only after validating the batch.

Never claim that something is fixed without testing it.

Priority order:

P0:
- syntax errors
- import failures
- missing modules
- fatal runtime errors

P1:
- broken core architecture
- broken APIs
- failing tests
- dependency problems

P2:
- Ruff/static-analysis errors
- typing problems
- resource/path/configuration problems

P3:
- robustness
- maintainability
- documentation
- code quality

The final objective is:

- zero Python syntax errors
- zero import failures
- zero Ruff errors
- zero failing tests
- zero obvious broken references
- no corrupted package structure
- no fake implementations introduced just to satisfy tests

Do not stop merely because one test suite passes.

The repository must be re-scanned after repairs.

When a problem cannot be safely solved, document the exact blocker
instead of inventing a fake solution.

At the end of each cycle report:
- files inspected
- files modified
- errors found
- errors fixed
- remaining errors
- tests executed
- test results
- Ruff result
- import result
- unresolved blockers
PROMPT

# ------------------------------------------------------------
# 5. AGY cycle
# ------------------------------------------------------------

run_agy() {
    local cycle="$1"

    echo
    echo "============================================================"
    echo " AGY REPAIR CYCLE $cycle"
    echo "============================================================"

    local cycle_log="$LOG_DIR/agy_cycle_${cycle}.log"

    timeout "$AGY_TIMEOUT" \
        agy \
        --dangerously-skip-permissions \
        -p "$(cat "$PROMPT_FILE")" \
        2>&1 | tee "$cycle_log"

    return "${PIPESTATUS[0]}"
}

# ------------------------------------------------------------
# 6. Validation après AGY
# ------------------------------------------------------------

validate_cycle() {
    local cycle="$1"
    local result=0

    echo
    echo "============================================================"
    echo " VALIDATION CYCLE $cycle"
    echo "============================================================"

    run_compile || result=1
    run_ruff || result=1
    run_import_smoke || result=1
    run_pytest || result=1

    return "$result"
}

# ------------------------------------------------------------
# 7. Boucle principale
# ------------------------------------------------------------

FINAL_SUCCESS=0

for ((cycle=1; cycle<=MAX_CYCLES; cycle++)); do

    echo
    echo "############################################################"
    echo "# CYCLE $cycle / $MAX_CYCLES"
    echo "############################################################"

    BEFORE="$STATE_DIR/status_before_${cycle}.txt"
    AFTER="$STATE_DIR/status_after_${cycle}.txt"

    git status --short > "$BEFORE" || true

    if ! run_agy "$cycle"; then
        echo "[WARN] AGY cycle $cycle returned non-zero."
        echo "[INFO] Validation will decide whether to continue."
    fi

    git diff --stat || true

    if validate_cycle "$cycle"; then

        echo
        echo "############################################################"
        echo "# VALIDATION PASSED"
        echo "############################################################"

        git status --short > "$AFTER" || true

        # Re-scan final
        echo
        echo "[FINAL SCAN]"

        find src tests tools \
            -type f \
            \( -name '*.py' -o -name '*.sh' \) \
            2>/dev/null \
            | sort > "$STATE_DIR/final_code_inventory.txt"

        FINAL_SUCCESS=1
        break

    else

        echo
        echo "[INFO] Validation failed after cycle $cycle."
        echo "[INFO] AGY will receive another repair cycle."

        git status --short > "$AFTER" || true

        # Génération d'un résumé pour le cycle suivant
        {
            echo "Previous cycle: $cycle"
            echo
            echo "Current git status:"
            git status --short || true
            echo
            echo "Current Ruff:"
            ruff check . --output-format=concise 2>&1 || true
            echo
            echo "Current compile:"
            "$PYTHON_BIN" -m compileall -q src tests 2>&1 || true
            echo
            echo "Current pytest:"
            "$PYTHON_BIN" -m pytest -q 2>&1 || true
        } > "$STATE_DIR/current_state.txt"

    fi

done

# ------------------------------------------------------------
# 8. Rapport final
# ------------------------------------------------------------

REPORT="$LOG_DIR/FINAL_REPORT_${TIMESTAMP}.txt"

{
    echo "============================================================"
    echo " ACF FULL REPAIR FINAL REPORT"
    echo "============================================================"
    echo
    echo "Date       : $(date)"
    echo "Project    : $PROJECT_ROOT"
    echo "Cycles max : $MAX_CYCLES"
    echo "Success    : $FINAL_SUCCESS"
    echo
    echo "Files:"
    echo "  Total    : $TOTAL_FILES"
    echo "  Python   : $PY_FILES"
    echo "  Shell    : $SH_FILES"
    echo "  Tests    : $TEST_FILES"
    echo
    echo "Git status:"
    git status --short || true
    echo
    echo "Git diff stat:"
    git diff --stat || true
    echo
    echo "Final Ruff:"
    ruff check . --output-format=concise 2>&1 || true
    echo
    echo "Final compile:"
    "$PYTHON_BIN" -m compileall -q src tests 2>&1 || true
    echo
    echo "Final pytest:"
    "$PYTHON_BIN" -m pytest -q 2>&1 || true
    echo
    echo "============================================================"
} > "$REPORT"

echo
echo "============================================================"

if [ "$FINAL_SUCCESS" -eq 1 ]; then
    echo " ACF REPAIR SUCCESSFULLY VALIDATED"
    echo "============================================================"
    echo "Ruff       : PASS"
    echo "Compile    : PASS"
    echo "Imports    : PASS"
    echo "Pytest     : PASS"
    echo
    echo "Report: $REPORT"
    echo "Log   : $LOG"
    exit 0
else
    echo " ACF REPAIR NOT YET COMPLETE"
    echo "============================================================"
    echo "AGY reached the maximum number of cycles or could not"
    echo "produce a fully passing validation."
    echo
    echo "Report: $REPORT"
    echo "Log   : $LOG"
    exit 2
fi

