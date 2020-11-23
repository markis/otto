import os
import tempfile

from typing import Tuple

from wand.exceptions import MissingDelegateError
from wand.image import Image


def get_image_size(filename: str) -> Tuple[int, int]:
    try:
        with Image(filename=filename) as img:
            return img.width, img.height
    except MissingDelegateError:
        return 300, 400


def resize_image(
    filename: str, max_width: int = int(300 * 2), max_height: int = int(400 * 2)
) -> str:
    assert filename

    file_ext = os.path.splitext(filename)[1]
    new_file_name = tempfile.mkstemp(file_ext)[1]
    try:
        with Image(filename=filename) as img:
            if img.height > max_height or img.width > max_width:
                img.transform(resize=f"{max_width}x{max_height}>")
            else:
                max_width = int(max_width / 2)
                max_height = int(max_height / 2)
                img.transform(resize=f"{max_width}x{max_height}>")
            img.save(filename=new_file_name)
    except MissingDelegateError:
        new_file_name = filename
    return new_file_name
