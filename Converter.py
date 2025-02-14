import hashlib
import io
import os

import ffmpeg
import pytesseract
from PIL import Image

import SetupLogging
import globals

LOG = SetupLogging.setup_logger('converter', 'converter.log')


def ImgPrep(image_data):
    """
    Prepares an image for display by compressing it and returning the compressed image data, MIME type, height,
    and width.
    :param image_data:
    :return:
    """
    if not os.path.exists(globals.CACHE_FOLDER):
        os.makedirs(globals.CACHE_FOLDER)
    
    image_hash = hashlib.md5(image_data, usedforsecurity=False).hexdigest()
    
    # let's check if the image is already in the cache
    cache_path = os.path.join(globals.CACHE_FOLDER, image_hash)
    if os.path.exists(cache_path):
        if image_data.startswith(b"GIF"):
            with open(cache_path, "rb") as f:
                with open(cache_path + "_size", "rt") as f_size:
                    height, width = f_size.read().split(",")
                    return f.read(), "image/gif", int(height), int(width)
        else:
            with open(cache_path, "rb") as f:
                with open(cache_path + "_size", "rt") as f_size:
                    height, width = f_size.read().split(",")
                    return f.read(), "image/jpeg", int(height), int(width)
    
    # Open the image data with PIL
    image = Image.open(io.BytesIO(image_data))
    
    with open(cache_path, "wb") as f:
        f.write(image_data)
    with open(cache_path + "_size", "wt") as f:
        f.write(f"{image.height},{image.width}")
    
    if image_data.startswith(b"GIF"):
        pass
    else:
        ocr = pytesseract.image_to_string(image)
    
    if image_data.startswith(b"GIF"):
        return image_data, "image/gif", image.height, image.width
    else:
        # noinspection PyUnboundLocalVariable
        return image_data, "image/jpeg", image.height, image.width, ocr


def compress_image(image_data, image_url):
    """
    Compresses an image based on its file type and returns the compressed image data.

    Args:
        image_data (bytes): The binary data of the image to be compressed.
        image_url (str): The URL of the image, used to determine the file type.

    Returns:
        bytes: The binary data of the compressed image.
    """
    # Open the image file
    if image_url.endswith(".gif"):
        image = (
                "image_cache/"
                + hashlib.md5(image_data, usedforsecurity=False).hexdigest()
                + ".gif"
        )
    else:
        image = Image.open(io.BytesIO(image_data))
    
    # Compress the image based on its file type
    output = io.BytesIO()
    if image_url.endswith(".jpg") or image_url.endswith(".jpeg"):
        image.save(output, format="JPEG", quality=80)  # Adjust the quality as needed
    elif image_url.endswith(".png"):
        width, height = image.size
        len(image_data)
        LOG.info(
            "Image size before compression: {}x{} ({} bytes)".format(
                width, height, len(image_data)
                )
            )
        new_size = (width // 2, height // 2)
        # should fix cannot write mode RGBA as JPEG at the cost of bluesky not supporting files over 1mb in size (grr)
        image.resize(new_size, Image.Resampling.LANCZOS)
        image.save(output, format="PNG", optimize=True, quality=20)
        # (i wish bsky would support blobs more than 1mb but whatever)
    elif image_url.endswith(".gif"):
        # Convert the GIF to an MP4 using ffmpeg
        LOG.info("Converting GIF to MP4")
        (
            ffmpeg.input(image)
            .output(output, format="mp4", vcodec="libx264", pix_fmt="yuv420p")
            .run(
                quiet=True, overwrite_output=True
                )  # overwrite_output=True is needed to avoid a prompt
            # when the file already exists (e.g. when testing)
        )
        # probe = ffmpeg.probe(output)
        # width = probe['streams'][0]['width']
        # height = probe['streams'][0]['height']
    elif image_url.endswith(".bmp"):
        image.save(output, format="BMP")  # BMPs are not compressible
    maxsize = 976560
    # Check if the image size is greater than the maximum size
    if image_url.endswith(".gif"):
        compressed_image_data = output
    else:
        compressed_image_data = output.getvalue()
    return compressed_image_data
