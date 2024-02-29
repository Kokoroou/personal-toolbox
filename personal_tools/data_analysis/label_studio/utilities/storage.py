"""
Storage utilities
"""
from pathlib import Path


def standardize_path(path: str) -> str:
    """
    Standardize the storage path
    """
    # Get the directory path
    path = Path(path)
    if not path.is_dir():
        path = path.parent
    path = str(path)

    # Change the prefix
    if path.startswith("/data/local-files/?d=/label-studio/data/"):
        path = path[len("/data/local-files/?d=/label-studio/data/"):]
    elif path.startswith("/data/local-files/?d=label-studio/data/"):
        path = path[len("/data/local-files/?d=label-studio/data/"):]
    elif path.startswith("/data/upload/"):
        path = "media/" + path[len("/data/"):]

    return path
