"""Generate icon.ico for PyInstaller from the app's tray image."""
import math
from pathlib import Path
from PIL import Image, ImageDraw


def make_icon_image(size: int) -> Image.Image:
    S    = size
    pad  = max(1, int(S * 0.06))
    rw   = max(2, int(S * 0.13))
    bbox = [pad, pad, S - pad, S - pad]

    img  = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    draw.ellipse(bbox, fill=(22, 22, 22, 255))
    draw.arc(bbox, start=-90, end=270, fill=(42, 42, 42, 255), width=rw)

    r, g, b = 34, 197, 94
    glow = [pad - rw, pad - rw, S - pad + rw, S - pad + rw]
    draw.arc(glow, start=-90, end=270, fill=(r, g, b, 60), width=rw + max(1, rw // 2))
    draw.arc(bbox, start=-90, end=270, fill=(r, g, b, 255), width=rw)

    return img


if __name__ == "__main__":
    # Render each size natively for sharpness, then save as multi-size ICO
    sizes  = [16, 24, 32, 48, 64, 128, 256]
    frames = [make_icon_image(s) for s in sizes]

    out = Path(__file__).parent / "icon.ico"
    # Save largest first; append the rest — PIL writes all sizes into one ICO
    frames[-1].save(
        out,
        format="ICO",
        append_images=frames[:-1],
        sizes=[(s, s) for s in sizes],
    )
    print("icon.ico generated")
