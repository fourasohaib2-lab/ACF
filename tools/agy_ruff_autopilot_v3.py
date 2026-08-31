from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# ============================================================================
# CONFIGURATION & CONSTANTS
# ============================================================================

MAX_ITERATIONS = 1000
MAX_CONTEXT_LINES = 10
MAX_TOKENS = 96
TIMEOUT = 420
SLEEP_AFTER_TIMEOUT = 60

IGNORE_CODES = {
    "BLE001",
    "S110",
    "E722",
}

TARGET_CODES = {
    "RUF012",
    "RUF013",
    "DTZ003",
    "DTZ005",
    "F841",
    "I001",
    "UP007",
    "C401",
    "C414",
    "PIE810",
    "PLW1510",
    "F821",
    "F811",
}

RUFF_AUTOFIX_CODES = {
    "I001",
    "UP007",
    "C401",
    "C414",
    "PIE810",
}

PRIORITY_ORDER = [
    "I001",
    "UP007",
    "C401",
    "C414",
    "PIE810",
    "RUF012",
    "RUF013",
    "DTZ003",
    "DTZ005",
    "PLW1510",
    "F841",
    "F811",
    "F821",
]

MAX_FILE_BYTES = 2 * 1024 * 1024

REPORT_DIR = Path("reports")
BACKUP_DIR = REPORT_DIR / "agy_ruff_v3_backups"

# ============================================================================
# DATA STRUCTURES
# ============================================================================


@dataclass
class RuffError:
    code: str
    message: str
    filename: str
    line: int
    column: int
    end_line: int | None = None
    end_column: int | None = None

    def key(self) -> str:
        return f"{self.code}:{self.filename}:{self.line}:{self.column}"


@dataclass
class IterationResult:
    iteration: int
    status: str
    code: str
    filename: str
    line: int
    message: str
    duration: float
    validation: str
    detail: str = ""


# ============================================================================
# REPOSITORY & ENVIRONMENT
# ============================================================================


def find_repo_root(start_path: Path | None = None) -> Path:
    """Find repository root containing .git directory."""
    current = (start_path or Path.cwd()).resolve()
    for parent in [current, *current.parents]:
        if (parent / ".git").is_dir() or (parent / ".git").is_file():
            return parent
    return current


def locate_binary(name: str, repo_root: Path) -> str | None:
    """Locate binary in repo venv or PATH."""
    venv_bin = repo_root / ".venv" / "bin" / name
    if venv_bin.is_file() and os.access(venv_bin, os.X_OK):
        return str(venv_bin)

    local_bin = Path.home() / ".local" / "bin" / name
    if local_bin.is_file() and os.access(local_bin, os.X_OK):
        return str(local_bin)

    which_path = shutil.which(name)
    if which_path:
        return which_path

    return None


def verify_environment(repo_root: Path) -> tuple[str, str, str, str | None]:
    """
    Verify required tools and repository.
    Returns (python_bin, ruff_bin, git_bin, agy_bin).
    Exits if any critical tool is missing.
    """
    python_bin = sys.executable or shutil.which("python3") or shutil.which("python")
    ruff_bin = locate_binary("ruff", repo_root)
    git_bin = shutil.which("git")
    agy_bin = locate_binary("agy", repo_root)

    # Check git repository
    is_git_repo = (repo_root / ".git").exists()

    # Get versions
    python_ver = f"Python {sys.version.split()[0]}"

    ruff_ver = "unknown"
    if ruff_bin:
        try:
            r_out = subprocess.run([ruff_bin, "--version"], capture_output=True, text=True, check=False)
            ruff_ver = r_out.stdout.strip() or r_out.stderr.strip()
        except Exception:
            ruff_ver = "failed to get version"

    git_ver = "unknown"
    if git_bin:
        try:
            g_out = subprocess.run([git_bin, "--version"], capture_output=True, text=True, check=False)
            git_ver = g_out.stdout.strip()
        except Exception:
            git_ver = "failed to get version"

    print(f"Repository: {repo_root}")
    print(f"Python: {python_bin} ({python_ver})")
    print(f"Ruff: {ruff_bin} ({ruff_ver})")
    print(f"Git: {git_bin} ({git_ver})")

    if not is_git_repo or not python_bin or not ruff_bin or not git_bin:
        print("\nSTOP: Missing critical tool or invalid git repository.")
        if not is_git_repo:
            print(" - Not a valid git repository (.git missing)")
        if not python_bin:
            print(" - Python binary not found")
        if not ruff_bin:
            print(" - Ruff binary not found")
        if not git_bin:
            print(" - Git binary not found")
        sys.exit(1)

    return python_bin, ruff_bin, git_bin, agy_bin


