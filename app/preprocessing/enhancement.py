import cv2
import numpy as np

from .utils import (
    resize_image,
)


# --------------------------------------------------
# Resize
# --------------------------------------------------

def adaptive_resize(image):
    """
    Resize image based on width.
    """

    height, width = image.shape[:2]

    if width < 600:
        scale = 2.0

    elif width < 1000:
        scale = 1.5

    else:
        scale = 1.0

    return resize_image(image, scale)


# --------------------------------------------------
# Brightness
# --------------------------------------------------

def increase_brightness(image, beta=25):
    """
    Increase image brightness.
    """
    return cv2.convertScaleAbs(image, alpha=1.0, beta=beta)


def reduce_brightness(image, beta=25):
    """
    Reduce brightness for overexposed images.
    """
    return cv2.convertScaleAbs(image, alpha=1.0, beta=-beta)


# --------------------------------------------------
# CLAHE
# --------------------------------------------------

def apply_clahe(gray):
    """
    Improve local contrast.
    """

    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8)
    )

    return clahe.apply(gray)


# --------------------------------------------------
# Denoise
# --------------------------------------------------

def denoise(gray):
    """
    Remove scanner noise while preserving edges.
    """

    return cv2.fastNlMeansDenoising(
        gray,
        None,
        h=10,
        templateWindowSize=7,
        searchWindowSize=21
    )


# --------------------------------------------------
# Sharpen
# --------------------------------------------------

def sharpen(gray):
    """
    Sharpen text edges.
    """

    kernel = np.array([
        [0, -1, 0],
        [-1, 5, -1],
        [0, -1, 0]
    ])

    return cv2.filter2D(gray, -1, kernel)


# --------------------------------------------------
# Adaptive Threshold
# --------------------------------------------------

def adaptive_threshold(gray):
    """
    Adaptive threshold for difficult scans.
    """

    return cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        15
    )


# --------------------------------------------------
# Morphology
# --------------------------------------------------

def morphology(gray):
    """
    Clean small noise.
    """

    kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT,
        (2, 2)
    )

    return cv2.morphologyEx(
        gray,
        cv2.MORPH_OPEN,
        kernel
    )


# --------------------------------------------------
# Main Enhancement Engine
# --------------------------------------------------

def enhance_image(image, report):
    """
    Apply preprocessing based on image quality report.

    report comes from quality.py
    """

    recommendations = report["recommendations"]

    brightness_status = report["brightness"]["status"]

    processed = image.copy()

    # ---------------------------------------
    # Resize
    # ---------------------------------------

    if "resize" in recommendations:
        print("✔ Resizing image")
        processed = adaptive_resize(processed)

    # ---------------------------------------
    # Brightness
    # ---------------------------------------

    if "increase_brightness" in recommendations:
        print("✔ Increasing brightness")
        processed = increase_brightness(processed)

    if brightness_status == "Very Bright":
        print("✔ Reducing brightness")
        processed = reduce_brightness(processed)

    # ---------------------------------------
    # Convert to grayscale
    # ---------------------------------------

    if len(processed.shape) == 3:
        processed = cv2.cvtColor(
            processed,
            cv2.COLOR_BGR2GRAY
        )

    # ---------------------------------------
    # CLAHE
    # ---------------------------------------

    if "clahe" in recommendations:
        print("✔ Applying CLAHE")
        processed = apply_clahe(processed)

    # ---------------------------------------
    # Denoise (Always)
    # ---------------------------------------

    print("✔ Removing noise")
    processed = denoise(processed)

    # ---------------------------------------
    # Sharpen
    # ---------------------------------------

    if "sharpen" in recommendations:
        print("✔ Sharpening image")
        processed = sharpen(processed)

    # ---------------------------------------
    # Adaptive Threshold
    # ---------------------------------------

    contrast = report["contrast"]["value"]

    if contrast < 20:
        print("✔ Applying adaptive threshold")
        processed = adaptive_threshold(processed)

    # ---------------------------------------
    # Morphology
    # ---------------------------------------

    processed = morphology(processed)

    return processed