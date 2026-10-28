"""Saves a picture (NumPy array) as a TIFF file, 8-bit or 16-bit.

- 8-bit array  (uint8)  -> saved with Pillow
- 16-bit array (uint16) -> saved with tifffile (Pillow cannot save 16-bit RGB)
"""
import numpy as np
import tifffile
from PIL import Image

# Friendly name -> name that each library understands
PILLOW_COMPRESSION = {
    "lzw": "tiff_lzw",
    "deflate": "tiff_adobe_deflate",
    "packbits": "packbits",
    "none": None,
}
TIFFFILE_COMPRESSION = {
    "lzw": "lzw",         # needs the 'imagecodecs' package
    "deflate": "zlib",    # works without extra packages
    "packbits": "packbits",  # needs the 'imagecodecs' package
    "none": None,
}


def save_tiff(rgb, out_path, compression="lzw"):
    """Save the picture as TIFF (lossless).

    rgb:         picture array from loader.load_dng() (uint8 or uint16)
    out_path:    where to save the file
    compression: "lzw", "deflate", "packbits" or "none"
                 (the bit depth is taken from the array itself)
    """
    if compression not in PILLOW_COMPRESSION:
        raise ValueError(
            f"Unknown TIFF compression '{compression}'. "
            f"Use: {', '.join(PILLOW_COMPRESSION)}"
        )

    if rgb.dtype == np.uint16:
        # 16-bit: tifffile writes the array exactly as it is
        with open(out_path, "wb") as output:
            tifffile.imwrite(
                output,
                rgb,
                photometric="rgb",
                compression=TIFFFILE_COMPRESSION[compression],
            )
    elif rgb.dtype == np.uint8:
        # 8-bit: Pillow is fine
        with open(out_path, "wb") as output:
            Image.fromarray(rgb).save(
                output, "TIFF", compression=PILLOW_COMPRESSION[compression]
            )
    else:
        raise TypeError(f"Unsupported array type: {rgb.dtype} (need uint8 or uint16)")