# utils/image_loader.py

from pathlib import Path
from PIL import Image


def load_image(name: str):
    """
    Load image from resources folder.

    Args:
        name: filename including extension

    Returns:
        PIL Image
    """

    resources = Path(__file__).resolve().parent.parent / "resources"

    with open(resources / name, "rb") as f:
        image = Image.open(f)
        image.load()
        return image
