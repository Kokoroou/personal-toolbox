"""
Utilities for encoding and decoding data
"""
import pyotp


def get_2fa_code(key):
    """
    Get 2-Factor Authentication code from key

    :param key: 2-Factor Authentication key
    :return: 2-Factor Authentication code
    """
    totp = pyotp.TOTP(str(key).strip().replace(" ", "")[:32])
    code = totp.now()

    return code
