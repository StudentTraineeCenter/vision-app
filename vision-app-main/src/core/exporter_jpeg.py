
from PIL import Image


def export_jpeg(
    image,
    output_path,
    quality=85,
    subsampling="4:4:4",
    optimize=True,
    progressive=False
):
    subsampling_map = {
        "4:4:4": 0,
        "4:2:2": 1,
        "4:2:0": 2
    }

    if subsampling not in subsampling_map:
        raise ValueError("Invalid JPEG subsampling")

    if not 0 <= quality <= 100:
        raise ValueError("Quality must be between 0 and 100")

    image = image.convert("RGB")

    image.save(
        output_path,
        format="JPEG",
        quality=quality,
        subsampling=subsampling_map[subsampling],
        optimize=optimize,
        progressive=progressive
    )

    return output_path
