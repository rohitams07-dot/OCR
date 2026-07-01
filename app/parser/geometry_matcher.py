# """
# geometry_matcher.py

# Matches labels with values using OCR geometry.
# """

# from app.parser.geometry import (
#     OCRBox,
#     is_same_row,
# )


# def match_labels(ocr_data):

#     boxes = [OCRBox(item) for item in ocr_data]

#     results = []

#     for label in boxes:

#         nearest = None

#         nearest_distance = float("inf")

#         for value in boxes:

#             if value == label:
#                 continue

#             # Must be on same row
#             if not is_same_row(label, value):
#                 continue

#             # Value must be on right
#             if value.left <= label.right:
#                 continue

#             distance = value.left - label.right

#             if distance < nearest_distance:

#                 nearest_distance = distance

#                 nearest = value

#         if nearest:

#             results.append({

#                 "label": label.text,

#                 "value": nearest.text,

#                 "distance": nearest_distance

#             })

#     return results




"""
geometry_matcher.py

Matches labels with values using OCR geometry.
"""

from app.parser.geometry import (
    OCRBox,
    is_same_row,
)


# Maximum horizontal search distance (pixels)
MAX_HORIZONTAL_DISTANCE = 600


def match_labels(ocr_data):
    """
    Match each label with the nearest value using OCR geometry.

    Returns:
    [
        {
            "label": "...",
            "value": "...",
            "distance": 45
        }
    ]
    """

    boxes = [OCRBox(item) for item in ocr_data]

    results = []

    used_values = set()

    for label in boxes:

        nearest = None
        best_score = float("inf")

        for value in boxes:

            if value == label:
                continue

            if id(value) in used_values:
                continue

            # Must belong to same row
            if not is_same_row(label, value):
                continue

            # Value must be on the right
            if value.left <= label.right:
                continue

            horizontal_distance = value.left - label.right

            # Ignore values that are too far away
            if horizontal_distance > MAX_HORIZONTAL_DISTANCE:
                continue

            vertical_offset = abs(
                label.center_y - value.center_y
            )

            # Weighted score
            score = horizontal_distance + (vertical_offset * 3)

            if score < best_score:

                best_score = score
                nearest = value

        if nearest:

            used_values.add(id(nearest))

            results.append({

                "label": label.text,

                "value": nearest.text,

                "distance": round(best_score, 2)

            })

    return results