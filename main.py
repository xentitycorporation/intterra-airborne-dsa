"""Main file with updated watchdog implementation"""

from datetime import datetime, timezone
from pathlib import Path
import re
import sys
import os
import time
import glob
from typing import Tuple
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from models.product import Product
from services.config_manager import ConfigManager

from services.local_file_manager import LocalFileManager
from services.s3_file_manager import S3FileManager

# If running from executable file, path is determined differently
root_directory = os.path.dirname(
    os.path.realpath(sys.executable)
    if getattr(sys, "frozen", False)
    else os.path.realpath(__file__)
)

# Custom event handler to replace FileWatcher if needed
class CustomFileHandler(FileSystemEventHandler):
    """Handles file system events and processes new files"""
    
    def __init__(self, callback):
        """Initialize with callback to process files"""
        self.callback = callback
        self.processed_files = set()
        super().__init__()
    
    def on_created(self, event):
        """Process newly created files (non-directories)"""
        if not event.is_directory:
            self._process_file(event.src_path)
    
    def on_modified(self, event):
        """Process modified files (non-directories)"""
        if not event.is_directory:
            self._process_file(event.src_path)
    
    def _process_file(self, file_path):
        """Process a file if it hasn't been processed yet"""
        if file_path in self.processed_files:
            return
        
        # Skip temporary/system files
        filename = os.path.basename(file_path)
        if filename.startswith('.') or filename.startswith('~$'):
            return
        
        # Wait a moment to ensure file is completely written
        time.sleep(0.5)
        
        # Process the file
        try:
            self.callback(file_path)
            self.processed_files.add(file_path)
        except Exception as e:
            print(f"Error processing file {file_path}: {str(e)}")


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


def manual_file_polling(mission_base_path, upload_product):
    """Fallback method using manual polling instead of watchdog"""
    import glob
    
    print(f"Using manual polling for {mission_base_path}")
    processed_files = set()
    
    try:
        while True:
            # Find all files in the mission directory
            all_files = []
            for ext in ['*.jpg', '*.jpeg', '*.png', '*.tif', '*.mp4', '*.txt', '*.json']:
                all_files.extend(glob.glob(os.path.join(mission_base_path, '**', ext), recursive=True))
            
            # Process new files
            for file_path in all_files:
                if file_path not in processed_files:
                    processed_files.add(file_path)
                    # Only process files that have existed for at least 1 second
                    if time.time() - os.path.getmtime(file_path) > 1:
                        upload_product(file_path)
            
            time.sleep(2)  # Check every 2 seconds
    except KeyboardInterrupt:
        pass


def monitor_directory(directory, callback):
    """
    Monitor directory for new files using simple polling
    
    Args:
        directory: Directory to monitor
        callback: Function to call when new file is detected
    """
    processed_files = set()
    print(f"Watching for new files in {directory}")
    print()
    
    try:
        while True:
            # Find all files in the directory
            all_files = []
            for root, _, files in os.walk(directory):
                for file in files:
                    all_files.append(os.path.join(root, file))
            
            # Process new files
            for file_path in all_files:
                if file_path not in processed_files:
                    # Only process if file appears stable (not being written to)
                    try:
                        # Get initial size
                        initial_size = os.path.getsize(file_path)
                        # Wait a moment
                        time.sleep(0.5)
                        # Check if size changed
                        if initial_size == os.path.getsize(file_path):
                            processed_files.add(file_path)
                            callback(file_path)
                    except Exception as e:
                        # File might be in use or deleted
                        pass
                        
            # Sleep to avoid high CPU usage
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping file monitoring")


def main() -> None:
    """Entry point"""

    # Setup
    config = ConfigManager("config.json")
    
    # Check for vendor environment variable
    vendor_prefix = os.environ.get("vendor", "")
    
    # Display available accounts
    accounts = config.get_accounts()
    RESET = "\033[0m"  # Reset all formatting
    GREEN = "\033[92m"  # Green text
    
    print(f"{GREEN}Select an account to upload data:{RESET}")
    for i, account in enumerate(accounts):
        print(f"{i+1}. {account['name']}")
    
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
    print(f"Using account: {selected_account['name']}")
    print()
    
    # Use selected account for file manager
    file_manager = (
        S3FileManager(
            selected_account.get("awsAccessKeyId"), 
            selected_account.get("awsSecretAccessKey"), 
            selected_account.get("bucket")
        )
        if selected_account.get("storageMode", "remote") == "remote"
        else LocalFileManager()
    )
    
    mission_name, mission_time = get_mission_details()
    # Create mission file
    try:
        mission_file_key = f"MISSION/{mission_name}_{mission_time.strftime('%Y%m%d_%H%M')}Z.txt"
        
        # Build the complete path with appropriate prefixes
        # Priority: 1. vendor environment variable, 2. account path from config
        path_prefix = ""
        if vendor_prefix:
            path_prefix = vendor_prefix
        elif "path" in selected_account:
            path_prefix = selected_account['path']
            
        if path_prefix:
            mission_file_key = f"{path_prefix}/{mission_file_key}"
        
        file_manager.upload_empty_file(mission_file_key)
        print(f"Created mission: {mission_name}")
    except Exception as error:
        print(f"Failed to create mission: {str(error)}")
        sys.exit(1)

    mission_base_path = create_mission_scaffolding(mission_name, mission_time)

    # Handle new files
    def upload_product(file_path: str) -> None:
        try:
            product = create_product_from_file_path(file_path)
            key = get_product_s3_key(
                mission_name, 
                product, 
                os.path.splitext(file_path)[1]
            )
            
            # Build the complete path with appropriate prefixes
            # Priority: 1. vendor environment variable, 2. account path from config
            if vendor_prefix:
                key = f"{vendor_prefix}/{key}"
            elif "path" in selected_account:
                key = f"{selected_account['path']}/{key}"

            print(f"Uploading {os.path.basename(file_path)}")
            file_manager.upload_file(file_path, key)
            print(
                f"Successfully uploaded {os.path.basename(file_path)} as {key} to {selected_account.get('bucket', 'local storage')}"
            )

        except Exception as error:
            print(error)

    # Set up file monitoring for mission folder
    print(f"Setting up file monitoring for {mission_base_path}")
    try:
        # Try using watchdog first
        observer = Observer()
        handler = CustomFileHandler(upload_product)
        observer.schedule(handler, mission_base_path, recursive=True)
        observer.start()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()
    except Exception as e:
        print(f"Error with watchdog: {e}")
        print("Falling back to manual polling method")
        monitor_directory(mission_base_path, upload_product)


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        log_file = open("ERROR.txt", "w")
        log_file.write(str(error))
        log_file.close()
        print(error)