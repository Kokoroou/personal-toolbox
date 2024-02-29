"""
Utility to sort lines in file alphabetically
"""
import argparse
from pathlib import Path
from typing import Union


def sort_lines(file_path: Union[str, Path]) -> None:
    """
    Sort lines in file alphabetically

    :param file_path: Path to the file that needs to be sorted
    """
    # Add new line to the end of file if not exists
    with open(file_path, "a", encoding="utf-8") as file:
        file.write("\n")

    # Read file
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()

    # Remove empty lines
    lines = [line for line in lines if line.strip()]

    # Sort lines
    lines.sort()

    # Write to file
    with open(file_path, "w", encoding="utf-8") as file:
        file.writelines(lines)


if __name__ == '__main__':
    # Create parser for command line arguments
    parser = argparse.ArgumentParser(
        description="Sort lines in file alphabetically. "
                    "Can be used for 'requirements.txt' files or '.ignore' files")
    parser.add_argument('--path', '-p', type=str, help="Path to the requirements file")

    # Parse command line arguments
    args = parser.parse_args()

    # Sort lines in file
    sort_lines(args.path)
