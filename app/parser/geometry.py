"""
geometry.py

Utilities for working with OCR bounding boxes.
"""

from math import sqrt


class OCRBox:

    def __init__(self, item):

        self.text = item["text"]

        self.confidence = item["confidence"]

        self.bbox = item["bbox"]

        self.left = min(p[0] for p in self.bbox)
        self.right = max(p[0] for p in self.bbox)

        self.top = min(p[1] for p in self.bbox)
        self.bottom = max(p[1] for p in self.bbox)

        self.width = self.right - self.left
        self.height = self.bottom - self.top

        self.center_x = (self.left + self.right) / 2
        self.center_y = (self.top + self.bottom) / 2


def vertical_overlap(box1, box2):

    top = max(box1.top, box2.top)

    bottom = min(box1.bottom, box2.bottom)

    return max(0, bottom - top)


def horizontal_distance(box1, box2):

    return abs(box1.left - box2.right)


def vertical_distance(box1, box2):

    return abs(box1.center_y - box2.center_y)


def euclidean_distance(box1, box2):

    return sqrt(

        (box1.center_x - box2.center_x) ** 2 +

        (box1.center_y - box2.center_y) ** 2

    )


def is_same_row(box1, box2, threshold=15):

    return abs(box1.center_y - box2.center_y) <= threshold


def is_right_of(box1, box2):

    return box2.left > box1.right


def is_below(box1, box2):

    return box2.top > box1.bottom