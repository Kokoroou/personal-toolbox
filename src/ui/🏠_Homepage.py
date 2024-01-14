"""
Homepage for Streamlit app
"""
# pylint: disable=invalid-name,non-ascii-file-name
# Explain: Streamlit page names is created from filename

import streamlit as st

st.set_page_config(
    page_title="Homepage",
    page_icon="🏠",
    layout="wide",
)


def app():
    """
    Create main Streamlit app
    """
    st.title("Hello, world!")


if __name__ == "__main__":
    app()
