import argparse
import hashlib
import shutil
from pathlib import Path
from typing import Union, List, Tuple

import cv2
import imutils
import pandas as pd


def get_args():
    """
    Get arguments from command line

    :return: Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Check duplicated files inside a folder and in cross folders"
    )
    parser.add_argument("--folders", type=str, nargs="+", required=True,
                        help="Folders to check, priority increases from left to right")
    parser.add_argument("--aliases", type=str, nargs="+", help="Aliases for folders")
    parser.add_argument("--methods", type=str, nargs="+", default=["checksum"],
                        choices=["checksum", "name"], help="Methods to check duplicated files")
    parser.add_argument("--show", action="store_true", help="Show duplicated files (images only)")
    parser.add_argument("--move", action="store_true", help="Move duplicated files to new folder")

    return parser.parse_args()


class DuplicatingChecker:
    """
    Class to check duplicated files
    """

    def __init__(self, methods: List[str] = None, is_show: bool = False, is_move: bool = False):
        """
        Initialize DuplicatingChecker class

        :param methods: Methods to check duplicated files
        :param is_show: Show duplicated files (images only)
        :param is_move: Move duplicated files to new folder
        """
        if not methods:
            methods = ["checksum"]

        self.methods = methods
        self.is_show = is_show
        self.is_move = is_move

    @staticmethod
    def calculate_checksum(filepath: Union[str, Path]) -> str:
        """
        Calculate MD5 checksum of a file

        :param filepath: Path to file
        :return: MD5 checksum of file
        """
        with open(filepath, "rb") as f:
            checksum = hashlib.md5(f.read()).hexdigest()

        return checksum

    @staticmethod
    def extract_name(filepath: Union[str, Path]) -> str:
        """
        Extract name of file

        :param filepath: Path to file
        :return: Name of file
        """
        filepath = Path(filepath)

        return filepath.name

    @staticmethod
    def check_self_duplicate(folder_properties: list, ignore_indexes: list = None
                             ) -> Tuple[list, list]:
        """
        Get duplicate file indexes in a folder and its original file indexes for matching

        :param folder_properties: List of files' properties (checksum, name,...) in a folder,
            which is used to compare
        :param ignore_indexes: List of indexes to ignore (because they are already checked)
        :return: List of duplicate file indexes and their original file indexes
        """
        duplicate_indexes = []
        original_indexes = []

        if not ignore_indexes:
            ignore_indexes = []

        temp = {}
        for i, element in enumerate(folder_properties):
            if i in ignore_indexes:
                continue
            if element in temp:
                duplicate_indexes.append(i)
                original_indexes.append(temp[element])
            else:
                temp[element] = i

        return duplicate_indexes, original_indexes

    @staticmethod
    def check_cross_duplicate(main_folder_properties: list, secondary_folder_properties: list,
                              ignore_indexes: list = None) -> Tuple[list, list]:
        """
        Get indexes of duplicate files in the secondary folder
        and their original file indexes in the main folder

        :param main_folder_properties: List of files' properties (checksum, name,...)
            in the main folder, which is used to compare
        :param secondary_folder_properties: List of files' properties (checksum, name,...)
            in the secondary folder, which is used to compare
        :param ignore_indexes: List of indexes to ignore (because they are already checked)
        :return: List of duplicate file indexes and their original file indexes
        """
        duplicate_indexes = []
        original_indexes = []

        if not ignore_indexes:
            ignore_indexes = []

        temp = {}
        for i, element in enumerate(secondary_folder_properties):
            if i in ignore_indexes:
                continue
            if element in main_folder_properties:
                duplicate_indexes.append(i)
                original_indexes.append(main_folder_properties.index(element))
            else:
                temp[element] = i

        return duplicate_indexes, original_indexes

    def check(self, folders: List[str], aliases: List[str] = None):
        """
        Check duplicated files in folders

        :param folders: Folders to check. Priority increases from left to right
        :param aliases: Aliases for folders
        """
        assert all(Path(folder).is_dir() for folder in folders), "All paths must be folders"

        # Create folder to store duplicate files
        if self.is_move:
            for folder in folders:
                Path(folder, "duplicated").mkdir(exist_ok=True)

        # Get standard aliases for folders
        if not aliases:
            aliases = [Path(folder).name for folder in folders]
        if len(aliases) > len(set(aliases)):
            # If aliases contain duplicated names, fix duplicated names by adding index
            temp = {}
            for i, alias in enumerate(aliases):
                if alias in temp:
                    aliases[i] = f"{alias}({temp[alias]})"
                    temp[alias] += 1
                else:
                    temp[alias] = 1
        assert len(aliases) == len(folders), "Number of aliases must be equal to number of folders"

        # Get all file paths in folders
        folder_filepaths = {}

        for alias, folder in zip(aliases, folders):
            folder_filepaths[alias] = [filepath for filepath in Path(folder).glob("*")
                                       if filepath.is_file()]

        # Get properties of files in folders
        folder_properties = {method: {} for method in self.methods}

        for i, alias in enumerate(aliases):
            if "checksum" in self.methods:
                folder_properties["checksum"][alias] = [
                    self.calculate_checksum(filepath) for filepath in folder_filepaths[alias]
                ]
            if "name" in self.methods:
                folder_properties["name"][alias] = [
                    self.extract_name(filepath) for filepath in folder_filepaths[alias]
                ]

        # Check duplicated files
        summary = []
        for i, alias_1 in enumerate(aliases):
            # Create a dataframe to store the number of duplicated files
            duplicate_status = pd.DataFrame(columns=aliases[i:], index=self.methods)
            ignore_indexes = []

            for j in range(i, len(aliases)):
                alias_2 = aliases[j]

                for method in self.methods:
                    if i == j:
                        # Check duplicated files in the same folder
                        dup_indexes, org_indexes = self.check_self_duplicate(
                            folder_properties[method][alias_1],
                            ignore_indexes)
                    else:
                        # Check duplicated files in cross folders
                        dup_indexes, org_indexes = self.check_cross_duplicate(
                            folder_properties[method][alias_2],
                            folder_properties[method][alias_1],
                            ignore_indexes)

                    # Update the number of duplicated files and ignore duplicated indexes
                    duplicate_status.loc[method, alias_2] = len(dup_indexes)
                    ignore_indexes.extend(dup_indexes)

                    for m in range(len(dup_indexes)):
                        dup_filepath = folder_filepaths[alias_1][dup_indexes[m]]
                        org_filepath = folder_filepaths[alias_2][org_indexes[m]]
                        dup_property = folder_properties[method][alias_1][dup_indexes[m]]
                        org_property = folder_properties[method][alias_2][org_indexes[m]]

                        if self.is_show:
                            print("\n" + "-" * 50)
                            print(f"Duplicated file ({alias_1}): {dup_filepath.name}")
                            print(f"Duplicate of ({alias_2}): {org_filepath.name}")
                            print(f"Reason: Same {method} ({dup_property} == {org_property})")

                            # Show images if they are images
                            img_org = cv2.imread(str(org_filepath))
                            img_dup = cv2.imread(str(dup_filepath))
                            img_org = imutils.resize(img_org, width=500)
                            img_dup = imutils.resize(img_dup, width=500)
                            cv2.imshow("org", img_org)
                            cv2.imshow("dup", img_dup)
                            cv2.waitKey(0)

                        if self.is_move:
                            shutil.move(dup_filepath,
                                        Path(folders[i], "duplicated", dup_filepath.name))

            # Append the summary of duplicated files in the folder
            summary.append(duplicate_status.astype(int))

        # Print the summary
        print("\n" + "-" * 50)
        print("SUMMARY")

        for i, alias in enumerate(aliases):
            print(f"\nNumber of duplicate files in folder '{alias}': {summary[i].values.sum()}")
            print(summary[i])


if __name__ == "__main__":
    args = get_args()
    checker = DuplicatingChecker(methods=args.methods, is_show=args.show, is_move=args.move)
    checker.check(args.folders, args.aliases)
