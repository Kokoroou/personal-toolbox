"""
Render class
"""

from pathlib import Path

import magic


class BaseRenderer:
    """
    Base class for renderers
    """

    def __init__(self):
        """
        Initialize BaseRenderer class
        """
        self.config = {}
        self.cache = {}
        self.temp_dir = Path(__file__).parent.resolve() / "temp"

    @staticmethod
    def render_header(placeholder, title: str, caption: str = None):
        """
        Render header

        :param placeholder: Placeholder for header
        :param title: Title for header
        :param caption: Caption for header
        """
        placeholder.title(title)
        if caption:
            placeholder.caption(caption)

    def create_download_data(self):
        """
        Create file byte data to cache["output"] for downloading
        """
        raise NotImplementedError("This method must be implemented")

    def render_download_button(self, placeholder, file_name: str):
        """
        Render download button in the output section to download compressed output data.

        :param placeholder: Placeholder for download button
        :param file_name: Name of file for downloading
        """
        download_data = self.cache.get("output")

        if download_data:
            if not isinstance(download_data, bytes):
                raise AttributeError('cache["output"] must be bytes')

            # Add download button
            placeholder.download_button(
                label="Download",
                data=download_data,
                file_name=file_name,
                mime=magic.from_buffer(download_data, mime=True),
                key="download_button",
            )