# ============================================================================
# RUFF ANALYSIS & CLASSIFICATION
# ============================================================================


def run_ruff_check(repo_root: Path, ruff_bin: str, target: str | Path | None = None) -> list[RuffError]:
    """Run ruff check in JSON output mode and parse errors."""
    target_str = str(target) if target else "."
    cmd = [ruff_bin, "check", target_str, "--output-format", "json", "--exclude", "reports"]
    proc = subprocess.run(cmd, cwd=repo_root, capture_output=True, text=True, check=False)

    if not proc.stdout.strip():
        return []

    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return []

    errors: list[RuffError] = []
    for item in data:
        loc = item.get("location", {})
        end_loc = item.get("end_location")
        fn = item.get("filename", "")
        if not os.path.isabs(fn):
            fn = str((repo_root / fn).resolve())

        errors.append(
            RuffError(
                code=item.get("code", ""),
                message=item.get("message", ""),
                filename=fn,
                line=int(loc.get("row", 1)),
                column=int(loc.get("column", 1)),
                end_line=int(end_loc["row"]) if end_loc and "row" in end_loc else None,
                end_column=int(end_loc["column"]) if end_loc and "column" in end_loc else None,
            )
        )
    return errors


def classify_errors(errors: list[RuffError]) -> tuple[list[RuffError], list[RuffError], list[RuffError]]:
    """Partition errors into (target_errors, ignore_errors, other_errors)."""
    targets: list[RuffError] = []
    ignored: list[RuffError] = []
    others: list[RuffError] = []

    for err in errors:
        if err.code in TARGET_CODES:
            targets.append(err)
        elif err.code in IGNORE_CODES:
            ignored.append(err)
        else:
            others.append(err)

    return targets, ignored, others


def sort_target_errors(errors: list[RuffError]) -> list[RuffError]:
    """Sort target errors according to priority order, file, and line."""

    def sort_key(e: RuffError) -> tuple[int, str, int, int]:
        p = PRIORITY_ORDER.index(e.code) if e.code in PRIORITY_ORDER else 999
        return (p, e.filename, e.line, e.column)

    return sorted(errors, key=sort_key)


