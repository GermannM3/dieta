#!/usr/bin/env python3
"""Generate Android launcher icons from bot avatar PNG."""
from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "assets/source/bot_avatar.png"
RES = ROOT / "android/app/src/main/res"
ASSETS = ROOT / "assets/images"
BG = (242, 228, 200, 255)  # cream from bot avatar

SIZES = {
    "mipmap-mdpi": 48,
    "mipmap-hdpi": 72,
    "mipmap-xhdpi": 96,
    "mipmap-xxhdpi": 144,
    "mipmap-xxxhdpi": 192,
}


def circular_crop(im: Image.Image, inset: float = 0.04) -> Image.Image:
    w, h = im.size
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    im = im.crop((left, top, left + side, top + side))
    if inset > 0:
        pad = int(side * inset)
        im = im.crop((pad, pad, side - pad, side - pad))
    mask = Image.new("L", im.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, im.size[0] - 1, im.size[1] - 1), fill=255)
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    out.paste(im.convert("RGBA"), (0, 0), mask)
    return out


def make_icon(size: int) -> Image.Image:
    src = Image.open(SRC).convert("RGBA")
    fg = circular_crop(src, inset=0.02)
    canvas = Image.new("RGBA", (size, size), BG)
    fg_size = int(size * 0.88)
    fg = fg.resize((fg_size, fg_size), Image.Resampling.LANCZOS)
    offset = (size - fg_size) // 2
    canvas.paste(fg, (offset, offset), fg)
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size - 1, size - 1), fill=255)
    final = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    final.paste(canvas, (0, 0), mask)
    return final


def make_foreground(size: int) -> Image.Image:
    src = Image.open(SRC).convert("RGBA")
    fg = circular_crop(src, inset=0.08)
    fg_size = int(size * 0.72)
    fg = fg.resize((fg_size, fg_size), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    canvas.paste(fg, ((size - fg_size) // 2, (size - fg_size) // 2 - int(size * 0.04)), fg)
    return canvas


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    logo = make_icon(512)
    logo.save(ASSETS / "app_logo.png")

    store_dir = ROOT / "store"
    store_dir.mkdir(parents=True, exist_ok=True)
    for px in (512, 256, 128, 64, 32):
        icon = make_icon(px)
        out = store_dir / f"rustore_icon_{px}.png"
        icon.save(out, optimize=True)
        size_kb = out.stat().st_size / 1024
        print(f"  {out.name}: {px}x{px}, {size_kb:.0f} KB")

    for folder, px in SIZES.items():
        out_dir = RES / folder
        out_dir.mkdir(parents=True, exist_ok=True)
        icon = make_icon(px)
        icon.save(out_dir / "ic_launcher.png")
        icon.save(out_dir / "ic_launcher_round.png")
        fg = make_foreground(px)
        fg.save(out_dir / "ic_launcher_foreground.png")

    anydpi = RES / "mipmap-anydpi-v26"
    anydpi.mkdir(parents=True, exist_ok=True)
    (anydpi / "ic_launcher.xml").write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
    <background android:drawable="@color/ic_launcher_background"/>
    <foreground android:drawable="@mipmap/ic_launcher_foreground"/>
</adaptive-icon>
""",
        encoding="utf-8",
    )
    (anydpi / "ic_launcher_round.xml").write_text(
        (anydpi / "ic_launcher.xml").read_text(encoding="utf-8"),
        encoding="utf-8",
    )

    colors_dir = RES / "values"
    colors_dir.mkdir(parents=True, exist_ok=True)
    colors_file = colors_dir / "ic_launcher_colors.xml"
    colors_file.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <color name="ic_launcher_background">#F2E4C8</color>
</resources>
""",
        encoding="utf-8",
    )
    print("Generated launcher icons, store/rustore_icon_*.png, assets/images/app_logo.png")


if __name__ == "__main__":
    main()
