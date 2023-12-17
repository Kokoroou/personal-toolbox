"""
Page for demo Image Converter
"""
# pylint: disable=invalid-name,non-ascii-file-name
# Note: Streamlit page names is created from filename

from pathlib import Path

import streamlit as st
from PIL import Image

from personal_tools.tools_image import ImageConverter

st.set_page_config(
    page_title="Image Converter",
    page_icon="🖼️",
    layout="wide",
)


def app():
    """
    Create app for demo Image Converter
    """
    st.title("Image Converter")
    file = st.file_uploader("Upload file",
                            type=["png", "jpg", "jpeg", "bmp", "gif", "tiff", "webp", "ico"])

    tool = ImageConverter()

    if file:
        # Show original image
        st.image(file, caption=file.name)

        # Choose format to convert to
        supported_formats = ["PNG", "JPEG", "BMP", "GIF", "TIFF", "WebP", "ICO"]
        img_format = st.selectbox("Convert to", supported_formats)

        if img_format:
            convert_button = st.button("Convert")

            if convert_button:
                # Convert image
                image = Image.open(file)
                new_image = tool.convert(image,
                                         img_format.lower())

                # Show converted image
                new_image_name = f"{Path(file.name).stem}.{img_format.lower()}"
                st.image(new_image, caption=new_image_name)

                # Download converted image
                st.download_button(
                    label="Download",
                    data=new_image,
                    file_name=new_image_name,
                    mime=f"image/{img_format.lower()}",
                    key="image_download_button"
                )


if __name__ == "__main__":
    app()
