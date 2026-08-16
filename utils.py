import uuid
import os

CACHE_FOLDER = "cache"

os.makedirs(CACHE_FOLDER, exist_ok=True)


def generate_file_id():
    return str(uuid.uuid4())


def get_output_path(file_id):
    return os.path.join(
        CACHE_FOLDER,
        f"{file_id}.csv"
    )