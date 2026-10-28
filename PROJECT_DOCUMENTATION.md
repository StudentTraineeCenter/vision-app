# Vision - Project Documentation

## What this project does

Vision converts `.dng` camera photos into ordinary RGB images:

- JPEG for small, widely compatible files
- PNG for lossless 8-bit images
- TIFF for lossless 8-bit or 16-bit images

The project separates three responsibilities:

1. **Loading**: open a DNG and produce an RGB NumPy array.
2. **Coordination**: validate the request, choose an exporter, and report
   conversion statistics.
3. **Exporting**: write the RGB array in the selected file format.

The planned Flet interface and automated tests are not implemented yet. The
current runnable entry point is `src/main.py`.

## Complete conversion flow

```text
src/main.py
    |
    v
core.worker.convert()
    |
    +--> core.loader.load_dng()
    |       |
    |       +--> rawpy / LibRaw for normal RAW-compatible DNGs
    |       |
    |       +--> tifffile + imagecodecs for compatible DNG/TIFF data
    |       |
    |       +--> NumPy RGB array, uint8 or uint16
    |
    +--> exporter_jpeg.save_jpeg()
    +--> exporter_png.save_png()
    +--> exporter_tiff.save_tiff()
            |
            v
        JPEG, PNG, or TIFF file
```

In simple terms, `convert()` is the manager. It does not understand RAW
pixels or compression details itself. It asks the loader for an RGB array,
passes that array to the selected exporter, and returns the output path,
file sizes, bit depth, and elapsed time.

## How DNG loading works

The main loader is [src/core/loader.py](./src/core/loader.py). Its public
function is `load_dng(path, bit_depth=8, half_size=False)`.

It performs these checks:

1. Converts the input to a `pathlib.Path`.
2. Requires bit depth `8` or `16`.
3. Requires an existing file with the `.dng` extension.
4. Tries the normal RAW decoder first.
5. Uses the TIFF fallback when LibRaw reports that the DNG encoding is not
   supported.
6. Returns an RGB array shaped `(height, width, 3)`.

The returned array is:

- `uint8` with values from `0` to `255` for 8-bit output
- `uint16` with values from `0` to `65535` for 16-bit output

### Normal DNG path: rawpy and LibRaw

`rawpy` is the Python interface to LibRaw, a native RAW-image processing
library. For ordinary camera DNGs, `rawpy` opens the file and calls
`raw.postprocess()`. The project requests the camera's saved white balance and
the requested output bit depth.

This is the preferred path because LibRaw understands camera RAW metadata and
can perform the normal RAW development process.

### Fallback path: tifffile and embedded images

Some newer Samsung DNGs are not ordinary Bayer RAW files from LibRaw's point
of view. They can use JPEG XL compression and can contain linear RGB data
inside a TIFF/DNG container. When LibRaw cannot unpack such a file, the loader
uses `tifffile`.

The loader examines the TIFF series in the DNG. If it finds a 3-channel
`uint8` RGB series, it treats that series as the phone's embedded rendered
preview and uses it directly.

This is the important color fix. The phone's rendered preview already has the
correct:

- camera color profile
- white balance
- exposure
- tone curve and gamma
- contrast
- saturation
- orientation

Trying to recreate all of that from the linear sensor data with arbitrary
channel multipliers caused the earlier green, purple, sepia, flat, and
overexposed results. Using the phone's own rendered image is both more
reliable and closer to the original photo.

The embedded preview is already display-oriented, so the loader does not
apply the DNG orientation tag a second time. If no rendered preview exists,
the fallback reads the first RGB TIFF image and applies the available
linear-DNG processing.

### 10-bit data in a 16-bit container

Some phone DNGs declare 16-bit samples but actually use only 10-bit values,
approximately `0` to `1023`. If those values were sent directly to a normal
16-bit image, the result would be almost black because the values would occupy
only a small part of the `0` to `65535` range.

The fallback detects this situation and scales the values to the full output
range before exporting.

### 16-bit output

