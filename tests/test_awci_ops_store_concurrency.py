"""Concurrent first opening of a cube: web handlers run in a thread pool and must never open the same
NetCDF/HDF5 file from several threads at once (segfault / xarray file-manager KeyError, found in SP3)."""

import subprocess
import sys
import textwrap
from datetime import UTC, datetime
from pathlib import Path

from acf.awci.ops.engine import DEFAULT_OPERATIONAL_PROFILE_PATH, load_profile
from acf.awci.ops.ingest import ingest_run
from tests.awci_ops_support import DOMAIN, FixtureFetcher

REPO = Path(__file__).resolve().parents[1]

PROBE = textwrap.dedent("""
    import sys, threading
    from pathlib import Path
    from acf.awci.ops import store as st
    cubes = st.CubeStore(Path(sys.argv[1]))
    for _ in range(25):
        st._open.cache_clear()
        barrier = threading.Barrier(16)
        results, errors = [], []
        def worker():
            barrier.wait()
            try:
                ds = cubes.dataset("fixture", "2026092500")
                results.append((id(ds), float(ds["awci"].isel(step=0).max())))
            except Exception as exc:
                errors.append(repr(exc))
        threads = [threading.Thread(target=worker) for _ in range(16)]
        [t.start() for t in threads]
        [t.join() for t in threads]
        assert not errors, errors[:3]
        assert len({r[0] for r in results}) == 1, "every thread must share one opened dataset"
    print("ok")
""")


def test_concurrent_first_open_is_safe(tmp_path: Path) -> None:
    ingest_run(datetime(2026, 9, 25, tzinfo=UTC), [DOMAIN], load_profile(DEFAULT_OPERATIONAL_PROFILE_PATH),
               FixtureFetcher(), tmp_path, [0, 3])
    run = subprocess.run([sys.executable, "-X", "faulthandler", "-c", PROBE, str(tmp_path)], cwd=REPO,
                         capture_output=True, text=True, timeout=300)
    assert run.returncode == 0 and "ok" in run.stdout, (run.returncode, run.stderr[-2000:])
