"""Main file"""

from datetime import datetime, timezone
from pathlib import Path
import re
import sys
import os
import time
from typing import Tuple
from watchdog.observers import Observer
from models.product import Product
from services.config_manager import ConfigManager
from services.file_watcher import FileWatcher
from services.local_file_manager import LocalFileManager
from services.s3_file_manager import S3FileManager

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
    # Replace special characters in input with a dash
    mission_name = re.sub(r"[^a-zA-Z0-9\s-]", "-", input().replace(" ", "-"))
    print()
    print(f"{GREEN}Enter local time (format: YYYY-MM-DD HH:MM) [default now]:{RESET}")
    try:
        mission_time = (
            datetime.now()
            .replace(second=0)
            .replace(microsecond=0)
            .astimezone(timezone.utc)
            .replace(tzinfo=None)
        )

        # If input provided, use that instead of current time
        if mission_time_input := input():
            mission_time = (
                datetime.strptime(mission_time_input, "%Y-%m-%d %H:%M")
                .astimezone(timezone.utc)
                .replace(tzinfo=None)
            )

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


def create_mission_scaffolding(mission_name: str, mission_time: datetime) -> str:
    """Create mission folder scaffolding for upload. Returns the mission base path"""

    mkdir_ignore_file_exist(os.path.join(root_directory, "missions"))
    mission_base_path = os.path.join(
        root_directory,
        "missions",
        f"{mission_time.isoformat()[:-3].replace(':', '')}_{mission_name}",
    )
    mkdir_ignore_file_exist(mission_base_path)

    mkdir_ignore_file_exist(os.path.join(mission_base_path, "images"))
    mkdir_ignore_file_exist(os.path.join(mission_base_path, "images", "EO"))
    mkdir_ignore_file_exist(os.path.join(mission_base_path, "images", "HS"))
    mkdir_ignore_file_exist(os.path.join(mission_base_path, "images", "IR"))

    mkdir_ignore_file_exist(os.path.join(mission_base_path, "tactical"))
    mkdir_ignore_file_exist(os.path.join(mission_base_path, "tactical", "Detection"))
    mkdir_ignore_file_exist(
        os.path.join(mission_base_path, "tactical", "HeatPerimeter")
    )
    mkdir_ignore_file_exist(os.path.join(mission_base_path, "tactical", "IntenseHeat"))
    mkdir_ignore_file_exist(os.path.join(mission_base_path, "tactical", "IsolatedHeat"))
    mkdir_ignore_file_exist(
        os.path.join(mission_base_path, "tactical", "ScatteredHeat")
    )

    mkdir_ignore_file_exist(os.path.join(mission_base_path, "videos"))

    return os.path.normpath(mission_base_path)


def create_product_from_file_path(file_path: str) -> Product:
    """Takes in a file path and returns a Product"""

    product = None
    last_modified_on = datetime.fromtimestamp(os.path.getmtime(file_path)).astimezone(
        timezone.utc
    )

    folders_in_path = file_path.split(os.path.sep)
    # We only want to check the mission path, without filename and user's path
    mission_path = folders_in_path[folders_in_path.index("missions") + 2 : -1]

    if "images" in mission_path:
        if "EO" in mission_path:
            product = Product("image", "EO", last_modified_on)
        if "HS" in mission_path:
            product = Product("image", "HS", last_modified_on)
        if "IR" in mission_path:
            product = Product("image", "IR", last_modified_on)
    elif "tactical" in mission_path:
        if "Detection" in mission_path:
            product = Product("tactical", "Detection", last_modified_on)
        if "HeatPerimeter" in mission_path:
            product = Product("tactical", "HeatPerimeter", last_modified_on)
        if "IntenseHeat" in mission_path:
            product = Product("tactical", "IntenseHeat", last_modified_on)
        if "IsolatedHeat" in mission_path:
            product = Product("tactical", "IsolatedHeat", last_modified_on)
        if "ScatteredHeat" in mission_path:
            product = Product("tactical", "ScatteredHeat", last_modified_on)
    elif "videos" in mission_path:
        product = Product("video", None, last_modified_on)

    if product is None:
        raise ValueError(f"Failed to map product: {os.path.basename(file_path)}")

    return product


def get_product_s3_key(mission_name: str, product: Product, file_extension: str) -> str:
    folder = None
    product_subtype = None

    if product.type == "image":
        folder = "IMAGERY"

        if product.subtype == "EO":
            product_subtype = "EOimage"
        elif product.subtype == "HS":
            product_subtype = "HSimage"
        elif product.subtype == "IR":
            product_subtype = "IRimage"

    elif product.type == "tactical":
        folder = "TACTICAL"
        product_subtype = product.subtype
    elif product.type == "video":
        folder = "VIDEO"
        product_subtype = "Video"

    return f"{folder}/{product.timestamp.strftime('%Y%m%d_%H%M%SZ')}_{mission_name}_{product_subtype}{file_extension}"


