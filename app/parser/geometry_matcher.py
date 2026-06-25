"""
geometry_matcher.py

Matches labels with values using OCR geometry.
"""

from app.parser.geometry import (
    OCRBox,
    is_same_row,
)


def match_labels(ocr_data):

    boxes = [OCRBox(item) for item in ocr_data]

    results = []

    for label in boxes:

        nearest = None

        nearest_distance = float("inf")

        for value in boxes:

            if value == label:
                continue

            # Must be on same row
            if not is_same_row(label, value):
                continue

            # Value must be on right
            if value.left <= label.right:
                continue

            distance = value.left - label.right

            if distance < nearest_distance:

                nearest_distance = distance

                nearest = value

        if nearest:

            results.append({

                "label": label.text,

                "value": nearest.text,

                "distance": nearest_distance

            })

    return results