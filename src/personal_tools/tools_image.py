"""
Set of tools for converting images to different formats.
"""
from io import BytesIO

from PIL import Image


class ImageConverter:
    """
    Convert images to different formats.
    """

    def __init__(self):
        """
        Constructor.
        """
        self.last_image = None

    def convert(self, image: Image.Image, img_format: str):
        """
        Convert image to different format.

        :param image: Image to convert
        :param img_format: Format to convert to.
            Supported formats: PNG, JPEG, BMP, GIF, TIFF, WebP, ICO
        :return: Converted image
        """
        self.last_image = image.convert("RGB")

        if img_format.lower() in ["png", "jpeg", "bmp", "gif", "tiff", "webp", "ico"]:
            img_format = img_format.upper()
        else:
            raise ValueError(f"Unsupported format: {img_format}")

        with BytesIO() as new_file:
            self.last_image.save(new_file, format=img_format)

            return new_file.getvalue()

    def get_last_image(self) -> Image.Image:
        """
        Get last image.

        :return: Last image
        """
        return self.last_image
