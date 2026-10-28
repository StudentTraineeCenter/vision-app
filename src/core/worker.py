"""The 'boss' of the core: runs the whole conversion from start to finish.

Later the UI will call only convert() and does not need to know anything else.
"""
import time
from pathlib import Path

from .exporter_jpeg import save_jpeg
from .exporter_png import save_png
from .exporter_tiff import save_tiff
from .loader import load_dng

# format name -> (file extension, function that saves it)
EXPORTERS = {
    "jpeg": (".jpg", save_jpeg),
    "png": (".png", save_png),
    "tiff": (".tif", save_tiff),
}


def convert(src, fmt, out_dir=None, bit_depth=8, **options):
    """Convert one .dng file to JPEG, PNG or TIFF.

    src:       path to the .dng file
    fmt:       "jpeg", "png" or "tiff"
    out_dir:   folder for the result (default: same folder as the .dng)
    bit_depth: 8 or 16. 16-bit is only possible with "tiff".
    options:   settings passed to the exporter, for example
               quality=85, subsampling=2        (jpeg)
               compress_level=9                 (png)
               compression="lzw"                (tiff)

    Returns a dictionary with the output path, file sizes and time taken.
    """
    fmt = fmt.lower()
    if fmt not in EXPORTERS:
        raise ValueError(f"Unknown format '{fmt}'. Use: {', '.join(EXPORTERS)}")
    if bit_depth == 16 and fmt != "tiff":
        raise ValueError("16-bit output is only supported for TIFF.")

    extension, save_function = EXPORTERS[fmt]

    src = Path(src)
    out_dir = Path(out_dir) if out_dir else src.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    # photo.dng -> photo_converted.jpg (16-bit: photo_converted_16bit.tif)
    suffix = "_16bit" if bit_depth == 16 else ""
    out_path = out_dir / f"{src.stem}_converted{suffix}{extension}"

    start = time.perf_counter()
    rgb = load_dng(src, bit_depth=bit_depth)  # step 1: open the RAW
    save_function(rgb, out_path, **options)    # step 2: save in chosen format
    seconds = time.perf_counter() - start

    return {
        "output_path": out_path,
        "bit_depth": bit_depth,
        "original_size": src.stat().st_size,
        "new_size": out_path.stat().st_size,
        "seconds": seconds,
    }