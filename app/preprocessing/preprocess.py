# import cv2
# import os


# def preprocess_image(input_path: str, output_path: str) -> str:
#     """
#     Preprocess the uploaded image for OCR.
#     Returns the processed image path.
#     """

#     image = cv2.imread(input_path)

#     if image is None:
#         raise FileNotFoundError(f"Image not found: {input_path}")

#     # Add white border/padding of 20 pixels all around
#     image = cv2.copyMakeBorder(
#         image,
#         20,
#         20,
#         20,
#         20,
#         cv2.BORDER_CONSTANT,
#         value=[255, 255, 255]
#     )

#     # Resize
#     image = cv2.resize(
#         image,
#         None,
#         fx=2,
#         fy=2,
#         interpolation=cv2.INTER_CUBIC
#     )

#     # Convert to grayscale
#     gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

#     # CLAHE
#     clahe = cv2.createCLAHE(
#         clipLimit=2.0,
#         tileGridSize=(8, 8)
#     )

#     processed = clahe.apply(gray)

#     os.makedirs(os.path.dirname(output_path), exist_ok=True)

#     cv2.imwrite(output_path, processed)

#     print(f"Processed image saved: {output_path}")

#     return output_path


# if __name__ == "__main__":
#     preprocess_image("uploads/sample.png.jpeg", "processed/processed.png")



import os
import cv2

from .utils import (
    add_border,
    save_image,
)

from .quality import (
    analyze_image,
)

from .deskew_utils import (
    auto_deskew,
    print_deskew_report,
)

from .enhancement import (
    enhance_image,
)

from .report import (
    print_final_report,
)


def preprocess_image(
    input_path: str,
    output_path: str
) -> str:
    """
    Adaptive OCR preprocessing pipeline.

    Flow

    Read Image
        ↓
    Analyze Image
        ↓
    Print Report
        ↓
    Deskew
        ↓
    Enhance Image
        ↓
    Add Border
        ↓
    Save Image
    """

    # ----------------------------------
    # Read Image
    # ----------------------------------

    image = cv2.imread(input_path)

    if image is None:
        raise FileNotFoundError(
            f"Image not found: {input_path}"
        )

    print("\nReading Image...")

    # ----------------------------------
    # Analyze Image Quality
    # ----------------------------------

    report = analyze_image(image)

    print_final_report(report)

    # ----------------------------------
    # Deskew
    # ----------------------------------

    image, angle = auto_deskew(image)

    print_deskew_report(angle)

    # ----------------------------------
    # Adaptive Enhancement
    # ----------------------------------

    image = enhance_image(image, report)

    # ----------------------------------
    # Add White Border
    # ----------------------------------

    image = add_border(
        image,
        border_size=20
    )

    # ----------------------------------
    # Save
    # ----------------------------------

    os.makedirs(
        os.path.dirname(output_path),
        exist_ok=True
    )

    save_image(
        image,
        output_path
    )

    print(f"Processed image saved to:\n{output_path}")

    return output_path


if __name__ == "__main__":

    preprocess_image(
        "uploads/sample.jpeg",
        "processed/processed.png"
    )