When a rendered 8-bit preview is the available source, the loader expands each
8-bit value to 16-bit using the equivalent full-range mapping. This makes the
8-bit and 16-bit exports look the same:

```text
8-bit 255 -> 16-bit 65535
8-bit 128 -> approximately 16-bit 32896
```

This improves compatibility with 16-bit TIFF workflows, but it cannot create
raw detail that was not present in the embedded 8-bit preview.

## File-by-file explanation

### `src/main.py`

This is the temporary command-line entry point. It defines `SOURCE`, calls
`convert()` four times, and prints the result:

1. JPEG with quality `85` and subsampling `2`
2. PNG with compression level `6`
3. 8-bit TIFF with LZW compression
4. 16-bit TIFF with Deflate compression

The output is written beside the source DNG unless `convert()` receives a
different output directory. The future UI is expected to replace this file.

### `src/core/worker.py`

This module coordinates one complete conversion. Its main function is:

```python
convert(src, fmt, out_dir=None, bit_depth=8, **options)
```

It:

1. Normalizes the format name to lowercase.
2. Rejects unknown formats.
3. Rejects 16-bit JPEG and PNG because this project supports 16-bit output
   only for TIFF.
4. Creates the destination directory.
5. Builds the destination name, for example
   `photo_converted.jpg` or `photo_converted_16bit.tif`.
6. Calls `load_dng()`.
7. Calls the selected exporter with the supplied settings.
8. Returns output path, bit depth, original size, new size, and duration.

`EXPORTERS` connects a format name with its extension and saving function.
Adding another format normally means adding an exporter module and one entry
to this mapping.

### `src/core/exporter_jpeg.py`

`save_jpeg()` converts the NumPy array to a Pillow image and writes JPEG.

Supported settings:

- `quality`: JPEG quality and approximate size/detail trade-off
- `subsampling`: chroma detail; `0` keeps the most color detail, `2` is
  smaller and commonly used
- `optimize=True`: lets Pillow build more efficient JPEG tables

JPEG is lossy, so it is usually the smallest option but can discard detail.
The exporter opens the destination as a binary stream before passing it to
Pillow. This avoids Windows path-opening problems while preserving the
settings.

### `src/core/exporter_png.py`

`save_png()` converts the NumPy array to a Pillow image and writes PNG.

`compress_level` ranges from `0` to `9`. PNG compression is lossless, so this
setting changes encoding time and file size, not pixel quality. The exporter
also passes an explicitly opened binary stream to Pillow for reliable Windows
file handling.

### `src/core/exporter_tiff.py`

`save_tiff()` writes 8-bit and 16-bit RGB TIFF files.

- 8-bit arrays are written through Pillow.
- 16-bit arrays are written through `tifffile`.
- Supported friendly compression names are `lzw`, `deflate`, `packbits`,
  and `none`.

The module translates the project's friendly names into the names expected by
Pillow or tifffile. It rejects unsupported array data types instead of
silently changing them.

### `src/ui/`

These files are placeholders for the future Flet interface:

- `app_layout.py`: main application layout
- `components.py`: controls such as file pickers, dropdowns, and settings
- `preview.py`: image preview and conversion statistics
- `__init__.py`: package marker

The intended UI will collect a source DNG, output format, bit depth, and
compression settings, then call `core.worker.convert()`. It should not need
to know how RAW decoding or TIFF compression works.

### `tests/`

The current test files are placeholders:

- `tests/test_loader.py`
- `tests/test_exporters.py`
- `tests/__init__.py`

They are intended to cover DNG loading, fallback behavior, and output
exporters, but no automated tests are implemented in this checkout.

### `setup_env.py`

This script creates a local `.venv`, installs `requirements.txt`, and checks
that the main packages can be imported. It requires Python 3.10 or newer.

The environment is kept inside the project so project dependencies do not
have to be installed globally.

## Libraries and why each one is needed

The dependencies are listed in [requirements.txt](./requirements.txt).

### Flet

