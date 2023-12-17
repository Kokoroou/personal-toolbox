"""
Set of tools for base64 encoding and decoding.
"""

import base64


class Base64Converter:
    """
    Base64 encoding and decoding.
    """

    def __init__(self):
        """
        Constructor.
        """
        self.last_base64 = None

    def encode(self, data: bytes):
        """
        Encode data using base64 encoding.
        """
        self.last_base64 = base64.b64encode(data)

        return self.last_base64

    def decode(self, data: str = None):
        """
        Decode data using base64 encoding.
        """
        if data is None:
            data = self.last_base64

        return base64.b64decode(data)
