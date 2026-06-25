"""
row_detector.py

Groups OCR detections into rows using Y-coordinate clustering.
"""

from typing import List


ROW_THRESHOLD = 15


def get_y(item):
    """
    Returns top-left Y coordinate.
    """
    return item["bbox"][0][1]


def get_x(item):
    """
    Returns top-left X coordinate.
    """
    return item["bbox"][0][0]


def detect_rows(ocr_data: List[dict]):

    # Sort by Y then X
    ocr_data = sorted(
        ocr_data,
        key=lambda x: (
            get_y(x),
            get_x(x)
        )
    )

    rows = []

    for item in ocr_data:

        y = get_y(item)

        found = False

        for row in rows:

            if abs(row["y"] - y) <= ROW_THRESHOLD:

                row["items"].append(item)

                found = True

                break

        if not found:

            rows.append({

                "y": y,

                "items": [item]

            })

    # Sort every row by X
    for row in rows:

        row["items"] = sorted(
            row["items"],
            key=get_x
        )

    return rows