Flet is the planned desktop user-interface framework. It will provide the
file picker, controls, preview, progress/status area, and export buttons.
The current command-line entry point does not use it yet because the UI files
are still placeholders.

### rawpy

`rawpy` provides Python access to LibRaw. It opens and develops standard
camera RAW files, including many DNG files, and applies camera metadata such
as white balance during `postprocess()`.

It is the first decoder used because it is designed specifically for RAW
photography rather than general TIFF reading.

### LibRaw

LibRaw is the native processing engine used underneath `rawpy`. It is not
listed separately in `requirements.txt` because it is installed as part of
the `rawpy` package.

LibRaw handles RAW sensor data, camera metadata, white balance, and standard
RAW development. Some newer DNG variants are outside the installed LibRaw
support, which is why the project needs the TIFF fallback.

### NumPy

NumPy stores the decoded pixels as arrays. It provides:

- the `(height, width, 3)` RGB representation
- `uint8` and `uint16` pixel types
- scaling of 10-bit values
- clipping and conversion between bit depths
- efficient processing of millions of pixels

The loader and exporters use NumPy as the common format connecting all parts
of the application.

### Pillow

Pillow is the Python Imaging Library used to create and save:

- JPEG
- PNG
- 8-bit TIFF

It receives the already-decoded RGB NumPy array from the loader. Pillow is
not responsible for interpreting the DNG RAW data in this project.

### tifffile

`tifffile` reads TIFF structures and image series inside compatible DNG files.
It is needed because DNG is based on the TIFF/EP container format, and some
newer phone DNGs can be read as TIFF RGB data even when LibRaw cannot develop
them.

It also writes the project's 16-bit TIFF output, where it preserves the
`uint16` RGB array more directly than the Pillow path.

### imagecodecs

`imagecodecs` is a collection of compiled image compression/decompression
codecs. `tifffile` understands TIFF tags and file structure, but it delegates
many compressed pixel formats to codec implementations.

The newer Samsung DNGs use JPEG XL compression, identified inside the TIFF/DNG
metadata by a JPEG XL compression code. `tifffile` can recognize the DNG and
the compression tag, but without `imagecodecs` it cannot decode the compressed
pixel bytes. The result is an error such as “imagecodecs is required” or an
unsupported-compression failure.

Therefore:

- `tifffile` provides the TIFF/DNG reader and writer.
- `imagecodecs` provides the native JPEG XL and other codec implementations
  that `tifffile` calls.
- Both are required for the newer compressed DNG fallback.

`imagecodecs` is not a color-correction library. It only makes the compressed
pixel data readable. The correct colors come from the embedded rendered
preview, or from LibRaw's RAW development on the normal path.

## Installation and running

From the project root:

```powershell
python setup_env.py
.venv\Scripts\Activate.ps1
python -m src.main
```

Before running, set `SOURCE` in `src/main.py` to an existing DNG path. On
Windows, use a raw string or escaped backslashes:

```python
SOURCE = r"C:\Users\mifim\Downloads\Fotky\20261015_133731.dng"
```

The setup script installs all dependencies into `.venv`. It does not modify
the global Python installation.

## Output choices

| Format | Bit depth | Lossless | Main use |
|---|---:|---:|---|
| JPEG | 8-bit | No | Small files and sharing |
| PNG | 8-bit | Yes | Exact 8-bit pixels |
| TIFF | 8-bit | Yes | Editing and archival |
| TIFF | 16-bit | Yes | Higher-bit-depth editing workflows |

For newer phone DNGs using an embedded 8-bit preview, 16-bit TIFF preserves
the same appearance but does not contain additional sensor detail beyond that
preview.

## Design summary

The project keeps decoding, conversion coordination, and file-format writing
separate. `loader.py` solves the difficult DNG compatibility and color-source
problem. `worker.py` provides one stable conversion entry point. The exporter
modules keep format-specific settings isolated. This structure lets a future
Flet UI use the same conversion code without needing to understand RAW
formats, JPEG XL, white balance, or compression internals.
