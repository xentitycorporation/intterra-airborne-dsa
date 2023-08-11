"""Main file"""

from datetime import datetime, timezone
from pathlib import Path
import sys
import os
from typing import Tuple

# from airborne_dsa.config_manager import ConfigManager

# If running from executable file, path is determined differently
root_directory = os.path.dirname(
    os.path.realpath(sys.executable)
    if getattr(sys, "frozen", False)
    else os.path.realpath(__file__)
)


def get_mission_details() -> Tuple[str, datetime]:
    """Get mission name and time from input"""

    RESET = "\033[0m"  # Reset all formatting
    GREEN = "\033[92m"  # Green text

    print(f"{GREEN}Enter Mission Name:{RESET}")
    mission_name = input().replace(" ", "")
    print()
    print(
        f"{GREEN}Enter local time (format: YYYY-MM-DD HH:MM:SS) [default now]:{RESET}"
    )
    try:
        mission_time = datetime.now().replace(microsecond=0).astimezone(timezone.utc)
        if mission_time_input := input():
            mission_time = datetime.strptime(
                mission_time_input, "%Y-%m-%d %H:%M:%S"
            ).astimezone(timezone.utc)

    except ValueError:
        print("Invalid datetime provided")
        sys.exit(1)
    print()

    return mission_name, mission_time


def mkdir_ignore_file_exist(file_path: str) -> None:
    """Creates a directory using a file path and ignores FileExistsError"""
    try:
        Path(file_path).mkdir()
    except FileExistsError:
        pass


def create_mission_scaffolding(mission_name: str, mission_time: datetime) -> None:
    """Create mission folder scaffolding for upload"""

    mkdir_ignore_file_exist(f"{root_directory}/missions")
    mission_base_path = (
        f"{root_directory}/missions/{mission_name}_{mission_time.isoformat()}"
    )
    mkdir_ignore_file_exist(mission_base_path)

    mkdir_ignore_file_exist(f"{mission_base_path}/images")
    mkdir_ignore_file_exist(f"{mission_base_path}/images/IR")
    mkdir_ignore_file_exist(f"{mission_base_path}/images/EO")

    mkdir_ignore_file_exist(f"{mission_base_path}/tactical")
    mkdir_ignore_file_exist(f"{mission_base_path}/tactical/DPS")
    mkdir_ignore_file_exist(f"{mission_base_path}/tactical/HeatPerim")
    mkdir_ignore_file_exist(f"{mission_base_path}/tactical/IsolatedHeat")

    mkdir_ignore_file_exist(f"{mission_base_path}/videos")


def main() -> None:
    """Entry point"""

    mission_name, mission_time = get_mission_details()
    create_mission_scaffolding(mission_name, mission_time)

    # TODO: Scan folders for new files
    # TODO: Create filename for corresponding file path
    # TODO: Upload to right bucket prefix


if __name__ == "__main__":
    main()
