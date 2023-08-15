from typing import Callable
from watchdog.events import FileSystemEventHandler, FileSystemEvent


class FileWatcher(FileSystemEventHandler):
    def __init__(self, callback: Callable[[str], None]):
        self.callback = callback

    def on_created(self, event: FileSystemEvent):
        if event.is_directory:
            return

        self.callback(event.src_path)