def run_ruff_autofix(repo_root: Path, ruff_bin: str) -> None:
    """Run ruff check . --fix."""
    print("Running initial Ruff autofix (ruff check . --fix)...")
    subprocess.run(
        [ruff_bin, "check", ".", "--fix", "--exclude", "reports"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )


# ============================================================================
# CONTEXT EXTRACTION & PROMPT
# ============================================================================


def extract_context(file_path: Path, error_line: int) -> tuple[str, int, int, list[str]]:
    """
    Extract up to MAX_CONTEXT_LINES centered around error_line.
    Returns (formatted_context_text, start_line, end_line, context_lines_raw).
    """
    lines = file_path.read_text(encoding="utf-8", errors="replace").splitlines()
    total_lines = len(lines)
    if total_lines == 0:
        return "", 1, 1, []

    # Calculate window
    half_window = MAX_CONTEXT_LINES // 2
    start_line = max(1, error_line - half_window)
    end_line = min(total_lines, start_line + MAX_CONTEXT_LINES - 1)
    start_line = max(1, end_line - MAX_CONTEXT_LINES + 1)

    formatted_lines: list[str] = []
    raw_lines: list[str] = []

    for i in range(start_line, end_line + 1):
        line_content = lines[i - 1]
        raw_lines.append(line_content)
        prefix = ">>>" if i == error_line else "   "
        formatted_lines.append(f"{prefix} {i:4d} | {line_content}")

    return "\n".join(formatted_lines), start_line, end_line, raw_lines


def build_agy_prompt(
    error: RuffError,
    rel_path: str,
    context_text: str,
    start_line: int,
    end_line: int,
) -> str:
    """Construct minimal single-error prompt for AGY."""
    return f"""You are a minimal Python/Ruff fixer.

Fix ONLY this Ruff error.

CODE: {error.code}
FILE: {rel_path}
LINE: {error.line}
COLUMN: {error.column}
MESSAGE: {error.message}

Rules:
- Make the smallest possible change.
- Fix ONLY this error.
- Do not refactor.
- Do not rename unrelated symbols.
- Do not modify unrelated lines.
- Preserve project behavior.
- Return ONLY the exact replacement code for the given context (lines {start_line} to {end_line}).
- Do not include line numbers or >>> in your output.
- No markdown.
- No explanation.
- Maximum {MAX_TOKENS} output tokens.

Context (lines {start_line} to {end_line}):
{context_text}"""


# ============================================================================
# AGY INVOCATION & OUTPUT CLEANING
# ============================================================================


def clean_model_output(raw: str) -> str:
    """Strip markdown code blocks, trailing spaces, and line prefix artifacts."""
    text = raw.strip("\r\n")
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines)

    cleaned_lines = []
    for line in text.splitlines():
        # Remove line prefix like '>>> 123 | ' or '123 | ' if the model echoed them
        m = re.match(r"^(?:>>>|\s*)\s*\d+\s*\|\s?(.*)$", line)
        if m:
            cleaned_lines.append(m.group(1))
        else:
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines)


def query_agy(agy_bin: str | None, prompt: str) -> tuple[str | None, str, float]:
    """
    Invoke AGY CLI with prompt.
    Returns (output_or_none, status, duration).
    """
    if not agy_bin:
        return None, "AGY_NOT_FOUND", 0.0

    start_time = time.perf_counter()
    cmd = [
        agy_bin,
        "--print",
        prompt,
        "--print-timeout",
        f"{TIMEOUT}s",
        "--disable-slash-commands",
        "--dangerously-skip-permissions",
    ]
    _ = shlex.join(cmd)

    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=TIMEOUT,
            check=False,
        )
        duration = time.perf_counter() - start_time

        if proc.returncode != 0:
            return None, "AGY_FAILED", duration

        raw_output = proc.stdout.strip("\r\n")
        if not raw_output:
            return None, "EMPTY_RESPONSE", duration

        cleaned = clean_model_output(raw_output)
        return cleaned, "OK", duration

    except subprocess.TimeoutExpired:
        duration = time.perf_counter() - start_time
        return None, "TIMEOUT", duration
    except Exception as exc:
        duration = time.perf_counter() - start_time
        return None, f"EXCEPTION: {exc}", duration


# ============================================================================
# BACKUP, PATCH & VALIDATION
# ============================================================================


def create_backup(repo_root: Path, file_path: Path, iteration: int, code: str) -> Path:
    """Create timestamped/indexed backup in BACKUP_DIR."""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    rel_str = str(file_path.relative_to(repo_root)).replace(os.sep, "_")
    backup_name = f"{iteration:04d}_{code}_{rel_str}"
    backup_path = BACKUP_DIR / backup_name
    shutil.copy2(file_path, backup_path)
    return backup_path


def restore_backup(backup_path: Path, file_path: Path) -> None:
    """Restore file from backup."""
    if backup_path.exists():
        shutil.copy2(backup_path, file_path)


def apply_patch(
    file_path: Path,
    start_line: int,
    end_line: int,
    replacement_content: str,
) -> None:
    """Replace lines start_line..end_line (1-indexed) with replacement_content."""
    text = file_path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()

    rep_lines = replacement_content.splitlines() if replacement_content else []
    new_lines = lines[: start_line - 1] + rep_lines + lines[end_line:]

    result_text = "\n".join(new_lines)
    if text.endswith("\n"):
        result_text += "\n"

    file_path.write_text(result_text, encoding="utf-8")


