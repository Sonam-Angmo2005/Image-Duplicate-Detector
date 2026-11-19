
import hashlib
from PIL import Image


def compute_md5(file_path):
    hash_md5 = hashlib.md5()

    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(65536), b""):
            hash_md5.update(chunk)

    return hash_md5.hexdigest()


def compute_ahash(file_path):
    image = Image.open(file_path).convert("L")
    image = image.resize((8, 8))

    pixels = list(image.getdata())
    average = sum(pixels) / len(pixels)

    hash_value = ""

    for pixel in pixels:
        if pixel >= average:
            hash_value += "1"
        else:
            hash_value += "0"

    return hash_value



def compute_hash(file_path, mode):

    if mode.lower() == "md5":
        return compute_md5(file_path)

    elif mode.lower() == "ahash":
        return compute_ahash(file_path)

    else:
        raise ValueError("Invalid hashing mode")

