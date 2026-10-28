# Vision - Project Documentation

## What this project does

Vision is a small Python image-conversion application. It takes a camera RAW
photo in `.dng` format, turns it into a normal RGB image, and saves that image
as JPEG, PNG, or TIFF.

The code is split into:

- **Core logic**: loading DNG files, saving output files, and coordinating a
  conversion.
- **User interface**: planned Flet UI files. They are currently empty
  placeholders.
- **Tests**: test files exist, but are currently empty in this checkout.

## How a conversion works

The complete conversion flow is:

```text
src/main.py
    -> core.worker.convert()
        -> core.loader.load_dng()
            -> rawpy / LibRaw
            -> NumPy RGB array
        -> selected exporter
            -> Pillow or tifffile
            -> JPEG, PNG, or TIFF file
        -> result with path, sizes, bit depth, and duration
```

In simple terms, `convert()` is the coordinator. It does not decode or
compress images itself. It checks the requested format, loads the DNG, calls
the correct exporter, and reports what happened.

## File-by-file explanation

### Application entry point

#### `src/main.py`

This is the current command-line test entry point. It calls `convert()` four
times:

- JPEG with quality and chroma-subsampling settings
- PNG with a compression level
- 8-bit TIFF with LZW compression
- 16-bit TIFF with Deflate compression

The `show()` helper prints the output path, original and new file sizes, and
conversion time. The `SOURCE` constant must point to a real local `.dng` file.

The file is described as temporary because the planned graphical UI has not
yet replaced it.

### Core image processing

#### `src/core/loader.py`

`load_dng()` is the only module that directly uses `rawpy`. Keeping RAW
decoding here gives the rest of the application one simple input type: an RGB
NumPy array.

It:

1. Converts the path to a `Path` object.
2. Checks that the requested bit depth is 8 or 16.
3. Checks that the file exists and has a `.dng` extension.
4. Uses the camera white balance while decoding with `rawpy`.
5. Returns an array shaped as `(height, width, 3)`.

8-bit output uses values from 0 to 255 and is suitable for JPEG and PNG.
16-bit output preserves more image detail and is intended for TIFF. The
`half_size` option can later be used to load a faster, smaller preview.

Invalid input raises clear errors such as `FileNotFoundError` or
`ValueError`. Unsupported DNG encodings are converted into a readable
application error.

#### `src/core/worker.py`

Despite its name, this module currently performs the conversion synchronously;
it does not create a background thread yet. Its main function is
`convert(src, fmt, out_dir=None, bit_depth=8, **options)`.

It:

1. Normalizes and validates the requested format.
2. Rejects 16-bit JPEG and PNG because only TIFF supports that output.
3. Selects an exporter from the `EXPORTERS` mapping.
4. Creates the destination directory when needed.
5. Builds a name such as `photo_converted.jpg` or
   `photo_converted_16bit.tif`.
6. Loads the DNG and passes the resulting array to the selected exporter.
7. Returns output path, bit depth, original size, new size, and elapsed time.

The `EXPORTERS` mapping is the connection between a format name, its file
extension, and its saving function. Adding a new output format would normally
mean adding an exporter and one entry to this mapping.

#### `src/core/exporter_jpeg.py`

`save_jpeg()` converts the NumPy array to a Pillow image and saves it as
JPEG. It supports:

- `quality`: visual quality/file-size balance
- `subsampling`: color detail versus smaller file size
- Pillow's `optimize=True`: creates optimized JPEG encoding tables

JPEG is lossy, so a smaller file can mean some image detail is discarded.

#### `src/core/exporter_png.py`

`save_png()` converts the array to a Pillow image and saves it as PNG.
`compress_level` controls how much time is spent making the lossless file
smaller. It changes file size and speed, not image quality.

#### `src/core/exporter_tiff.py`

`save_tiff()` supports 8-bit and 16-bit RGB arrays and these compression
names: `lzw`, `deflate`, `packbits`, and `none`.

- 8-bit arrays are saved with Pillow.
- 16-bit arrays are saved with `tifffile`, because Pillow is not used here
  for 16-bit RGB TIFF output.

The two compression mappings translate the application's friendly names into
the names expected by Pillow or `tifffile`. Unsupported NumPy data types are
rejected instead of being silently converted.

### User interface package

The following files are currently empty, so they do not yet communicate with
the core:

- `src/ui/app_layout.py`: intended main window layout
- `src/ui/components.py`: intended controls such as sliders, dropdowns, and
  switches
- `src/ui/preview.py`: intended image preview and export statistics
- `src/ui/__init__.py`: package marker

The planned design is for these UI modules to collect user settings and call
`core.worker.convert()`. The UI should not need to know how RAW decoding or
format-specific compression works.

### Tests

The test modules are currently empty:

- `tests/test_loader.py`
- `tests/test_exporters.py`
- `tests/__init__.py`

They are intended to cover DNG loading and output exporters, but no automated
checks are implemented in the current checkout.

## Dependencies and why they are used

The packages listed in `requirements.txt` have these roles:

- **Flet**: planned desktop user interface
- **rawpy**: reads and develops DNG/RAW files through LibRaw
- **NumPy**: stores decoded RGB pixel data
- **Pillow**: creates images and writes JPEG, PNG, and 8-bit TIFF
- **tifffile**: writes 16-bit TIFF images and supports TIFF compression

`setup_env.py` creates a `.venv`, installs the requirements, and verifies that
the main packages can be imported. Python 3.10 or newer is required.

## Running the current implementation

From the project root:

```powershell
python setup_env.py
.venv\Scripts\Activate.ps1
python -m src.main
```

Before running, update `SOURCE` in `src/main.py` to the path of a real DNG
file. The output files are written next to that source file unless another
output directory is passed to `convert()`.

## Design in one sentence

The project keeps file decoding, conversion coordination, and format-specific
saving separate so that the future UI can use one simple conversion function
without depending on the details of RAW processing or image compression.
