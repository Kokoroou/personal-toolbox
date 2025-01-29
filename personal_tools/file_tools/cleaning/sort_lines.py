"""
Utility to sort lines in file alphabetically
"""

import argparse
from pathlib import Path
from typing import Union


def sort_file_lines(file_path: Union[str, Path]):
    """Sắp xếp lại các dòng trong file theo thứ tự bảng chữ cái."""
    file_path = Path(file_path)

    if not file_path.exists():
        print(f"Lỗi: File '{file_path}' không tồn tại.")
        return

    if not file_path.is_file():
        print(f"Lỗi: '{file_path}' không phải là một file hợp lệ.")
        return

    # Đảm bảo file có dòng trống ở cuối
    with file_path.open("a", encoding="utf-8") as file:
        file.write("\n")

    try:
        lines = file_path.read_text(encoding="utf-8").splitlines(keepends=True)
    except Exception as e:
        print(f"Lỗi khi đọc file: {e}")
        return

    if not lines:
        print("Lỗi: File rỗng, không có gì để sắp xếp.")
        return

    lines = [line for line in lines if line.strip()]
    sorted_lines = sorted(lines, key=str.lower)

    try:
        file_path.write_text("".join(sorted_lines) + "\n", encoding="utf-8")
        print(f"Đã sắp xếp xong file '{file_path}'.")
    except Exception as e:
        print(f"Lỗi khi ghi file: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Sắp xếp các dòng trong file theo thứ tự bảng chữ cái, "
        "giữ nguyên comment và dòng trống."
    )
    parser.add_argument(
        "file_path", type=str, nargs="?", help="Đường dẫn đến file cần sắp xếp"
    )
    args = parser.parse_args()

    if not args.file_path:
        args.file_path = input("Nhập đường dẫn file cần sắp xếp: ").strip()

    sort_file_lines(args.file_path)
