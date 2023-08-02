from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Final, NamedTuple
from unittest.mock import MagicMock, patch

import pytest

from otto.constants import DEFAULT_IMAGE_HEIGHT, DEFAULT_IMAGE_WIDTH
from otto.utils.image import (
    get_fileext,
    get_image_size,
    resize_image,
)

TEST_IMAGE_WIDTH: Final = 1280
TEST_IMAGE_HEIGHT: Final = 989


class Size(NamedTuple):
    width: int
    height: int


@pytest.fixture()
def image_path() -> Path:
    """Return the path to a test image."""
    return Path(__file__).parent / "images" / "test.png"


@contextmanager
def _get_image_mock(mock_image_instance: MagicMock | Exception, *, side_effect: bool = False) -> Iterator[MagicMock]:
    image_mock = MagicMock()
    with patch.dict("sys.modules", {"wand.image": image_mock}):  # import is done inside the function
        if side_effect:
            image_mock.Image().__enter__.side_effect = mock_image_instance
        else:
            image_mock.Image().__enter__.return_value = mock_image_instance
        yield image_mock


def test_get_image_size(image_path: Path) -> None:
    """Test that get_image_size returns the correct width and height."""
    width, height = get_image_size(image_path)
    assert width == TEST_IMAGE_WIDTH
    assert height == TEST_IMAGE_HEIGHT


def test_get_image_size_error(image_path: Path) -> None:
    """Test that get_image_size returns the default width and height when it can't read the image."""
    exceptions = pytest.importorskip("wand.exceptions", reason="Wand or ImageMagick is not installed")

    with _get_image_mock(exceptions.MissingDelegateError, side_effect=True):
        width, height = get_image_size(image_path)
    assert width == DEFAULT_IMAGE_WIDTH
    assert height == DEFAULT_IMAGE_HEIGHT


def test_get_fileext() -> None:
    """Test that get_fileext returns the correct file extension."""
    file_extensions = [".jpg", ".jpg", ".png", ".gif", ".webp"]
    mimetypes = [b"image/jpeg", b"image/jpg", b"image/png", b"image/gif", b"image/webp"]
    for ext in file_extensions:
        assert get_fileext(Path(f"test.{ext}"), None) == ext

    for mimetype, ext in zip(mimetypes, file_extensions, strict=True):
        assert get_fileext(Path("test"), mimetype) == ext

    assert get_fileext(Path("test"), b"") == ".png"  # test the else clause


@patch("otto.utils.image.tempfile.mkstemp", autospec=True, return_value=(None, "temp_file_path"))
@pytest.mark.parametrize(
    ("image_size", "resize", "expected_size"),
    [(Size(800, 600), Size(500, 500), Size(800, 600)), (Size(800, 600), Size(500, 500), Size(800, 600))],
)
def test_resize_large_image(
    mock_mkstemp: MagicMock,
    image_size: Size,
    resize: Size,
    expected_size: Size,
) -> None:
    """Test that resize_image returns the correct width and height."""
    image_instance_mock = MagicMock(height=image_size.width, width=image_size.height)
    with _get_image_mock(image_instance_mock):
        new_file, width, height = resize_image(Path("test.png"), max_width=resize.width, max_height=resize.height)

    mock_mkstemp.assert_called_once_with(".png")
    image_instance_mock.save.assert_called_once_with(filename=Path("temp_file_path"))
    image_instance_mock.transform.assert_called_once_with(resize=f"{resize.width}x{resize.height}>")
    assert width == expected_size.height
    assert height == expected_size.width
    assert new_file == Path("temp_file_path")
