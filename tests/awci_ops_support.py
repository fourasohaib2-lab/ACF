"""Shared helpers for AWCI ops tests: serve the real cropped fixture as if it were data.ecmwf.int."""

from pathlib import Path

from acf.awci.ops.domains import Domain
from acf.awci.ops.source_ecmwf import FetchError

FIXTURE = Path(__file__).parent / "data" / "awci_ops"
DOMAIN = Domain("fixture", "fixture", 35.0, 37.0, 2.0, 4.0, True)


class FixtureFetcher:
    def __init__(self, fail_steps: tuple[int, ...] = ()) -> None:
        self.fail_steps = fail_steps

    def _path(self, url: str) -> Path:
        name = url.rsplit("/", 1)[1]
        step = int(name.split("-")[1].removesuffix("h"))
        if step in self.fail_steps or not (FIXTURE / name).exists():
            raise FetchError(url)
        return FIXTURE / name

    def get_text(self, url: str) -> str:
        return self._path(url).read_text()

    def get_range(self, url: str, offset: int, length: int) -> bytes:
        return self._path(url).read_bytes()[offset : offset + length]
