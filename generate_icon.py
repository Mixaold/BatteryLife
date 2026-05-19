"""Generate icon.ico for PyInstaller from the app's tray image."""
import math
from pathlib import Path
from PIL import Image, ImageDraw


def _make_icon_image(size: int) -> Image.Image:
    S   = size
    pad = int(S * 0.05)
    rw  = max(2, int(S * 0.125))
    bbox = [pad, pad, S - pad, S - pad]

    img  = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    draw.ellipse(bbox, fill=(22, 22, 22, 255))
    draw.arc(bbox, start=-90, end=270, fill=(42, 42, 42, 255), width=rw)

    r, g, b = (34, 197, 94)
    glow_bbox = [pad - rw, pad - rw, S - pad + rw, S - pad + rw]
    draw.arc(glow_bbox, start=-90, end=270, fill=(r, g, b, 50), width=rw + int(rw * 0.6))
    draw.arc(bbox, start=-90, end=270, fill=(r, g, b, 255), width=rw)

    return img


if __name__ == "__main__":
    sizes  = [16, 32, 48, 64, 128, 256]
    frames = [_make_icon_image(s) for s in sizes]
    out    = Path(__file__).parent / "icon.ico"
    frames[0].save(out, format="ICO", sizes=[(s, s) for s in sizes],
                   append_images=frames[1:])
    print(f"Generated {out}")
