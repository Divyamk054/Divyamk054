#!/usr/bin/env python3
"""
Turns a photo into an ASCII portrait.

Usage:
    pip install pillow numpy rembg onnxruntime
    python photo_to_ascii.py photo.jpg
"""

import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter, ImageOps
from rembg import remove

SRC = sys.argv[1] if len(sys.argv) > 1 else "photo.jpg"

COLS = 96
ASPECT = 1.72
BUST = 0.62
DETAIL = 2.3
WEIGHT = 0.45
RAMP = "@%#*+=-:. "


def main():
    cut = remove(Image.open(SRC))

    rgba = np.asarray(cut)
    alpha = rgba[:, :, 3]

    ys, xs = np.nonzero(alpha > 60)

    x0, x1 = xs.min(), xs.max()
    y0 = ys.min()
    y1 = int(y0 + (ys.max() - ys.min()) * BUST)

    pad = 8

    box = (
        max(0, x0 - pad),
        max(0, y0 - pad),
        min(rgba.shape[1], x1 + pad),
        min(rgba.shape[0], y1),
    )

    cut = cut.crop(box)

    a = np.asarray(cut)[:, :, 3].astype(float) / 255.0

    g = np.asarray(
        ImageOps.autocontrast(
            cut.convert("L"),
            cutoff=1
        ),
        dtype=np.int16,
    )

    h, w = g.shape

    blur = np.asarray(
        Image.fromarray(g.astype(np.uint8))
        .filter(ImageFilter.GaussianBlur(max(2, w // 55))),
        dtype=np.int16,
    )

    ink = np.clip(
        150 + (g - blur) * DETAIL + (g - 128) * WEIGHT,
        0,
        255,
    )

    inside = a > 0.5

    lo, hi = np.percentile(ink[inside], 2), np.percentile(ink[inside], 98)

    ink = np.clip(
        (ink - lo) * 255.0 / max(1, hi - lo),
        0,
        255,
    )

    rows = max(1, int(COLS * (h / w) / ASPECT))

    small = np.asarray(
        Image.fromarray(ink.astype(np.uint8))
        .resize((COLS, rows), Image.LANCZOS),
        dtype=float,
    )

    mask = np.asarray(
        Image.fromarray((a * 255).astype(np.uint8))
        .resize((COLS, rows), Image.LANCZOS),
        dtype=float,
    )

    n = len(RAMP) - 1

    lines = []

    for y in range(rows):
        line = "".join(
            RAMP[round(small[y, x] / 255 * n)]
            if mask[y, x] > 110
            else " "
            for x in range(COLS)
        )
        lines.append(line.rstrip())

    Path("portrait.txt").write_text(
        "\n".join(lines),
        encoding="utf-8",
    )

    print("\n".join(lines))
    print("\nportrait.txt created successfully.")


if __name__ == "__main__":
    main()