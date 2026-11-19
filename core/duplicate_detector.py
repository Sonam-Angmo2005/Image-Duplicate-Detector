
from pathlib import Path
from core.hashing import compute_hash


SUPPORTED_EXT = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".bmp"
}


def scan_folder(folder_path, mode):

    folder_path = Path(folder_path)

    hash_buckets = {}

    for file_path in folder_path.rglob("*"):

        if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_EXT:

            try:
                file_hash = compute_hash(file_path, mode)

                if file_hash not in hash_buckets:
                    hash_buckets[file_hash] = []

                hash_buckets[file_hash].append(file_path)

            except Exception:
                continue

    duplicates = {}

    for file_hash, files in hash_buckets.items():

        if len(files) > 1:
            duplicates[file_hash] = files

    return duplicates
