"""
Read-only relay to the public EUMETSAT EUMETView WMS for AWCI Web observation overlays.

Only allow-listed layers, EPSG:3857 bounding boxes inside the Web-Mercator extent, image sizes up to
2048 px and ISO-8601 UTC times are forwarded; nothing else reaches the upstream URL. The latest time
of a layer comes from GetCapabilities (cached 5 min) and is returned in X-AWCI-Observed-At, so the UI
never shows an observation as synchronous with a forecast step. Tiles are cached on disk per
normalised request. Imagery © EUMETSAT.
"""

from __future__ import annotations

import hashlib
import re
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Annotated, Any, Protocol

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import Response

UPSTREAM = "https://view.eumetsat.int/geoserver/wms"
ATTRIBUTION = "© EUMETSAT"
MERCATOR_MAX = 20037508.342789244
USER_AGENT = "ACF-AWCI-Web/1.0 (+https://github.com/fourasohaib2-lab/ACF)"
CAPABILITIES_TTL_S = 300.0
_NS = "{http://www.opengis.net/wms}"
_TIME_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(:\d{2}(\.\d{1,3})?)?Z$")
_PERIOD_RE = re.compile(r"^PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?$")

WMS_LAYERS: dict[str, dict[str, Any]] = {
    "mtg_fd:ir105_hrfi": {"label": "MTG FCI IR 10,5 µm", "group": "satellite"},
    "mtg_fd:rgb_geocolour": {"label": "MTG GeoColour", "group": "satellite"},
    "mtg_fd:rgb_dust": {"label": "MTG Dust RGB", "group": "satellite"},
    "mtg_fd:rgb_fog": {"label": "MTG Fog RGB", "group": "satellite"},
    "mtg_fd:rgb_cloudtype": {"label": "MTG Cloud Type RGB", "group": "clouds"},
    "mtg_fd:rgb_cloudphase": {"label": "MTG Cloud Phase RGB", "group": "clouds"},
    "msg_fes:cth": {"label": "MSG hauteur du sommet des nuages", "group": "clouds"},
    "msg_fes:clm": {"label": "MSG masque nuageux", "group": "clouds"},
    "msg_fes:rgb_convection": {"label": "MSG Convection RGB", "group": "convection"},
    "msg_fes:rdt": {"label": "MSG orages à développement rapide (RDT)", "group": "convection"},
    "mtg_fd:li_afa": {"label": "MTG LI aire des éclairs cumulée", "group": "convection"},
    "msg_fes:rgb_ash": {"label": "MSG Ash RGB (cendres)", "group": "ash"},
}


class WmsUpstreamError(RuntimeError):
    """EUMETView did not return a usable answer."""


class WmsFetcher(Protocol):
    def get(self, url: str, timeout: float) -> tuple[str, bytes]: ...


class UrllibWmsFetcher:
    def get(self, url: str, timeout: float) -> tuple[str, bytes]:
        request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.headers.get_content_type(), response.read()


def _iso(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)


def _period(text: str) -> timedelta:
    match = _PERIOD_RE.match(text)
    if not match or not any(match.groups()):
        raise ValueError(f"unsupported WMS time period {text!r}")
    h, m, s = (int(g or 0) for g in match.groups())
    return timedelta(hours=h, minutes=m, seconds=s)


def parse_time_dimension(text: str, count: int) -> list[datetime]:
    """Latest `count` instants of a WMS 1.3 time dimension ("start/end/period" intervals and/or instants)."""
    found: set[datetime] = set()
    for part in (p.strip() for p in text.split(",")):
        if "/" in part:
            start, end, period = part.split("/")
            t, first, step = _iso(end), _iso(start), _period(period)
            while t >= first and len(found) < 4 * count:
                found.add(t)
                t -= step
        elif part:
            found.add(_iso(part))
    return sorted(found)[-count:]


def capabilities_time_dimensions(xml: bytes) -> dict[str, str]:
    root = ET.fromstring(xml)
    out: dict[str, str] = {}
    for layer in root.iter(f"{_NS}Layer"):
        name = layer.findtext(f"{_NS}Name")
        dim = next((d for d in layer.findall(f"{_NS}Dimension") if d.get("name") == "time"), None)
        if name and dim is not None and dim.text:
            out[name] = dim.text.strip()
    return out


def _fmt(t: datetime) -> str:
    return t.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


