import tempfile
from pathlib import Path

from wand.exceptions import MissingDelegateError
from wand.image import Image

from otto.constants import DEFAULT_IMAGE_HEIGHT, DEFAULT_IMAGE_WIDTH


def get_image_size(filename: str) -> tuple[int, int]:
    """Get the width and height of an image."""
    try:
        with Image(filename=filename) as img:
            return img.width, img.height
    except MissingDelegateError:
        return DEFAULT_IMAGE_WIDTH, DEFAULT_IMAGE_HEIGHT


def get_fileext(filename: str, img: Image) -> str:
    """Get the file extension of an image."""
    tmp_file_ext = Path(filename).suffix
    if tmp_file_ext in [".jpg", ".png", ".gif", ".webp"]:
        return tmp_file_ext
    if img.mimetype == b"image/jpeg" or img.mimetype == b"image/jpg":
        return ".jpg"
    if img.mimetype == b"image/png":
        return ".png"
    if img.mimetype == b"image/gif":
        return ".gif"
    if img.mimetype == b"image/webp":
        return ".webp"
    return ".png"


def resize_image(
    filename: str,
    max_width: int = int(DEFAULT_IMAGE_WIDTH * 2),
    max_height: int = int(DEFAULT_IMAGE_HEIGHT * 2),
) -> tuple[str, int, int]:
    """Resize an image to a max width and height."""
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
