"""Saves a picture (NumPy array) as a PNG file."""
from PIL import Image


def save_png(rgb, out_path, compress_level=6):
    """Save the picture as PNG (lossless: quality is always perfect).

    rgb:            picture array from loader.load_dng()
    out_path:       where to save the file
    compress_level: 0-9. Higher = smaller file but slower. Quality does NOT change.
    """
    image = Image.fromarray(rgb)
    image.save(out_path, "PNG", compress_level=compress_level)