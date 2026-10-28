"""Saves a picture (NumPy array) as a JPEG file."""
from pathlib import Path

from PIL import Image


def save_jpeg(rgb, out_path, quality=90, subsampling=2):
    """Save the picture as JPEG.

    rgb:         picture array from loader.load_dng()
    out_path:    where to save the file
    quality:     1-95 (higher = better looking, bigger file)
    subsampling: 0 = 4:4:4 (best colour), 1 = 4:2:2, 2 = 4:2:0 (smallest file)
    """
    image = Image.fromarray(rgb)
    with Path(out_path).open("wb") as output:
        image.save(
            output,
            "JPEG",
            quality=quality,
            subsampling=subsampling,
            optimize=True,  # builds optimized Huffman tables -> slightly smaller file
        )