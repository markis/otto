import tempfile
from pathlib import Path
from typing import Final

from otto.constants import DEFAULT_IMAGE_HEIGHT, DEFAULT_IMAGE_WIDTH

VALID_EXTENSIONS: Final = (".jpg", ".png", ".gif", ".webp")
MIMETYPE_MAPPING: Final = {
    b"image/jpeg": ".jpg",
    b"image/jpg": ".jpg",
    b"image/png": ".png",
    b"image/gif": ".gif",
    b"image/webp": ".webp",
}


def get_image_size(filename: Path | str) -> tuple[int, int]:
    """Get the width and height of an image."""
    from wand.exceptions import MissingDelegateError
    from wand.image import Image

    try:
        with Image(filename=filename) as img:
            return img.width, img.height
    except MissingDelegateError:
        return DEFAULT_IMAGE_WIDTH, DEFAULT_IMAGE_HEIGHT


def get_fileext(filename: Path, mimetype: bytes | None) -> str:
    """Get the file extension of an image."""
    if filename.suffix in VALID_EXTENSIONS:
        return filename.suffix
    if mimetype:
        return MIMETYPE_MAPPING.get(mimetype, ".png")
    return ".png"


def resize_image(
    filename: Path,
    max_width: int = DEFAULT_IMAGE_WIDTH * 2,
    max_height: int = DEFAULT_IMAGE_HEIGHT * 2,
) -> tuple[Path, int, int]:
    """Resize an image to a max width and height."""
    assert filename
    from wand.exceptions import MissingDelegateError
    from wand.image import Image

    new_file_name = None
    try:
        with Image(filename=filename) as img:
            if img.height > max_height or img.width > max_width:
                img.transform(resize=f"{max_width}x{max_height}>")
            else:
                max_width = int(max_width / 2)
                max_height = int(max_height / 2)
                img.transform(resize=f"{max_width}x{max_height}>")
            file_ext = get_fileext(filename, img.mimetype)
            new_file_name = Path(tempfile.mkstemp(file_ext)[1])
            img.save(filename=new_file_name)
    except MissingDelegateError:
        new_file_name = filename

    width, height = get_image_size(new_file_name)

    return new_file_name, width, height
