import cv2
import numpy as np


def to_grayscale(image: np.ndarray) -> np.ndarray:
    """
    Convert image to grayscale if needed.
    """
    if len(image.shape) == 2:
        return image
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def add_border(
    image: np.ndarray,
    border_size: int = 20,
    color=(255, 255, 255)
) -> np.ndarray:
    """
    Add white border around the image.
    """
    return cv2.copyMakeBorder(
        image,
        border_size,
        border_size,
        border_size,
        border_size,
        cv2.BORDER_CONSTANT,
        value=color
    )


def resize_image(
    image: np.ndarray,
    scale: float
) -> np.ndarray:
    """
    Resize image using cubic interpolation.
    """
    return cv2.resize(
        image,
        None,
        fx=scale,
        fy=scale,
        interpolation=cv2.INTER_CUBIC
    )


def calculate_brightness(gray: np.ndarray) -> float:
    """
    Calculate average brightness.
    """
    return float(np.mean(gray))


def calculate_contrast(gray: np.ndarray) -> float:
    """
    Calculate image contrast using standard deviation.
    """
    return float(np.std(gray))


def calculate_blur(gray: np.ndarray) -> float:
    """
    Calculate blur score using Laplacian variance.
    Higher value = Sharper image.
    Lower value = Blurrier image.
    """
    return float(cv2.Laplacian(gray, cv2.CV_64F).var())


def image_resolution(image: np.ndarray):
    """
    Return image width and height.
    """
    height, width = image.shape[:2]
    return width, height


def is_grayscale(image: np.ndarray) -> bool:
    """
    Check whether image is already grayscale.
    """
    return len(image.shape) == 2


def save_image(
    image: np.ndarray,
    output_path: str
):
    """
    Save processed image.
    """
    cv2.imwrite(output_path, image)