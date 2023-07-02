import os
import tempfile

from wand.exceptions import MissingDelegateError
from wand.image import Image


def get_image_size(filename: str) -> tuple[int, int]:
    try:
        with Image(filename=filename) as img:
            return img.width, img.height
    except MissingDelegateError:
        return 300, 400


def get_fileext(filename: str, img: Image) -> str:
    tmp_file_ext = os.path.splitext(filename)[1]
    if tmp_file_ext in [".jpg", ".png", ".gif", ".webp"]:
        return tmp_file_ext
    elif img.mimetype == b"image/jpeg" or img.mimetype == b"image/jpg":
        return ".jpg"
    elif img.mimetype == b"image/png":
        return ".png"
    elif img.mimetype == b"image/gif":
        return ".gif"
    elif img.mimetype == b"image/webp":
        return ".webp"
    return ".png"


def resize_image(filename: str, max_width: int = int(300 * 2), max_height: int = int(400 * 2)) -> tuple[str, int, int]:
    assert filename

    new_file_name = None
    try:
        with Image(filename=filename) as img:
            if img.height > max_height or img.width > max_width:
                img.transform(resize=f"{max_width}x{max_height}>")
            else:
                max_width = int(max_width / 2)
                max_height = int(max_height / 2)
                img.transform(resize=f"{max_width}x{max_height}>")
            file_ext = get_fileext(filename, img)
            new_file_name = tempfile.mkstemp(file_ext)[1]
            img.save(filename=new_file_name)
    except MissingDelegateError:
        new_file_name = filename

    width, height = get_image_size(new_file_name)

    return new_file_name, width, height
