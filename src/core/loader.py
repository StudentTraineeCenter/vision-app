import rawpy
import tifffile
import numpy as np
from PIL import Image


def load_raw_image(path: str) -> Image.Image:

    try:
        # 1. Klasické RAW soubory
        with rawpy.imread(path) as raw:
            rgb = raw.postprocess(
                use_camera_wb=True,
                output_bps=8
            )

        return Image.fromarray(rgb).convert("RGB")

    except rawpy.LibRawFileUnsupportedError:
        print("FALLBACK")

        
        with tifffile.TiffFile(path) as tif:
            page = tif.pages[0]
            image_data = page.asarray()

            def tag(code, default):
                t = page.tags.get(code)
                return np.atleast_1d(t.value) if t is not None else np.atleast_1d(default)

            white = float(tag(50717, 65535)[0])
            black = float(np.mean(tag(50714, 0)))
        
        if image_data.ndim != 3:
            raise ValueError(
                "Unsupported DNG image dimensions"
            )

        if image_data.shape[2] not in (3, 4):
            raise ValueError(
                "Unsupported number of color channels"
            )

        
        if image_data.shape[2] == 4:
            image_data = image_data[:, :, :3]

      
        if image_data.dtype == np.uint16:

            image_data = image_data.astype(np.float32)
            image_data = np.clip((image_data - black) / (white - black), 0.0, 1.0)

            # 1) srovnat barevný nádech (gray-world)
            means = image_data[::8, ::8].reshape(-1, 3).mean(axis=0)
            image_data = np.clip(image_data * (means.mean() / means), 0.0, 1.0)

            # 2) srovnat expozici (99,5. percentil = bílá)
            p = np.percentile(image_data[::8, ::8], 99.5)
            image_data = np.clip(image_data / max(p, 1e-6), 0.0, 1.0)

            # 3) gamma a převod na 8 bitů
            image_data = np.power(image_data, 1.0 / 2.2)
            image_data = (image_data * 255).round().astype(np.uint8)

        elif image_data.dtype != np.uint8:
            raise ValueError(
                "Unsupported DNG bit depth"
            )

       
        from PIL import ImageEnhance
        img = Image.fromarray(image_data).convert("RGB")
        img = ImageEnhance.Color(img).enhance(1.3)
        img = ImageEnhance.Contrast(img).enhance(1.1)
        return img
