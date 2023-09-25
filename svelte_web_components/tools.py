import asyncio
import os
import tarfile

def is_async():
    try:
        asyncio.get_running_loop()
        return True
    except RuntimeError:
        return False

def compress_folder(filename, folder_to_compress):
    with tarfile.open(filename, "w:gz") as tar:
        for root, _, files in os.walk(folder_to_compress):
            for file in files:
                file_path = os.path.join(root, file)
                tar.add(file_path, arcname=os.path.relpath(file_path, folder_to_compress))


def extract_folder(filename, folder_to_extract):
    with tarfile.open(filename, "r:gz") as tar:
        tar.extractall(folder_to_extract)
