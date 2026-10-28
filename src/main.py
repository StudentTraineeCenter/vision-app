"""Temporary test entry point (the UI will replace this later).

Run from the project ROOT folder (the one that contains src/):
    python -m src.main
"""
from core.worker import convert

# Change this to a real .dng file on your computer
SOURCE = r"C:\Users\mifim\Downloads\sample1.dng"


def show(result):
    print("Saved to:     ", result["output_path"])
    print(f"Original:      {result['original_size'] / 1e6:.1f} MB")
    print(f"New:           {result['new_size'] / 1e6:.1f} MB")
    print(f"Time:          {result['seconds']:.1f} s")
    print()


if __name__ == "__main__":
    print("--- JPEG ---")
    show(convert(SOURCE, "jpeg", quality=85, subsampling=2))

    print("--- PNG ---")
    show(convert(SOURCE, "png", compress_level=6))

    print("--- TIFF ---")
    show(convert(SOURCE, "tiff", compression="lzw"))

    print("--- TIFF 16-bit ---")
    show(convert(SOURCE, "tiff", bit_depth=16, compression="deflate"))
