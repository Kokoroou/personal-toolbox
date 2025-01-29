"""
Manager to handle storages of Label Studio data
"""

import argparse
import json
import os
import time
from pathlib import Path
from typing import Dict, List, Union

from dotenv import load_dotenv

from personal_tools.data_analysis.label_studio.managers.base import (
    BaseManager,
    BaseManagerConfig,
)
from personal_tools.data_analysis.label_studio.utilities.storage import standardize_path

# Define default location to store temporary files
TEMP_DIR = "/tmp/kokoroou-cached"
if not Path(TEMP_DIR).exists():
    Path(TEMP_DIR).mkdir(parents=True, exist_ok=True)


def get_args():
    """Get parsed arguments from command line."""
    parser = argparse.ArgumentParser(description="Manage data sources in Label Studio.")

    parser.add_argument("--env", type=str, default="./.env", help="Path to .env file.")
    parser.add_argument(
        "--type",
        "-t",
        type=str,
        default="all",
        help="Type of data sources to manage. " 'Can be "missing", "unused", "all".',
    )
    parser.add_argument(
        "--project",
        "-p",
        type=int,
        metavar="PROJECT_ID",
        help="ID of the project to manage data sources.",
    )
    parser.add_argument(
        "--force",
        "-f",
        action="store_true",
        help="Force to get all data sources from Label Studio again.",
    )

    return parser.parse_args()


