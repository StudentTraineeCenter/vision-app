"""Opens a .dng file and turns it into a normal picture (NumPy array).

This is the ONLY file in the project that uses rawpy.
"""
from pathlib import Path

import numpy as np
import rawpy


def load_dng(path, bit_depth=8, half_size=False) -> np.ndarray:
    """Read a .dng file and return the picture as an array.

    path:      path to the .dng file
    bit_depth: 8  -> values 0-255,   array type uint8  (enough for JPEG/PNG)
               16 -> values 0-65535, array type uint16 (more detail, for TIFF)
    half_size: if True, the picture is half the width/height, but loads ~4x faster
               (useful later for previews)

    Returns an array with shape (height, width, 3) = RGB.
    """
    path = Path(path)

    if bit_depth not in (8, 16):
        raise ValueError(f"bit_depth must be 8 or 16, got: {bit_depth}")
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    if path.suffix.lower() != ".dng":
        raise ValueError(f"Expected a .dng file, got: {path.suffix}")

    try:
        with rawpy.imread(str(path)) as raw:
            rgb = raw.postprocess(
                use_camera_wb=True,   # use the white balance the camera saved
                output_bps=bit_depth,  # 8 or 16 bits per colour channel
                half_size=half_size,
            )
    except rawpy.LibRawFileUnsupportedError as error:
        raise ValueError(
            f"rawpy cannot decode this DNG ({path.name}). "
            "It probably uses a format LibRaw does not support."
        ) from error

    return rgb