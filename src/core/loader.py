"""Opens a .dng file and turns it into a normal picture (NumPy array).

This is the ONLY file in the project that uses rawpy.
"""
from pathlib import Path

import numpy as np
import rawpy
import tifffile


def _dng_tag_values(page, name, rational=False):
    tag = page.tags.get(name)
    if tag is None:
        return None
    values = np.asarray(tag.value, dtype=np.float32).reshape(-1)
    if rational and values.size % 2 == 0:
        values = values[::2] / values[1::2]
    return values


def _apply_orientation(rgb, orientation):
    return {
        2: np.fliplr(rgb),
        3: np.rot90(rgb, 2),
        4: np.flipud(rgb),
        5: np.transpose(rgb, (1, 0, 2))[:, ::-1],
        6: np.rot90(rgb, 3),
        7: np.transpose(rgb, (1, 0, 2))[::-1],
        8: np.rot90(rgb),
    }.get(int(orientation), rgb)


def _develop_linear_dng(rgb, page):
    """Convert a linear DNG RGB array into display-ready sRGB values."""
    data = rgb.astype(np.float32)
    white_level = _dng_tag_values(page, "WhiteLevel")
    white = float(white_level[0]) if white_level is not None else float(data.max())

    # Some phone DNGs declare 16-bit samples but store 10-bit values.
    if white > 4095 and data.max() <= 4095:
        white = float((1 << int(np.ceil(np.log2(max(data.max(), 1) + 1)))) - 1)

    black_level = _dng_tag_values(page, "BlackLevel")
    black = float(np.mean(black_level)) if black_level is not None else 0.0
    data = np.clip((data - black) / max(white - black, 1.0), 0.0, 1.0)

    neutral = _dng_tag_values(page, "AsShotNeutral", rational=True)
    if neutral is not None and neutral.size >= 3:
        gains = 1.0 / np.maximum(neutral[:3], 1e-6)
        data *= np.power(gains, 0.25).reshape(1, 1, 3)

    data = np.clip(data, 0.0, 1.0)
    data *= np.array([1.0, 0.75, 1.0], dtype=np.float32).reshape(1, 1, 3)
    data *= 0.5
    data = np.where(
        data <= 0.0031308,
        data * 12.92,
        1.055 * np.power(data, 1.0 / 2.4) - 0.055,
    )
    luma = (
        data[..., 0] * 0.2126
        + data[..., 1] * 0.7152
        + data[..., 2] * 0.0722
    )
    data = luma[..., None] + (data - luma[..., None]) * 1.35
    data = (data - 0.18) * 1.3 + 0.18
    data = np.clip(data, 0.0, 1.0)
    return data


def _load_tiff_dng(path, bit_depth):
    """Load RGB DNG variants that LibRaw cannot unpack, such as JPEG XL DNG."""
    try:
        with tifffile.TiffFile(path) as tif:
            preview = next(
                (
                    series.asarray()
                    for series in reversed(tif.series)
                    if series.shape[-1:] == (3,)
                    and series.dtype == np.uint8
                ),
                None,
            )
            if preview is not None:
                rgb = preview
                photometric = 2
                orientation = 1
            else:
                page = tif.pages[0]
                rgb = page.asarray()
                photometric = page.photometric
                orientation_tag = page.tags.get("Orientation")
                orientation = (
                    orientation_tag.value if orientation_tag is not None else 1
                )
                if int(photometric) == 34892:
                    rgb = _develop_linear_dng(rgb, page)
    except (OSError, ValueError) as error:
        raise ValueError(
            f"rawpy and tifffile could not decode this DNG ({path.name}). "
            "The file may use an unsupported compression or be damaged."
        ) from error

    if rgb.ndim != 3 or rgb.shape[2] != 3:
        raise ValueError(
            f"Decoded DNG ({path.name}) is not an RGB image: shape {rgb.shape}"
        )
    if rgb.dtype not in (np.uint8, np.uint16, np.float32):
        raise TypeError(
            f"Decoded DNG ({path.name}) has unsupported pixel type: {rgb.dtype}"
        )

    if int(photometric) != 34892 and rgb.dtype == np.uint16 and rgb.max() <= 1023:
        rgb = np.rint(rgb.astype(np.float32) * (65535 / 1023)).astype(np.uint16)

    if int(photometric) != 34892:
        rgb = _apply_orientation(rgb, orientation)

    if bit_depth == 8 and rgb.dtype == np.uint16:
        rgb = np.rint(rgb / 257).astype(np.uint8)
    elif bit_depth == 16 and rgb.dtype == np.uint8:
        rgb = (rgb.astype(np.uint16) * 257)
    elif bit_depth == 16 and rgb.dtype == np.float32:
        rgb = np.rint(rgb * 65535).astype(np.uint16)
    elif bit_depth == 8 and rgb.dtype == np.float32:
        rgb = np.rint(rgb * 255).astype(np.uint8)

    return rgb


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
    except rawpy.LibRawFileUnsupportedError:
        return _load_tiff_dng(path, bit_depth)

    return rgb