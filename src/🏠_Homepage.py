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
