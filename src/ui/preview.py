from pathlib import Path
import rawpy
from PIL import Image


Image.MAX_IMAGE_PIXELS = None
CACHE_DIR = Path(__file__).resolve().parent.parent / ".cache"

def make_exported_preview(export_path, max_side=1600):
    CACHE_DIR.mkdir(exist_ok=True)
    out = CACHE_DIR / "exported_preview.jpg"
    with Image.open(export_path) as im:
        im = im.convert("RGB")
        im.thumbnail((max_side, max_side))
        im.save(out, "JPEG", quality=85)
    return str(out)

def _out_path(dng_path: str) -> Path:
    cache_dir = Path(__file__).resolve().parent.parent / ".cache"
    cache_dir.mkdir(exist_ok=True)
    return cache_dir / f"vision_preview_{Path(dng_path).stem}.jpg"

def make_preview(dng_path: str, max_side: int = 1600) -> str:
    out = _out_path(dng_path)
    if out.exists():
        return str(out)

    with rawpy.imread(dng_path) as raw:
        try:
            thumb = raw.extract_thumb()
            if thumb.format == rawpy.ThumbFormat.JPEG:
                import io
                img = Image.open(io.BytesIO(thumb.data))
            else:
                img = Image.fromarray(thumb.data)
        except (rawpy.LibRawNoThumbnailError, rawpy.LibRawUnsupportedThumbnailError):
            rgb = raw.postprocess(half_size=True, use_camera_wb=True)
            img = Image.fromarray(rgb)

    img = img.convert("RGB")
    img.thumbnail((max_side, max_side))
    img.save(out, quality=85)
    return str(out)