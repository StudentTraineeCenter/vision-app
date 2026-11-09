from PIL import Image


def export_tiff(
    image,
    output_path,
    compression="LZW"
):
    compression_map = {
        "LZW": "tiff_lzw",
        "Deflate": "tiff_adobe_deflate",
        "Packbits": "packbits",
        "None": None
    }

    if compression not in compression_map:
        raise ValueError("Invalid TIFF compression")

    image.save(
        output_path,
        format="TIFF",
        compression=compression_map[compression]
    )

    return output_path
