"""Shared helpers for AWCI ops tests: serve the real cropped fixture as if it were data.ecmwf.int."""

from pathlib import Path

from acf.awci.ops.domains import Domain
from acf.awci.ops.source_ecmwf import FetchError

FIXTURE = Path(__file__).parent / "data" / "awci_ops"
DOMAIN = Domain("fixture", "fixture", 35.0, 37.0, 2.0, 4.0, True)
#: Real precipitating deep-convection box (tropical Atlantic off Senegal), same run and steps.
WET_FIXTURE = Path(__file__).parent / "data" / "awci_ops_wet"
WET_DOMAIN = Domain("fixture_wet", "fixture wet", 15.0, 17.0, -20.0, -18.0, False)


class FixtureFetcher:
    def __init__(self, fail_steps: tuple[int, ...] = (), root: Path = FIXTURE) -> None:
        self.fail_steps = fail_steps
        self.root = root

    def _path(self, url: str) -> Path:
        name = url.rsplit("/", 1)[1]
        step = int(name.split("-")[1].removesuffix("h"))
        if step in self.fail_steps or not (self.root / name).exists():
            raise FetchError(url)
        return self.root / name

    def get_text(self, url: str) -> str:
        return self._path(url).read_text()

    def get_range(self, url: str, offset: int, length: int) -> bytes:
        return self._path(url).read_bytes()[offset : offset + length]