def apply_single_line_patch(
    file_path: Path,
    target_line: int,
    replacement_content: str,
) -> None:
    """Replace only the target_line with replacement_content."""
    text = file_path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()

    rep_lines = replacement_content.splitlines() if replacement_content else []
    new_lines = lines[: target_line - 1] + rep_lines + lines[target_line:]

    result_text = "\n".join(new_lines)
    if text.endswith("\n"):
        result_text += "\n"

    file_path.write_text(result_text, encoding="utf-8")


def validate_patch(
    repo_root: Path,
    python_bin: str,
    ruff_bin: str,
    file_path: Path,
    error: RuffError,
) -> tuple[bool, str]:
    """
    Validate modified file:
    1. git diff -- <file> (ensure changes are small)
    2. python -m py_compile <file>
    3. ruff check <file> (ensure target error resolved and no fatal regressions)
    """
    # 1. Check git diff magnitude
    diff_proc = subprocess.run(
        ["git", "diff", "--", str(file_path)],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    diff_lines = diff_proc.stdout.splitlines()
    changed_lines_count = sum(1 for line in diff_lines if line.startswith(("+", "-")))
    if changed_lines_count > 60:
        return False, "ROLLBACK_DIFF_TOO_LARGE"

    # 2. py_compile
    compile_proc = subprocess.run(
        [python_bin, "-m", "py_compile", str(file_path)],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if compile_proc.returncode != 0:
        err_msg = compile_proc.stderr.strip() or compile_proc.stdout.strip()
        return False, f"ROLLBACK_COMPILE: {err_msg}"

    # 3. ruff check file
    file_errors = run_ruff_check(repo_root, ruff_bin, target=file_path)
    # Check if this exact error still exists
    for fe in file_errors:
        if fe.code == error.code and fe.line == error.line:
            return False, "ROLLBACK_RUFF"
    # Check if new syntax errors appeared
    for fe in file_errors:
        if fe.code.startswith("E9") or fe.code.startswith("F9"):
            return False, f"ROLLBACK_RUFF_SYNTAX: {fe.message}"

    return True, "FIXED"


# ============================================================================
# REPORTS
# ============================================================================


def generate_reports(
    repo_root: Path,
    start_time: str,
    iterations_run: int,
    fixed_count: int,
    failed_count: int,
    skipped_count: int,
    initial_target_count: int,
    final_targets: list[RuffError],
    final_ignored: list[RuffError],
    final_others: list[RuffError],
    results: list[IterationResult],
) -> tuple[Path, Path]:
    """Generate timestamped JSON and TXT reports in reports/."""
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")

    json_path = REPORT_DIR / f"agy_ruff_autopilot_v3_{timestamp}.json"
    txt_path = REPORT_DIR / f"agy_ruff_autopilot_v3_{timestamp}.txt"

    code_counts: dict[str, int] = {}
    for code in TARGET_CODES:
        code_counts[code] = sum(1 for r in results if r.code == code and r.status == "FIXED")

    ignored_counts: dict[str, int] = {}
    for code in IGNORE_CODES:
        ignored_counts[code] = sum(1 for e in final_ignored if e.code == code)

    report_data: dict[str, Any] = {
        "timestamp": timestamp,
        "start_time": start_time,
        "configuration": {
            "MAX_ITERATIONS": MAX_ITERATIONS,
            "MAX_CONTEXT_LINES": MAX_CONTEXT_LINES,
            "MAX_TOKENS": MAX_TOKENS,
            "TIMEOUT": TIMEOUT,
            "SLEEP_AFTER_TIMEOUT": SLEEP_AFTER_TIMEOUT,
            "MAX_FILE_BYTES": MAX_FILE_BYTES,
            "TARGET_CODES": sorted(TARGET_CODES),
            "IGNORE_CODES": sorted(IGNORE_CODES),
            "RUFF_AUTOFIX_CODES": sorted(RUFF_AUTOFIX_CODES),
        },
        "iterations": iterations_run,
        "initial_target_errors": initial_target_count,
        "final_target_errors": len(final_targets),
        "fixed": fixed_count,
        "failed": failed_count,
        "skipped": skipped_count,
        "ignored": len(final_ignored),
        "other_errors": len(final_others),
        "fixed_by_target_code": code_counts,
        "ignored_by_code": ignored_counts,
        "results": [asdict(r) for r in results],
        "remaining_errors": [asdict(e) for e in final_targets],
    }

    json_path.write_text(json.dumps(report_data, indent=2), encoding="utf-8")

    # TXT Report
    txt_lines = [
        "================================================================================",
        "ACF RUFF AUTOPILOT V3 REPORT",
        "================================================================================",
        f"Timestamp: {timestamp}",
        f"Initial TARGET errors: {initial_target_count}",
        f"Final TARGET errors: {len(final_targets)}",
        f"Fixed: {fixed_count}",
        f"Failed: {failed_count}",
        f"Skipped: {skipped_count}",
        "",
        "TARGET CODES SUMMARY (Fixed / Target):",
    ]
    for code in sorted(TARGET_CODES):
        rem = sum(1 for e in final_targets if e.code == code)
        fix = code_counts.get(code, 0)
        txt_lines.append(f"{code:10}: fixed={fix}, remaining={rem}")

    txt_lines.extend(
        [
            "",
            "IGNORED CODES SUMMARY:",
        ]
    )
    for code in sorted(IGNORE_CODES):
        cnt = ignored_counts.get(code, 0)
        txt_lines.append(f"{code:10}: {cnt}")

    txt_lines.extend(
        [
            "",
            "ITERATION LOGS:",
        ]
    )
    for r in results:
        txt_lines.append(
            f"[{r.iteration:04d}] {r.status:20} | {r.code:8} | {r.filename}:{r.line} | {r.duration:.2f}s | {r.validation} | {r.detail}"
        )

    if final_targets:
        txt_lines.extend(
            [
                "",
                "REMAINING TARGET ERRORS:",
            ]
        )
        for e in final_targets:
            txt_lines.append(f" - {e.code:8} {e.filename}:{e.line}:{e.column} | {e.message}")

    txt_path.write_text("\n".join(txt_lines) + "\n", encoding="utf-8")

    return json_path, txt_path


# ============================================================================
# MAIN DRIVER
# ============================================================================


def main() -> int:
    parser = argparse.ArgumentParser(description="ACF Ruff Autopilot V3")
    parser.add_argument(
        "--dry-run", action="store_true", help="Analyze errors without modifying repository or querying LLM"
    )
    parser.add_argument("--no-autofix", action="store_true", help="Skip initial ruff check . --fix step")
    parser.add_argument("--max-iterations", type=int, default=MAX_ITERATIONS, help="Maximum autopilot iterations")
    parser.add_argument("--file", type=str, default=None, help="Target specific file")
    args = parser.parse_args()

    start_iso = datetime.now(UTC).isoformat()
    repo_root = find_repo_root()
    os.chdir(repo_root)

    print("================================================================================")
    print("ACF RUFF AUTOPILOT V3 - INITIALIZING")
    print("================================================================================")

    python_bin, ruff_bin, git_bin, agy_bin = verify_environment(repo_root)

    # Initial Ruff Check
    initial_errors = run_ruff_check(repo_root, ruff_bin, target=args.file)
    initial_targets, initial_ignored, initial_others = classify_errors(initial_errors)

    print("\nInitial Analysis:")
    print(f" - Total Ruff errors   : {len(initial_errors)}")
    print(f" - TARGET errors       : {len(initial_targets)}")
    print(f" - IGNORE errors       : {len(initial_ignored)}")
    print(f" - OTHER errors        : {len(initial_others)}")

    if args.dry_run:
        print("\n[DRY-RUN MODE] No files will be modified. No LLM calls will be made.")
        print("\nTarget Errors:")
        for err in sort_target_errors(initial_targets):
            print(f"  {err.code:8} {Path(err.filename).relative_to(repo_root)}:{err.line}:{err.column} - {err.message}")
        print("\nIgnored Errors:")
        for err in initial_ignored:
            print(f"  {err.code:8} {Path(err.filename).relative_to(repo_root)}:{err.line}:{err.column} - {err.message}")
        return 0

    # Autofix Phase
    if not args.no_autofix:
        run_ruff_autofix(repo_root, ruff_bin)
        post_fix_errors = run_ruff_check(repo_root, ruff_bin, target=args.file)
        post_targets, post_ignored, post_others = classify_errors(post_fix_errors)
        print(f"Post-autofix TARGET errors: {len(post_targets)} (was {len(initial_targets)})")
    else:
        post_targets = initial_targets

    # Main Remediation Loop
    results: list[IterationResult] = []
    attempt_counts: dict[str, int] = {}
    iteration = 0
    fixed_count = 0
    failed_count = 0
    skipped_count = 0

    max_iter = args.max_iterations

    print(f"\nStarting Remediation Loop (Max iterations: {max_iter})...\n")

    while iteration < max_iter:
        current_errors = run_ruff_check(repo_root, ruff_bin, target=args.file)
        current_targets, _, _ = classify_errors(current_errors)
        sorted_targets = sort_target_errors(current_targets)

        # Filter out errors that exceeded retry limit
        actionable_targets = [e for e in sorted_targets if attempt_counts.get(e.key(), 0) < 3]

        if not current_targets:
            print("\n>>> SUCCESS: All TARGET Ruff errors have been resolved! <<<")
            break

        if not actionable_targets:
            print(f"\n>>> STOPPING: All {len(current_targets)} remaining TARGET errors have reached retry limit. <<<")
            break

        target_error = actionable_targets[0]
        err_key = target_error.key()
        attempt_counts[err_key] = attempt_counts.get(err_key, 0) + 1
        iteration += 1

        file_path = Path(target_error.filename)
        rel_path = str(file_path.relative_to(repo_root))

        print(
            f"[{iteration:04d}/{max_iter}] Attempt {attempt_counts[err_key]}/3 on {target_error.code} at {rel_path}:{target_error.line}"
        )

        # Check file size protection
        if file_path.stat().st_size > MAX_FILE_BYTES:
            print(f" - SKIP: File size exceeds MAX_FILE_BYTES ({file_path.stat().st_size} bytes)")
            results.append(
                IterationResult(
                    iteration=iteration,
                    status="SKIPPED_FILE_TOO_LARGE",
                    code=target_error.code,
                    filename=rel_path,
                    line=target_error.line,
                    message=target_error.message,
                    duration=0.0,
                    validation="SKIP",
                    detail=f"Size {file_path.stat().st_size} > {MAX_FILE_BYTES}",
                )
            )
            skipped_count += 1
            continue

        # Extract context
        context_text, start_line, end_line, raw_lines = extract_context(file_path, target_error.line)

        # Build prompt
        prompt = build_agy_prompt(target_error, rel_path, context_text, start_line, end_line)

        # Create Backup
        backup_path = create_backup(repo_root, file_path, iteration, target_error.code)

        # Query AGY
        model_output, agy_status, duration = query_agy(agy_bin, prompt)

        if agy_status == "TIMEOUT":
            print(f" - TIMEOUT after {TIMEOUT}s. Sleeping {SLEEP_AFTER_TIMEOUT}s...")
            restore_backup(backup_path, file_path)
            results.append(
                IterationResult(
                    iteration=iteration,
                    status="TIMEOUT",
                    code=target_error.code,
                    filename=rel_path,
                    line=target_error.line,
                    message=target_error.message,
                    duration=duration,
                    validation="FAIL",
                    detail=f"Timeout {TIMEOUT}s",
                )
            )
            failed_count += 1
            time.sleep(SLEEP_AFTER_TIMEOUT)
            continue

        if agy_status != "OK" or model_output is None:
            print(f" - AGY Query failed: {agy_status}")
            restore_backup(backup_path, file_path)
            results.append(
                IterationResult(
                    iteration=iteration,
                    status=agy_status,
                    code=target_error.code,
                    filename=rel_path,
                    line=target_error.line,
                    message=target_error.message,
                    duration=duration,
                    validation="FAIL",
                    detail=f"AGY status: {agy_status}",
                )
            )
            failed_count += 1
            continue

        # Check if output is unchanged
        orig_snippet = "\n".join(raw_lines)
        if model_output.strip() == orig_snippet.strip():
            print(" - NO_CHANGE: Model output is identical to original context")
            restore_backup(backup_path, file_path)
            results.append(
                IterationResult(
                    iteration=iteration,
                    status="NO_CHANGE",
                    code=target_error.code,
                    filename=rel_path,
                    line=target_error.line,
                    message=target_error.message,
                    duration=duration,
                    validation="FAIL",
                    detail="Model returned unchanged snippet",
                )
            )
            failed_count += 1
            continue

        # Try Context Replacement first
        apply_patch(file_path, start_line, end_line, model_output)
        is_valid, val_status = validate_patch(repo_root, python_bin, ruff_bin, file_path, target_error)

        # If context replacement failed, test single line replacement as fallback
        if not is_valid:
            restore_backup(backup_path, file_path)
            apply_single_line_patch(file_path, target_error.line, model_output)
            is_valid, val_status = validate_patch(repo_root, python_bin, ruff_bin, file_path, target_error)

        if is_valid:
            print(f" - FIXED ({duration:.2f}s) - py_compile & ruff check PASSED")
            results.append(
                IterationResult(
                    iteration=iteration,
                    status="FIXED",
                    code=target_error.code,
                    filename=rel_path,
                    line=target_error.line,
                    message=target_error.message,
                    duration=duration,
                    validation="PASS",
                    detail="",
                )
            )
            fixed_count += 1
        else:
            print(f" - VALIDATION FAILED: {val_status} -> Rolling back.")
            restore_backup(backup_path, file_path)
            results.append(
                IterationResult(
                    iteration=iteration,
                    status=val_status,
                    code=target_error.code,
                    filename=rel_path,
                    line=target_error.line,
                    message=target_error.message,
                    duration=duration,
                    validation="FAIL",
                    detail=val_status,
                )
            )
            failed_count += 1

    # Final Analysis
    final_errors = run_ruff_check(repo_root, ruff_bin, target=args.file)
    final_targets, final_ignored, final_others = classify_errors(final_errors)

    json_report, txt_report = generate_reports(
        repo_root=repo_root,
        start_time=start_iso,
        iterations_run=iteration,
        fixed_count=fixed_count,
        failed_count=failed_count,
        skipped_count=skipped_count,
        initial_target_count=len(initial_targets),
        final_targets=final_targets,
        final_ignored=final_ignored,
        final_others=final_others,
        results=results,
    )

    print("\n================================================================================")
    print("ACF RUFF AUTOPILOT V3 - FINAL SUMMARY")
    print("================================================================================")
    print(f"Initial TARGET errors: {len(initial_targets)}")
    print(f"Final TARGET errors  : {len(final_targets)}")
    print(f"Fixed                : {fixed_count}")
    print(f"Failed               : {failed_count}")
    print(f"Skipped              : {skipped_count}")
    print(f"\nIgnored errors       : {len(final_ignored)}")
    print(f"Other Ruff errors    : {len(final_others)}")
    print("\nReports generated:")
    print(f" - JSON: {json_report}")
    print(f" - TXT : {txt_report}")

    if len(final_targets) == 0:
        print("\nSTATUS: SUCCESS (0 TARGET errors remaining)")
        return 0
    else:
        print(f"\nSTATUS: INCOMPLETE ({len(final_targets)} TARGET errors remaining)")
        return 1


if __name__ == "__main__":
    sys.exit(main())