class WmsRelay:
    def __init__(self, fetcher: WmsFetcher, cache_dir: Path, timeout_s: float = 20.0,
                 clock: Callable[[], float] = time.monotonic) -> None:
        self.fetcher, self.cache_dir, self.timeout_s, self.clock = fetcher, Path(cache_dir), timeout_s, clock
        self._caps: tuple[float, dict[str, str]] | None = None

    def _dimensions(self) -> dict[str, str]:
        if self._caps is None or self.clock() - self._caps[0] > CAPABILITIES_TTL_S:
            url = f"{UPSTREAM}?service=WMS&version=1.3.0&request=GetCapabilities"
            try:
                _, body = self.fetcher.get(url, self.timeout_s)
                self._caps = (self.clock(), capabilities_time_dimensions(body))
            except (OSError, ET.ParseError) as exc:
                raise WmsUpstreamError(f"EUMETView capabilities unavailable: {exc}") from exc
        return self._caps[1]

    def times(self, layer: str, count: int) -> list[str]:
        dim = self._dimensions().get(layer)
        if dim is None:
            raise WmsUpstreamError(f"layer {layer} has no time dimension upstream")
        return [_fmt(t) for t in parse_time_dimension(dim, count)]

    def tile(self, layer: str, when: str | None, bbox: tuple[float, float, float, float], width: int,
             height: int) -> tuple[bytes, str]:
        observed = when or self.times(layer, 1)[-1]
        params = {"service": "WMS", "version": "1.3.0", "request": "GetMap", "layers": layer, "styles": "",
                  "crs": "EPSG:3857", "bbox": ",".join(f"{v:.3f}" for v in bbox), "width": str(width),
                  "height": str(height), "format": "image/png", "transparent": "true", "time": observed}
        query = urllib.parse.urlencode(params)
        path = self.cache_dir / f"{hashlib.sha256(query.encode()).hexdigest()}.png"
        if path.exists():
            return path.read_bytes(), observed
        try:
            content_type, body = self.fetcher.get(f"{UPSTREAM}?{query}", self.timeout_s)
        except OSError as exc:
            raise WmsUpstreamError(f"EUMETView GetMap failed: {exc}") from exc
        if content_type != "image/png":
            raise WmsUpstreamError(f"EUMETView answered {content_type} instead of a PNG")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".tmp")
        tmp.write_bytes(body)
        tmp.replace(path)
        return body, observed


router = APIRouter()


def _relay(request: Request) -> WmsRelay:
    return request.app.state.awci_wms


def _layer(name: str) -> str:
    if name not in WMS_LAYERS:
        raise HTTPException(400, f"layer {name!r} is not relayed")
    return name


def _bbox(text: str) -> tuple[float, float, float, float]:
    try:
        values = tuple(float(v) for v in text.split(","))
    except ValueError as exc:
        raise HTTPException(400, "bbox must be 4 numbers") from exc
    if len(values) != 4 or not all(abs(v) <= MERCATOR_MAX for v in values) or values[0] >= values[2] \
            or values[1] >= values[3]:
        raise HTTPException(400, "bbox must be minx,miny,maxx,maxy inside the EPSG:3857 extent")
    return values[0], values[1], values[2], values[3]


@router.get("/wms/layers")
def wms_layers() -> list[dict[str, Any]]:
    return [{"layer": name, **meta, "attribution": ATTRIBUTION} for name, meta in WMS_LAYERS.items()]


@router.get("/wms/times")
def wms_times(request: Request, layer: str, count: Annotated[int, Query(ge=1, le=48)] = 1) -> dict[str, Any]:
    try:
        times = _relay(request).times(_layer(layer), count)
    except WmsUpstreamError as exc:
        raise HTTPException(502, str(exc)) from exc
    return {"layer": layer, "label": WMS_LAYERS[layer]["label"], "times": times, "attribution": ATTRIBUTION}


@router.get("/wms", response_model=None)
def wms_tile(request: Request, layer: str, bbox: str, width: Annotated[int, Query(ge=1, le=2048)] = 256,
             height: Annotated[int, Query(ge=1, le=2048)] = 256, time: str | None = None) -> Response:
    if time is not None and not _TIME_RE.match(time):
        raise HTTPException(400, "time must be ISO-8601 UTC, e.g. 2026-09-25T18:50:00Z")
    try:
        body, observed = _relay(request).tile(_layer(layer), time, _bbox(bbox), width, height)
    except WmsUpstreamError as exc:
        raise HTTPException(502, str(exc)) from exc
    return Response(content=body, media_type="image/png", headers={
        "X-AWCI-Observed-At": observed, "X-AWCI-Attribution": "EUMETSAT",  # HTTP headers stay ASCII
        "Cache-Control": "public, max-age=86400" if time else "public, max-age=300"})
