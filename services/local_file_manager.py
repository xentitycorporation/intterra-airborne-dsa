class LocalFileManager:
    def __init__(self) -> None:
        print("Using faux file manager. No files will be uploaded")
        print()

    def upload_file(self, file_path: str, key: str):
        pass

    def upload_empty_file(self, file_key: str) -> None:
        pass
