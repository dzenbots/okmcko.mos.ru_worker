import datetime
import zipfile
from pathlib import Path


class Unziper:
    path: Path
    target_path: Path

    def unzip_file(self, path: Path, target_path: Path):
        if not path.exists() or not path.is_file():
            raise FileNotFoundError
        self.path = path
        if target_path.exists() and target_path.is_file():
            raise NotADirectoryError
        self.target_path = target_path

        try:
            with zipfile.ZipFile(file=path, metadata_encoding='cp866') as zip_ref:
                zip_ref.extractall(target_path)
        except FileNotFoundError:
            print(f"Error: The file {path} was not found.")
        except zipfile.BadZipFile:
            print(f"Error: {path} is not a valid ZIP file.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
