"""Tests for the new acf.utils additions (serialization.py, hashing.py,
decorators.py), built while working through the full remaining-gaps
list ("On les attaque toutes un par un") for the ACF-general utils/
gap: docs/architecture/acf_awci_architecture_gap_analysis.md's own
utils/{...} row named these as missing standalone modules.

serialization.py was promoted from awci.api.routes._serialization
(built earlier this session for the AWCI HTTP API) - that module now
re-exports this one rather than keeping a duplicate implementation;
this file tests the real, generic behavior once, here.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone

import pytest

from acf.utils.decorators import retry
from acf.utils.hashing import sha256_of_bytes, sha256_of_file, sha256_of_text
from acf.utils.serialization import to_json_safe

# --------------------------------------------------------------------- serialization.py


@dataclass
class _Point:
    lat: float
    lon: float


def test_to_json_safe_converts_a_dataclass_to_a_dict():
    assert to_json_safe(_Point(1.0, 2.0)) == {"lat": 1.0, "lon": 2.0}


def test_to_json_safe_converts_datetime_to_iso_string():
    dt = datetime(2024, 1, 1, tzinfo=timezone.utc)
    assert to_json_safe(dt) == "2024-01-01T00:00:00+00:00"


def test_to_json_safe_recurses_through_lists_and_dicts():
    value = [_Point(1.0, 2.0), {"when": datetime(2024, 1, 1, tzinfo=timezone.utc)}]
    result = to_json_safe(value)
    assert result == [{"lat": 1.0, "lon": 2.0}, {"when": "2024-01-01T00:00:00+00:00"}]


def test_to_json_safe_leaves_plain_values_unchanged():
    assert to_json_safe(42) == 42
    assert to_json_safe("x") == "x"
    assert to_json_safe(None) is None


def test_to_json_safe_base64_encodes_real_binary_data():
    """Real bug found via GET /observations/{icao} against a real
    request: bytes (e.g. a real downloaded MTG satellite quicklook
    image, MTGFetchResult.image_bytes) used to fall through as
    "already JSON-safe" and crash FastAPI's real JSON serializer with
    PydanticSerializationError. Base64 is the real, reversible,
    JSON-safe encoding - decoding the result must recover the exact
    original bytes, not an approximation."""
    import base64

    raw = b"\xff\xd8\xff\xe0real-jpeg-like-bytes\x00\x01"
    encoded = to_json_safe(raw)
    assert isinstance(encoded, str)
    assert base64.b64decode(encoded) == raw

    encoded_bytearray = to_json_safe(bytearray(raw))
    assert base64.b64decode(encoded_bytearray) == raw


@dataclass
class _WithImage:
    label: str
    image_bytes: bytes | None


def test_to_json_safe_handles_bytes_nested_in_a_dataclass():
    result = to_json_safe(_WithImage(label="quicklook", image_bytes=b"\x89PNG\r\n"))
    assert result["label"] == "quicklook"
    import base64

    assert base64.b64decode(result["image_bytes"]) == b"\x89PNG\r\n"
    assert to_json_safe(_WithImage(label="none", image_bytes=None))["image_bytes"] is None


def test_awci_api_serialization_reuses_this_module_not_a_copy():
    from awci.api.routes._serialization import to_json_safe as awci_to_json_safe

    assert awci_to_json_safe is to_json_safe


# --------------------------------------------------------------------- hashing.py


def test_sha256_of_bytes_matches_stdlib_hashlib():
    assert sha256_of_bytes(b"hello") == hashlib.sha256(b"hello").hexdigest()


def test_sha256_of_text_matches_stdlib_hashlib():
    assert sha256_of_text("hello") == hashlib.sha256("hello".encode()).hexdigest()


def test_sha256_of_file_matches_stdlib_hashlib(tmp_path):
    path = tmp_path / "data.bin"
    path.write_bytes(b"hello world" * 1000)
    assert sha256_of_file(path) == hashlib.sha256(b"hello world" * 1000).hexdigest()


def test_sha256_of_file_handles_chunked_reads(tmp_path):
    path = tmp_path / "big.bin"
    content = b"x" * (1 << 21)  # bigger than the default chunk size
    path.write_bytes(content)
    assert sha256_of_file(path, chunk_size=4096) == hashlib.sha256(content).hexdigest()


# --------------------------------------------------------------------- decorators.py


def test_retry_succeeds_after_real_failures_within_attempts():
    calls: list[int] = []

    @retry(attempts=3, delay_seconds=0)
    def flaky():
        calls.append(1)
        if len(calls) < 3:
            raise ValueError("nope")
        return "ok"

    assert flaky() == "ok"
    assert len(calls) == 3


def test_retry_raises_the_last_real_exception_when_every_attempt_fails():
    calls: list[int] = []

    @retry(attempts=2, delay_seconds=0)
    def always_fails():
        calls.append(1)
        raise ValueError("nope")

    with pytest.raises(ValueError, match="nope"):
        always_fails()
    assert len(calls) == 2


def test_retry_only_catches_the_declared_exception_types():
    @retry(attempts=3, delay_seconds=0, exceptions=(ValueError,))
    def raises_type_error():
        raise TypeError("not retried")

    with pytest.raises(TypeError):
        raises_type_error()


def test_retry_rejects_attempts_below_one():
    with pytest.raises(ValueError):
        retry(attempts=0)