def get_account_selection(accounts):
    """Prompt user to select an account"""
    RESET = "\033[0m"  # Reset all formatting
    GREEN = "\033[92m"  # Green text
    YELLOW = "\033[93m"  # Yellow text for warnings

    # Check if there are any accounts with proper remote storage configuration
    remote_accounts = [
        a
        for a in accounts
        if isinstance(a, dict) and a.get("storageMode", "remote") == "remote"
    ]

    if not remote_accounts:
        print(
            f"{YELLOW}Warning: No properly configured remote accounts found in config.{RESET}"
        )
        print(
            f"{YELLOW}Files will be stored locally. Check your config.json file.{RESET}"
        )
        print()

    print(f"{GREEN}Select an account to upload data:{RESET}")
    for i, account in enumerate(accounts):
        storage_type = (
            "S3" if account.get("storageMode", "remote") == "remote" else "Local"
        )
        bucket_info = (
            f"(Bucket: {account.get('bucket', 'N/A')} Base Folder: {account.get('folder', 'N/A')})" if storage_type == "S3" else ""
        )
        print(f"{i+1}. {account['name']} - {storage_type} {bucket_info}")

    # Get user selection
    selected_account_index = 0  # Default to first account
    if len(accounts) > 1:
        while True:
            try:
                selection = int(input("Enter account number: ")) - 1
                if 0 <= selection < len(accounts):
                    selected_account_index = selection
                    break
                else:
                    print("Invalid selection. Please try again.")
            except ValueError:
                print("Please enter a number.")

    selected_account = accounts[selected_account_index]

    # Show detailed information about selected account
    print(f"{GREEN}Selected account:{RESET} {selected_account.get('name')}")
    storage_mode = selected_account.get("storageMode", "remote")
    if storage_mode == "remote":
        bucket = selected_account.get("bucket")
        if bucket:
            print(f"Files will be uploaded to S3 bucket: {bucket}")
        else:
            print(
                f"{YELLOW}Warning: No bucket specified for this account. Check config.json.{RESET}"
            )
    else:
        print("Files will be stored locally (no S3 upload)")
    print()

    return selected_account


def main() -> None:
    """Entry point"""

    # Setup
    config = ConfigManager("config.json")

    # Get accounts from config
    accounts = config.get_accounts()

    # Have user select which account to use
    selected_account = get_account_selection(accounts)

    # Initialize the appropriate file manager based on the selected account
    if selected_account.get("storageMode", "remote") == "remote":
        # Ensure all required S3 credentials are present
        if not all(
            [
                selected_account.get("awsAccessKeyId"),
                selected_account.get("awsSecretAccessKey"),
                selected_account.get("bucket"),
            ]
        ):
            print(
                "ERROR: Missing required S3 credentials in config. Check your config.json file."
            )
            print(f"Required fields: awsAccessKeyId, awsSecretAccessKey, bucket")
            print(f"Available fields: {', '.join(selected_account.keys())}")
            sys.exit(1)

        # Initialize S3 file manager with account-specific bucket
        file_manager = S3FileManager(
            selected_account.get("awsAccessKeyId"),
            selected_account.get("awsSecretAccessKey"),
            selected_account.get("bucket"),
        )
        print(f"Initialized S3 file manager for bucket: {selected_account.get('bucket')}")
    else:
        file_manager = LocalFileManager()
        print("Using local file manager. Files will be stored locally.")

    mission_name, mission_time = get_mission_details()

    # Create mission file with proper path prefix if vendor is specified
    try:
        mission_file_key = (
            f"MISSION/{mission_name}_{mission_time.strftime('%Y%m%d_%H%M')}Z.txt"
        )

        # Add vendor prefix if specified
        if selected_account.get('folder'):
            mission_file_key = f"{selected_account.get('folder')}/{mission_file_key}"

        file_manager.upload_empty_file(mission_file_key)

        # Verify that we're using the correct file manager type
        file_manager_type = type(file_manager).__name__
        if selected_account.get("storageMode", "remote") == "remote":
            print(
                f"Created mission: {mission_name} in S3 bucket: {selected_account.get('bucket')}"
            )
            print(f"Mission file path: {mission_file_key}")
        else:
            print(f"Created mission: {mission_name} locally")
            print(f"Using file manager: {file_manager_type}")
    except Exception as error:
        print(f"Failed to create mission: {str(error)}")
        # Add more detailed error information
        import traceback

        print("\nDetailed error information:")
        traceback.print_exc()
        sys.exit(1)

    mission_base_path = create_mission_scaffolding(mission_name, mission_time)

    # Handle new files
    def upload_product(file_path: str) -> None:
        try:
            product = create_product_from_file_path(file_path)
            key = get_product_s3_key(
                mission_name, product, os.path.splitext(file_path)[1]
            )

            # Add vendor prefix if specified
            if selected_account.get('folder'):
                key = f"{selected_account.get('folder')}/{key}"

            print(f"Uploading {os.path.basename(file_path)}")
            try:
                file_manager.upload_file(file_path, key)

                if isinstance(file_manager, S3FileManager):
                    print(
                        f"Successfully uploaded {os.path.basename(file_path)} as {key} to bucket: {selected_account.get('bucket')}"
                    )
                else:
                    print(
                        f"Successfully processed {os.path.basename(file_path)} as {key} (local storage mode)"
                    )
            except Exception as upload_error:
                print(
                    f"Error uploading file {os.path.basename(file_path)}: {str(upload_error)}"
                )
                # For debugging
                import traceback

                traceback.print_exc()

        except Exception as error:
            print(error)

    # Set up file monitoring for mission folder
    print(f"Setting up file monitoring for {mission_base_path}")
    file_watcher = FileWatcher(upload_product)
    observer = Observer()
    observer.schedule(file_watcher, mission_base_path, recursive=True)
    observer.start()

    print(f"Watching for new files in ${mission_base_path}")
    print()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        log_file = open("ERROR.txt", "w")
        log_file.write(str(error))
        log_file.close()
        print(error)
