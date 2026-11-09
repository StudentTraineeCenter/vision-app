from PIL import Image
import struct
import zlib


def paeth_predictor(a, b, c):
    p = a + b - c

    pa = abs(p - a)
    pb = abs(p - b)
    pc = abs(p - c)

    if pa <= pb and pa <= pc:
        return a
    elif pb <= pc:
        return b

    return c


def apply_png_filter(row, previous_row, bpp, filter_type):
    result = bytearray(len(row))

    for i in range(len(row)):
        left = row[i - bpp] if i >= bpp else 0
        above = previous_row[i]
        upper_left = previous_row[i - bpp] if i >= bpp else 0

        if filter_type == 0:
            predictor = 0
        elif filter_type == 1:
            predictor = left
        elif filter_type == 2:
            predictor = above
        elif filter_type == 3:
            predictor = (left + above) // 2
        elif filter_type == 4:
            predictor = paeth_predictor(left, above, upper_left)
        else:
            raise ValueError("Invalid PNG filter")

        result[i] = (row[i] - predictor) & 255

    return bytes(result)


def filter_score(filtered_row):
    score = 0

    for value in filtered_row:
        signed_value = value if value < 128 else value - 256
        score += abs(signed_value)

    return score


def create_png_chunk(chunk_type, data):
    chunk = chunk_type + data
    crc = zlib.crc32(chunk) & 0xFFFFFFFF

    return (
        struct.pack(">I", len(data))
        + chunk
        + struct.pack(">I", crc)
    )


def export_png(
    image,
    output_path,
    compress_level=6,
    optimize=True,
    colors="256",
    color_mode="RGB"
):
    if not 0 <= compress_level <= 9:
        raise ValueError("Compress level must be between 0 and 9")

    if color_mode == "Grayscale":
        image = image.convert("L")
        png_color_type = 0

    elif color_mode == "RGBA":
        image = image.convert("RGBA")
        png_color_type = 6

    elif color_mode == "RGB":
        image = image.convert("RGB")
        png_color_type = 2

    elif color_mode == "Palette":
        image = image.convert("RGB")

        color_count = 256 if colors == "TrueColor" else int(colors)

        if not 1 <= color_count <= 256:
            raise ValueError("Colors must be between 1 and 256")

        image = image.quantize(
            colors=color_count,
            method=Image.Quantize.MEDIANCUT
        )

        png_color_type = 3

    else:
        raise ValueError("Invalid PNG color mode")

    width, height = image.size

    raw_data = image.tobytes()

    if png_color_type == 0 or png_color_type == 3:
        bpp = 1
    elif png_color_type == 2:
        bpp = 3
    else:
        bpp = 4

    row_length = width * bpp
    previous_row = bytes(row_length)

    filtered_data = bytearray()

    for y in range(height):
        start = y * row_length
        end = start + row_length

        row = raw_data[start:end]

        if optimize:
            best_filter = 0
            best_row = None
            best_score = float("inf")

            for filter_type in range(5):
                candidate = apply_png_filter(
                    row,
                    previous_row,
                    bpp,
                    filter_type
                )

                score = filter_score(candidate)

                if score < best_score:
                    best_score = score
                    best_filter = filter_type
                    best_row = candidate

            filtered_data.append(best_filter)
            filtered_data.extend(best_row)

        else:
            filtered_row = apply_png_filter(
                row,
                previous_row,
                bpp,
                0
            )

            filtered_data.append(0)
            filtered_data.extend(filtered_row)

        previous_row = row

    compressed_data = zlib.compress(
        bytes(filtered_data),
        compress_level
    )

    png_data = bytearray()

    png_data.extend(b"\x89PNG\r\n\x1a\n")

    ihdr = struct.pack(
        ">IIBBBBB",
        width,
        height,
        8,
        png_color_type,
        0,
        0,
        0
    )

    png_data.extend(create_png_chunk(b"IHDR", ihdr))

    if png_color_type == 3:
        palette = image.getpalette()[:768]
        palette_data = bytes(palette)

        png_data.extend(
            create_png_chunk(b"PLTE", palette_data)
        )

    png_data.extend(
        create_png_chunk(b"IDAT", compressed_data)
    )

    png_data.extend(
        create_png_chunk(b"IEND", b"")
    )

    with open(output_path, "wb") as file:
        file.write(png_data)

    return output_path
