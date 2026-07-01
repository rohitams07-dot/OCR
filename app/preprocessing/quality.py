import cv2
import numpy as np

from .utils import (
    to_grayscale,
    calculate_blur,
    calculate_brightness,
    calculate_contrast,
    image_resolution,
)


# ----------------------------
# Thresholds
# ----------------------------

LOW_RESOLUTION = 800          # width in pixels
LOW_BRIGHTNESS = 80
HIGH_BRIGHTNESS = 210

LOW_CONTRAST = 35

BLUR_THRESHOLD = 120


def analyze_image(image):
    """
    Analyze image quality and return OCR recommendations.
    """

    gray = to_grayscale(image)

    width, height = image_resolution(image)

    brightness = calculate_brightness(gray)
    contrast = calculate_contrast(gray)
    blur = calculate_blur(gray)

    report = {
        "resolution": {
            "width": width,
            "height": height,
            "status": "Good"
        },

        "brightness": {
            "value": round(brightness, 2),
            "status": "Good"
        },

        "contrast": {
            "value": round(contrast, 2),
            "status": "Good"
        },

        "blur": {
            "value": round(blur, 2),
            "status": "Sharp"
        },

        "recommendations": []
    }

    # ---------------------------------------
    # Resolution
    # ---------------------------------------

    if width < LOW_RESOLUTION:
        report["resolution"]["status"] = "Low"
        report["recommendations"].append("resize")

    # ---------------------------------------
    # Brightness
    # ---------------------------------------

    if brightness < LOW_BRIGHTNESS:
        report["brightness"]["status"] = "Dark"
        report["recommendations"].append("increase_brightness")

    elif brightness > HIGH_BRIGHTNESS:
        report["brightness"]["status"] = "Very Bright"

    # ---------------------------------------
    # Contrast
    # ---------------------------------------

    if contrast < LOW_CONTRAST:
        report["contrast"]["status"] = "Low"
        report["recommendations"].append("clahe")

    # ---------------------------------------
    # Blur
    # ---------------------------------------

    if blur < BLUR_THRESHOLD:
        report["blur"]["status"] = "Blurry"
        report["recommendations"].append("sharpen")

    # Remove duplicate recommendations

    report["recommendations"] = list(set(report["recommendations"]))

    return report


def print_quality_report(report):
    """
    Print image quality report.
    """

    print("\n==============================")
    print(" OCR IMAGE QUALITY REPORT")
    print("==============================")

    print(
        f"Resolution : "
        f"{report['resolution']['width']} x "
        f"{report['resolution']['height']} "
        f"({report['resolution']['status']})"
    )

    print(
        f"Brightness : "
        f"{report['brightness']['value']} "
        f"({report['brightness']['status']})"
    )

    print(
        f"Contrast   : "
        f"{report['contrast']['value']} "
        f"({report['contrast']['status']})"
    )

    print(
        f"Blur Score : "
        f"{report['blur']['value']} "
        f"({report['blur']['status']})"
    )

    print()

    if report["recommendations"]:
        print("Recommended Processing")

        for item in report["recommendations"]:
            print(f"  ✔ {item}")

    else:
        print("Image quality is already good.")

    print("==============================\n")




def check_image_quality(image_path: str):
    """
    Read the image from disk, analyze its quality,
    and return a result for the upload route.
    """

    image = cv2.imread(image_path)

    if image is None:
        return {
            "success": False,
            "message": "Unable to read the uploaded image."
        }

    report = analyze_image(image)

    # Decide whether the image passes quality checks.
    # You can adjust this logic later based on your requirements.
    success = (
        report["resolution"]["status"] == "Good"
        and report["brightness"]["status"] == "Good"
        and report["contrast"]["status"] == "Good"
        and report["blur"]["status"] == "Sharp"
    )

    return {
        "success": success,
        "message": "Image quality is good." if success else "Image quality is not sufficient.",
        "report": report
    }    