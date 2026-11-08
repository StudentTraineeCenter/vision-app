from pathlib import Path
import rawpy
from PIL import Image

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