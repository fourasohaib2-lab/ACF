"""
Measure a categorical/ordinal map palette: WCAG contrast on the map surface and the smallest CIEDE2000 difference
between classes, with normal vision and simulated colour-vision deficiencies.

    .venv/bin/python tools/awci/check_palette.py "#2e7d32,#66bb6a,#ffeb3b,#ff9100,#e8413c,#a52cba" VL,L,M,H,VH,EX

- WCAG 2.x relative luminance and contrast ratio (sRGB, W3C);
- CVD simulation: Machado, Oliveira & Fernandes (2009), IEEE TVCG 15(6):1291-1298, severity 1.0, on linear RGB;
- CIELAB (D65 white), then CIEDE2000 (Sharma, Wu & Dalal 2005, Color Res. Appl. 30(1):21-30).
"""

from __future__ import annotations

import argparse
import itertools
import math

import numpy as np

SURFACE = "#0b1220"  # AWCI Web map surface (web/awci/src/theme/tokens.css --surface-0)
CVD = {
    "normal": np.eye(3),
    "deutan": np.array([[0.367322, 0.860646, -0.227968], [0.280085, 0.672501, 0.047413], [-0.011820, 0.042940, 0.968881]]),
    "protan": np.array([[0.152286, 1.052583, -0.204868], [0.114503, 0.786281, 0.099216], [-0.003882, -0.048116, 1.051998]]),
    "tritan": np.array([[1.255528, -0.076749, -0.178779], [-0.078411, 0.930809, 0.147602], [0.004733, 0.691367, 0.303900]]),
}
SRGB_TO_XYZ = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])
D65 = np.array([0.95047, 1.0, 1.08883])


def linear_rgb(hex_color: str) -> np.ndarray:
    c = np.array([int(hex_color[i:i + 2], 16) / 255 for i in (1, 3, 5)])
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def luminance(hex_color: str) -> float:
    return float(np.array([0.2126, 0.7152, 0.0722]) @ linear_rgb(hex_color))


def contrast(a: str, b: str) -> float:
    hi, lo = sorted((luminance(a), luminance(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def lab(rgb_linear: np.ndarray) -> tuple[float, float, float]:
    xyz = SRGB_TO_XYZ @ np.clip(rgb_linear, 0, 1) / D65
    d = 6 / 29
    f = np.where(xyz > d**3, np.cbrt(xyz), xyz / (3 * d**2) + 4 / 29)
    return float(116 * f[1] - 16), float(500 * (f[0] - f[1])), float(200 * (f[1] - f[2]))


def _mean_hue(h1: float, h2: float, zero_chroma: bool) -> float:
    if zero_chroma:
        return h1 + h2
    if abs(h1 - h2) <= 180:
        return (h1 + h2) / 2
    return (h1 + h2 + 360) / 2 if h1 + h2 < 360 else (h1 + h2 - 360) / 2


def ciede2000(c1: tuple[float, float, float], c2: tuple[float, float, float]) -> float:
    (l1, a1, b1), (l2, a2, b2) = c1, c2
    cbar = (math.hypot(a1, b1) + math.hypot(a2, b2)) / 2
    g = 0.5 * (1 - math.sqrt(cbar**7 / (cbar**7 + 25**7)))
    a1p, a2p = (1 + g) * a1, (1 + g) * a2
    c1p, c2p = math.hypot(a1p, b1), math.hypot(a2p, b2)
    h1p, h2p = math.degrees(math.atan2(b1, a1p)) % 360, math.degrees(math.atan2(b2, a2p)) % 360
    zero = c1p * c2p == 0
    dh = 0.0 if zero else (h2p - h1p + 180) % 360 - 180
    d_l, d_c = l2 - l1, c2p - c1p
    d_h = 2 * math.sqrt(c1p * c2p) * math.sin(math.radians(dh) / 2)
    lbar, cbarp, hbar = (l1 + l2) / 2, (c1p + c2p) / 2, _mean_hue(h1p, h2p, zero)
    t = (1 - 0.17 * math.cos(math.radians(hbar - 30)) + 0.24 * math.cos(math.radians(2 * hbar))
         + 0.32 * math.cos(math.radians(3 * hbar + 6)) - 0.20 * math.cos(math.radians(4 * hbar - 63)))
    rc = 2 * math.sqrt(cbarp**7 / (cbarp**7 + 25**7))
    rt = -math.sin(math.radians(2 * 30 * math.exp(-(((hbar - 275) / 25) ** 2)))) * rc
    sl = 1 + 0.015 * (lbar - 50) ** 2 / math.sqrt(20 + (lbar - 50) ** 2)
    sc, sh = 1 + 0.045 * cbarp, 1 + 0.015 * cbarp * t
    return math.sqrt((d_l / sl) ** 2 + (d_c / sc) ** 2 + (d_h / sh) ** 2 + rt * (d_c / sc) * (d_h / sh))


def report(palette: list[str], names: list[str]) -> dict[str, object]:
    out: dict[str, object] = {"contrast": {n: round(contrast(c, SURFACE), 2) for n, c in zip(names, palette)}}
    for kind, matrix in CVD.items():
        labs = [lab(matrix @ linear_rgb(c)) for c in palette]
        worst = min((ciede2000(labs[i], labs[j]), names[i], names[j])
                    for i, j in itertools.combinations(range(len(palette)), 2))
        adjacent = min(ciede2000(labs[i], labs[i + 1]) for i in range(len(palette) - 1))
        out[kind] = {"min_all": round(worst[0], 1), "pair": f"{worst[1]}/{worst[2]}", "min_adjacent": round(adjacent, 1)}
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("palette", help="comma-separated #rrggbb colours, in class order")
    parser.add_argument("names", nargs="?", help="comma-separated class names")
    args = parser.parse_args()
    palette = args.palette.split(",")
    names = args.names.split(",") if args.names else [str(i) for i in range(len(palette))]
    for key, value in report(palette, names).items():
        print(f"{key:9s} {value}")


if __name__ == "__main__":
    main()
