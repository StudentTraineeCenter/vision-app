import io
from PIL import Image, ImageDraw


def make_histogram(path: str, w: int = 500, h: int = 180) -> bytes:
    with Image.open(path) as im:
        im = im.convert("RGB")
        im.thumbnail((600, 600))
        hist = im.histogram()

    chans = [hist[0:256], hist[256:512], hist[512:768]]
    peak = max(max(c[1:255]) for c in chans) or 1
    colors = [(255, 80, 80), (80, 220, 110), (90, 140, 255)]

    base = Image.new("RGBA", (w, h), (27, 27, 27, 255))
    for c, col in zip(chans, colors):
        pts = [(i * (w - 1) / 255, h - min(v / peak, 1.0) * (h - 6)) for i, v in enumerate(c)]
        layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        d.polygon([(0, h)] + pts + [(w, h)], fill=col + (70,))
        d.line(pts, fill=col + (255,), width=2)
        base = Image.alpha_composite(base, layer)

    out = io.BytesIO()
    base.convert("RGB").save(out, "PNG")
    return out.getvalue()