class StorageManager(BaseManager):
    """
    Manager to handle storages of Label Studio data
    """

    def get_all_sources(
        self,
        return_dict=False,
        force_update: bool = False,
        cache_file: str = f"{TEMP_DIR}/ls_storage.json",
    ) -> Union[List[str], Dict[str, List[str]]]:
        """
        Get all data sources in Label Studio.

        :param return_dict: Whether to return a dictionary of data sources.
            Key is the data source and value is the list of projects that use the data source.
        :param force_update: Whether to force to get all data sources from Label Studio again.
        :param cache_file: Path to the cache file to store the data sources.
        :return: List of all data sources or a dictionary of data sources.
        """
        ls_sources_dict: dict = {}

        if not force_update and Path(cache_file).exists():
            # Load the data sources from the cache file
            with open(cache_file, "r", encoding="utf-8") as f:
                ls_sources_dict = json.load(f)

        else:
            # Get all projects
            start = time.time()
            print("Getting all projects...", end="", flush=True)
            projects = self.client.list_projects()
            print(f"Done in {time.time() - start:.2f} seconds.")

            for proj_idx, project in enumerate(projects):
                # Add upload folder of the project to the list of data sources
                ls_sources_dict[f"media/upload/{project.id}"] = {project.id}

                # Get all tasks of the project
                start = time.time()
                print(
                    f"[{proj_idx + 1}/{len(projects)}] "
                    f"Getting tasks of project {project.id}...",
                    end="",
                    flush=True,
                )
                tasks = project.get_tasks()
                print(f"Done in {time.time() - start:.2f} seconds.")

                # Extract data sources from tasks
                for task in tasks:
                    data: dict = task["data"]

                    for key in data.keys():
                        source = standardize_path(data[key])
                        if source in ls_sources_dict:
                            ls_sources_dict[source].add(project.id)
                        else:
                            ls_sources_dict[source] = {project.id}

            # Order the IDs of the projects that use the same data source
            for source in ls_sources_dict:
                ls_sources_dict[source] = sorted(list(ls_sources_dict[source]))

            # Order the data sources
            ls_sources_dict = dict(sorted(ls_sources_dict.items()))

            # Save the data sources to the cache file
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(ls_sources_dict, f, indent=4)

        if return_dict:
            return ls_sources_dict

        return list(ls_sources_dict.keys())

    def get_all_folders(self) -> List[str]:
        """
        Get all data folders in Label Studio Server.

        :return: List of all data folders.
        """
        stdin, stdout, stderr = self.ssh_client.exec_command(
            """
            cd ttanh/mydata
            find . -type d
            """
        )

        # Get the list of folders
        ls_sources = stdout.read().decode("utf-8").split()
        ls_sources = sorted(ls_sources)

        # Close the channels
        stdin.close()
        stdout.close()
        stderr.close()

        # Filter out the root folder
        ls_sources = [source for source in ls_sources if source != "."]

        # Remove the leading './' from the folder paths
        ls_sources = [source[len("./") :] for source in ls_sources]

        # Filter out folders that have sub-folder(s)
        to_filter = []
        for source in ls_sources:
            if str(Path(source).parent) in ls_sources:
                to_filter.append(str(Path(source).parent))
        ls_sources = [source for source in ls_sources if source not in to_filter]

        # Filter out some folders that are not data sources
        to_filter = ["export", "media/avatars", "media/export", "test_data"]
        ls_sources = [
            source
            for source in ls_sources
            if not any(source.startswith(f) for f in to_filter)
        ]

        return ls_sources

    def get_missing_sources(self, force_update: bool = False) -> List[str]:
        """
        Get data sources that are missing in Label Studio server.

        :param force_update: Whether to force to get all data sources from Label Studio again.
        :return: List of missing data sources.
        """
        # Get all data folders and sources
        ls_sources = self.get_all_folders()
        used_sources = self.get_all_sources(return_dict=True, force_update=force_update)

        # Filter out sources that are not in the server
        ls_sources = [
            source for source in used_sources.keys() if source not in ls_sources
        ]

        # Add the projects that use the missing sources
        ls_sources = [
            f"{source: <20} - Required by projects: {used_sources[source]}"
            for source in ls_sources
        ]

        return ls_sources

    def get_unused_sources(self, force_update: bool = False) -> List[str]:
        """
        Get data sources that are not used in any project.

        :param force_update: Whether to force to get all data sources from Label Studio again.
        :return: List of unused data sources.
        """
        # Get all data folders and sources
        ls_sources = self.get_all_folders()
        used_sources = self.get_all_sources(force_update=force_update)

        # Filter out folders that are used for projects
        ls_sources = [source for source in ls_sources if source not in used_sources]

        return ls_sources

    def get_sources_by_project(self, project_id) -> List[str]:
        """
        Get data sources of a project by project ID.

        :param project_id: ID of the project to get data sources.
        :return: List of data sources of the project.
        """
        ls_sources: set = set([])

        # Get the project
        project = self.client.get_project(project_id)

        # Get all tasks of the project
        start = time.time()
        print("Getting tasks...", end="", flush=True)
        tasks = project.get_tasks()
        print(f"Done in {time.time() - start:.2f} seconds.")

        # Extract data sources from tasks
        for task in tasks:
            data: dict = task["data"]
            data_keys = data.keys()

            for key in data_keys:
                ls_sources.add(standardize_path(data[key]))

        return sorted(list(ls_sources))


if __name__ == "__main__":
    args = get_args()
    load_dotenv(dotenv_path=args.env)
    assert Path(args.env).exists(), f"File {args.env} does not exist."

    LS_URL = os.getenv("LS_URL")
    LS_API_KEY = os.getenv("LS_API_KEY")
    LS_IP = os.getenv("LS_IP")
    LS_USER = os.getenv("LS_USER")
    LS_PASSWORD = os.getenv("LS_PASSWORD")

    assert LS_URL is not None, f"LS_URL is not set in {args.env} file."
    assert LS_API_KEY is not None, f"LS_API_KEY is not set in {args.env} file"

    # Initialize a Label Studio Manager
    manager = StorageManager(
        BaseManagerConfig(
            url=LS_URL, key=LS_API_KEY, ip=LS_IP, user=LS_USER, password=LS_PASSWORD
        )
    )

    # Get data sources
    if args.project:
        sources = manager.get_sources_by_project(project_id=args.project)
    else:
        if args.type == "all":
            sources = manager.get_all_sources(force_update=args.force)
        elif args.type == "missing":
            sources = manager.get_missing_sources(force_update=args.force)
        elif args.type == "unused":
            sources = manager.get_unused_sources(force_update=args.force)
        else:
            raise ValueError(f"Invalid type: {args.type}")

    print("\nData sources:")
    for src in sources:
        print(src)
