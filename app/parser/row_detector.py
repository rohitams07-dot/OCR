# """
# row_detector.py

# Groups OCR detections into rows using Y-coordinate clustering.
# """

# from typing import List


# ROW_THRESHOLD = 15


# def get_y(item):
#     """
#     Returns top-left Y coordinate.
#     """
#     return item["bbox"][0][1]


# def get_x(item):
#     """
#     Returns top-left X coordinate.
#     """
#     return item["bbox"][0][0]


# def detect_rows(ocr_data: List[dict]):

#     # Sort by Y then X
#     ocr_data = sorted(
#         ocr_data,
#         key=lambda x: (
#             get_y(x),
#             get_x(x)
#         )
#     )

#     rows = []

#     for item in ocr_data:

#         y = get_y(item)

#         found = False

#         for row in rows:

#             if abs(row["y"] - y) <= ROW_THRESHOLD:

#                 row["items"].append(item)

#                 found = True

#                 break

#         if not found:

#             rows.append({

#                 "y": y,

#                 "items": [item]

#             })

#     # Sort every row by X
#     for row in rows:

#         row["items"] = sorted(
#             row["items"],
#             key=get_x
#         )

#     return rows




"""
row_detector.py

Groups OCR detections into rows using Y-coordinate clustering.
"""

from typing import List

# Minimum row threshold (pixels)
MIN_ROW_THRESHOLD = 15


def get_x(item):
    """
    Returns top-left X coordinate.
    """
    return item["bbox"][0][0]


def get_center_y(item):
    """
    Returns vertical center of OCR box.
    """
    bbox = item["bbox"]

    top = bbox[0][1]
    bottom = bbox[2][1]

    return (top + bottom) / 2


def get_height(item):
    """
    Returns height of OCR box.
    """
    bbox = item["bbox"]

    return abs(bbox[2][1] - bbox[0][1])


def detect_rows(ocr_data: List[dict]):
    """
    Group OCR detections into rows.

    Returns:
    [
        {
            "center_y": float,
            "avg_height": float,
            "items": [...]
        },
        ...
    ]
    """

    if not ocr_data:
        return []

    # -----------------------------------------
    # Sort by vertical center then X
    # -----------------------------------------

    ocr_data = sorted(
        ocr_data,
        key=lambda item: (
            get_center_y(item),
            get_x(item)
        )
    )

    rows = []

    # -----------------------------------------
    # Group into rows
    # -----------------------------------------

    for item in ocr_data:

        center_y = get_center_y(item)
        height = get_height(item)

        matched = False

        for row in rows:

            threshold = max(
                MIN_ROW_THRESHOLD,
                row["avg_height"] * 0.6
            )

            if abs(row["center_y"] - center_y) <= threshold:

                row["items"].append(item)

                # Update average center
                row["center_y"] = (
                    row["center_y"] * (len(row["items"]) - 1)
                    + center_y
                ) / len(row["items"])

                # Update average height
                row["avg_height"] = (
                    row["avg_height"] * (len(row["items"]) - 1)
                    + height
                ) / len(row["items"])

                matched = True
                break

        if not matched:

            rows.append({
                "center_y": center_y,
                "avg_height": height,
                "items": [item]
            })

    # -----------------------------------------
    # Sort each row by X
    # -----------------------------------------

    for row in rows:

        row["items"] = sorted(
            row["items"],
            key=get_x
        )

    return rows