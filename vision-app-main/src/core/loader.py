
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

        
        with tifffile.TiffFile(path) as tif:
            image_data = tif.pages[0].asarray()

        
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

            if image_data.max() <= 1023:
                white_level = 1023.0
            else:
                white_level = 65535.0

          
            image_data = np.clip(
                image_data / white_level,
                0.0,
                1.0
            )

          
            image_data = np.power(
                image_data,
                1.0 / 2.2
            )

         
            image_data = (
                image_data * 255
            ).round().astype(np.uint8)

        elif image_data.dtype != np.uint8:
            raise ValueError(
                "Unsupported DNG bit depth"
            )

       
        return Image.fromarray(
            image_data
        ).convert("RGB")
