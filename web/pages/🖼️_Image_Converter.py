"""
Page for demo Image Converter
"""

# pylint: disable=invalid-name,non-ascii-file-name
# Note: Streamlit page names is created from filename
import shutil
from pathlib import Path

import PIL
import streamlit as st
from PIL import Image

from personal_tools.file_tools.conversion.convert_image import ImageConverter
from ..utils.render import BaseRenderer

st.set_page_config(
    page_title="Image Converter",
    page_icon="🖼️",
    layout="wide",
)

tool = ImageConverter()


class ImageRenderer(BaseRenderer):
    """
    Renderer for Image Converter page
    """
    # All formats fully supported by Pillow
    supported_formats = ["BLP", "BMP", "DDS", "DIB", "EPS", "GIF", "ICNS", "ICO", "IM",
                         "JPEG", "MSP", "PCX", "PNG", "PPM", "SGI", "SPIDER",
                         "TGA", "TIFF", "WEBP", "XBM"]
    extensions_additional = ["JPG"]
    extensions_map = {
        "JPG": "JPEG",
    }
    supported_formats = sorted(supported_formats + extensions_additional)

    def __init__(self, main_func: callable):
        """
        Initialize ImageRenderer class
        """
        super().__init__()

        self.main_func = main_func

    def render_config(self, placeholder):
        """
        Render the config section of page

        :param placeholder: Placeholder for config section
        """
        placeholder.title("Config")

        # Add format selection
        self.config["raw_format"] = placeholder.selectbox("Convert to", self.supported_formats,
                                                          index=self.supported_formats.index("JPG"))
        if self.config["raw_format"].upper() in self.extensions_map:
            self.config["format"] = self.extensions_map[self.config["raw_format"].upper()]
        else:
            self.config["format"] = self.config["raw_format"]
        self.config["format"] = self.config["format"].lower()

        # Add visualization
        self.config["vis"] = placeholder.checkbox("Visualize image", value=False)
        self.config["vis_columns"] = 3
        if self.config["vis"]:
            self.config["vis_columns"] = placeholder.slider("Columns", min_value=1, max_value=10, value=3)

    def render_input(self, placeholder):
        """
        Render the input section of page

        :param placeholder: Placeholder for input section
        """
        self.cache["files"] = placeholder.file_uploader("Upload image",
                                                        accept_multiple_files=True)

        return self.cache["files"]

    def render_processing(self, placeholder):
        """
        Render the processing section of page

        :param placeholder: Placeholder for processing section
        """
        files = self.cache.get("files")

        if files:
            converted_images = []

            convert_button = placeholder.button("Convert")

            # Convert images
            if convert_button:
                progress_bar = placeholder.progress(0, text="Converting images...")
                for i, file in enumerate(files):
                    converted_image = None

                    try:
                        image = Image.open(file)

                        converted_image = self.main_func(image, self.config["format"])
                    except PIL.UnidentifiedImageError:
                        placeholder.warning(f"Cannot read image: {file.name}")

                    converted_images.append(converted_image)

                    progress_bar.progress((i + 1) / len(files), f"Converting {file.name}...")

                progress_bar.empty()

                # Add images to cache
                if converted_images:
                    self.cache["converted_images"] = converted_images

    def render_output(self, placeholder):
        """
        Render the output section of page

        :param placeholder: Placeholder for output section
        """
        if self.config["vis"] and \
                any(image is not None for image in self.cache["converted_images"]):
            vis_expander = placeholder.expander("Visualize image",
                                                expanded=False)

            columns = vis_expander.columns(self.config["vis_columns"])

            for i, image in enumerate(self.cache["converted_images"]):
                if not image:
                    continue

                columns[i % self.config["vis_columns"]].image(image)

    def create_download_data(self):
        converted_count = sum(image is not None for image in self.cache["converted_images"])

        if converted_count >= 1:
            shutil.rmtree(self.temp_dir, ignore_errors=True)
            self.temp_dir.mkdir(exist_ok=True)

            # Create temporary directory for images
            temp_image_dir = self.temp_dir / "images"
            temp_image_dir.mkdir(exist_ok=True)

            filenames = [Path(file.name).stem for file in self.cache["files"]]
            file_format = self.config["raw_format"].lower()

            # Save images to temporary directory
            for index, image in enumerate(self.cache["converted_images"]):
                if not image:
                    continue

                image_filepath = temp_image_dir / f"{filenames[index]}.{file_format}"

                write_index = 1
                while image_filepath.exists():
                    image_filename = f"{filenames[index]} ({write_index}).{file_format}"
                    image_filepath = temp_image_dir / image_filename
                    write_index += 1

                with open(image_filepath, "wb") as image_file:
                    image_file.write(image)

            # Create zip file
            zip_path = self.temp_dir / "images.zip"
            shutil.make_archive(str(zip_path).rstrip(".zip"), "zip", temp_image_dir)

            with open(zip_path, "rb") as zip_file:
                self.cache["output"] = zip_file.read()

            shutil.rmtree(self.temp_dir)
        else:
            self.cache["output"] = None


renderer = ImageRenderer(main_func=tool.convert)


def app():
    """
    Create app for demo Image Converter
    """
    sidebar = st.sidebar.container()
    header = st.container()
    main = st.container()

    section_input = main.container()
    section_middle = main.container()
    section_output = main.container()

    renderer.render_header(header,
                           title="Image Converter",
                           caption="Convert images to different formats. "
                                   "Support from common formats like PNG, JPG, BMP to "
                                   "more rare formats like BLP, DDS, etc.")
    renderer.render_config(sidebar)
    renderer.render_input(section_input)

    # if not st.session_state.get("files") or \
    #         renderer.cache.get("files") != st.session_state.get("files"):
    #     st.session_state["files"] = renderer.cache.get("files")
    if renderer.cache.get("files"):
        # print(len(renderer.cache.get("files", [])))
        renderer.render_processing(section_middle)

    print(len(renderer.cache.get("converted_images", [])))
    if renderer.cache.get("converted_images"):
        renderer.render_output(section_output)
        renderer.create_download_data()
        renderer.render_download_button(section_output, "images.zip")


if __name__ == "__main__":
    app()
