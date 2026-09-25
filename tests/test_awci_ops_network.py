"""Real ECMWF Open Data check - opt-in: ACF_AWCI_NETWORK_TESTS=1."""

import os
from datetime import UTC, datetime

import numpy as np
import pytest

from acf.awci.ops.decode import decode_messages
from acf.awci.ops.domains import Domain
from acf.awci.ops.source_ecmwf import UrllibFetcher, fetch_step_messages, find_latest_run

pytestmark = pytest.mark.skipif(os.environ.get("ACF_AWCI_NETWORK_TESTS") != "1", reason="network test (opt-in)")


@pytest.mark.timeout(600)
def test_latest_real_step_decodes() -> None:
    fetcher = UrllibFetcher()
    run = find_latest_run(fetcher, datetime.now(UTC), last_step=0)
    fields = decode_messages(fetch_step_messages(fetcher, run, 0), [Domain("na", "na", 15, 45, -20, 40, True)])["na"]
    assert fields.pl["t"].shape == (12, 121, 241)
    assert 180.0 < np.nanmin(fields.pl["t"]) and np.nanmax(fields.pl["t"]) < 330.0
