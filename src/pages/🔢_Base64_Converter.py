"""
Page for demo Base64 Converter
"""
# pylint: disable=invalid-name,non-ascii-file-name
# Note: Streamlit page names is created from filename

from binascii import Error as BinasciiError
from pathlib import Path

import streamlit as st

from personal_tools.tools_base64 import Base64Converter

st.set_page_config(
    page_title="Base64 Converter",
    page_icon="🔢",
    layout="wide",
)


def app():
    """
    Create app for demo Base64 Converter
    """
    st.title("Base64 Converter")
    file = st.file_uploader("Upload file")

    tool = Base64Converter()

    if file:
        col_1, col_2 = st.columns(2)

        # Show main buttons
        with col_1:
            button_1 = st.button("Encode")
        with col_2:
            button_2 = st.button("Decode")

        if button_1:
            # Encode file
            raw_data = file.getvalue()
            base64_data = tool.encode(raw_data)

            # Create new filename for saving
            new_filename = Path(file.name).stem + "_base64.txt"

            # Show base64 text
            st.text_area(label=new_filename,
                         height=200,
                         value=base64_data.decode("utf-8"))

            # Create download button
            st.download_button(
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
                st.error("File is not valid for Base64 decoding")
                return

            # Create new filename for saving
            new_filename = Path(file.name).stem.strip("_base64")

            # Show raw text
            st.text_area(label=new_filename,
                         height=200,
                         value=raw_data.decode("utf-8"))

            # Create download button
            download_options = ["Raw", "ZIP", "TXT", "PDF", "PNG", "JPG", "JSON"]
            download_type = st.selectbox(
                label="Download type",
                options=download_options,
                index=download_options.index("Raw")
            )

            # Add file extension to filename
            if download_type in download_options and download_type != "Raw":
                new_filename = new_filename + "." + download_type.lower()

            # Create download button
            st.download_button(
                label="Download",
                data=raw_data,
                file_name=new_filename,
                key="raw_download_button"
            )


if __name__ == "__main__":
    app()
