import cv2
import numpy as np
from deskew import determine_skew


def get_skew_angle(gray_image: np.ndarray) -> float:
    """
    Detect the skew angle of the image.

    Returns:
        float: Skew angle in degrees.
    """
    try:
        angle = determine_skew(gray_image)

        if angle is None:
            return 0.0

        return float(angle)

    except Exception:
        return 0.0


def rotate_image(image: np.ndarray, angle: float) -> np.ndarray:
    """
    Rotate image while keeping the entire image visible.

    Args:
        image: Input image.
        angle: Rotation angle.

    Returns:
        Rotated image.
    """

    h, w = image.shape[:2]

    center = (w // 2, h // 2)

    matrix = cv2.getRotationMatrix2D(center, angle, 1.0)

    cos = abs(matrix[0, 0])
    sin = abs(matrix[0, 1])

    new_w = int((h * sin) + (w * cos))
    new_h = int((h * cos) + (w * sin))

    matrix[0, 2] += (new_w / 2) - center[0]
    matrix[1, 2] += (new_h / 2) - center[1]

    rotated = cv2.warpAffine(
        image,
        matrix,
        (new_w, new_h),
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=(255, 255, 255)
    )

    return rotated


def auto_deskew(image: np.ndarray):
    """
    Automatically deskew image.

    Returns:
        processed_image,
        detected_angle
    """

    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()

    angle = get_skew_angle(gray)

    # Ignore tiny rotations
    if abs(angle) < 1.0:
        return image, angle

    corrected = rotate_image(image, angle)

    return corrected, angle


def print_deskew_report(angle: float):
    """
    Print deskew information.
    """

    print("\n------------------------------")
    print("DESKEW REPORT")
    print("------------------------------")

    print(f"Detected Rotation : {angle:.2f}°")

    if abs(angle) < 1.0:
        print("Deskew            : Not Required")
    else:
        print("Deskew            : Applied")

    print("------------------------------\n")