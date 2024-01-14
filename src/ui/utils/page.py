"""
Page class to define page structure
"""
import streamlit as st


class Page:
    """
    Page class to define page structure
    """
    def __init__(self, page_config: dict = None):
        """
        Initialize Page class
        """
        print("Create page\n")
        st.set_page_config(**(page_config or {}))

        self.sidebar = st.sidebar.container()
        self.header = st.container()
        self.main = st.container()

        self.section_input = self.main.container()
        self.section_middle = self.main.container()
        self.section_output = self.main.container()
