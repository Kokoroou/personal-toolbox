"""
Page for demo Base64 Converter
"""
# pylint: disable=invalid-name,non-ascii-file-name
# Note: Streamlit page names is created from filename

from binascii import Error as BinasciiError
from pathlib import Path

import streamlit as st

from personal_tools.file_tools.conversion.convert_base64 import Base64Converter
from ..utils.page import Page

st.set_page_config(
    page_title="Base64 Converter",
    page_icon="🔢",
    layout="wide",
)

tool = Base64Converter()
page = Page()


def app():
    """
    Create app for demo Base64 Converter
    """
    page.render_header(
        title="Base64 Converter",
        caption="Convert files to Base64 and vice versa"
    )
    page.render_sidebar(title="Config")

    # Create main content
    object_type = page.sidebar.radio(
        label="Convert from",
        options=["File", "Text"],
        index=0
    )

    if object_type == "File":
        decode_options = ["Raw", "ZIP", "TXT", "PDF", "PNG", "JPG", "JSON"]

        # Add file config
        group_all = page.sidebar.checkbox("Group all files",
                                          value=True,
                                          help="Group all files into one zip file")
        decode_type = page.sidebar.selectbox(
            label="Decode type",
            options=decode_options,
            index=decode_options.index("Raw")
        )

        # Add file uploader
        uploaded_files = page.main.file_uploader("Upload file",
                                                 accept_multiple_files=True)

        if uploaded_files:
            # Show main buttons
            col_1, col_2 = page.main.columns(2)
            button_1 = col_1.button("Encode")
            button_2 = col_2.button("Decode")

            if button_1:
                # Encode file
                base64_data = tool.encode(raw_data)

                # Create new filename for saving
                new_filename = Path(file.name).stem + "_base64.txt"

                # Show base64 text
                page.main.text_area(label=new_filename,
                                    height=200,
                                    value=base64_data.decode("utf-8"))

                # Create download button
                page.main.download_button(
                    label="Download",
                    data=base64_data,
                    file_name=new_filename,
                    mime="text/plain",
                    key="base64_download_button"
                )

            elif button_2:
                base64_data = file.getvalue()

                try:
                    # Only decode if data is valid
                    raw_data = tool.decode(base64_data)
                except BinasciiError:
                    page.main.error("File is not valid for Base64 decoding")
                    return

                # Create new filename for saving
                new_filename = Path(file.name).stem.strip("_base64")

                # Add file extension to filename
                if decode_type in decode_options and decode_type != "Raw":
                    new_filename = new_filename + "." + decode_type.lower()

                # Create download button
                page.main.download_button(
                    label="Download",
                    data=raw_data,
                    file_name=new_filename,
                    key="raw_download_button"
                )


if __name__ == "__main__":
    app()
