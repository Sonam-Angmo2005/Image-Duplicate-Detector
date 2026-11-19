
import os


def get_file_size(file_path):
    return os.path.getsize(file_path)


def delete_file(file_path):
    file_size = os.path.getsize(file_path)

    os.remove(file_path)

    return file_size
