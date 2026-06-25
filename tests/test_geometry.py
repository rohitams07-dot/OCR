import json

from app.parser.geometry import OCRBox
from app.parser.geometry import is_same_row
from app.parser.geometry import vertical_distance


with open(
    "output/ocr_output.json",
    "r",
    encoding="utf-8"
) as f:

    data = json.load(f)


boxes = [OCRBox(item) for item in data]


print("=" * 50)

print("TOTAL BOXES:", len(boxes))

print("=" * 50)


for box in boxes[:10]:

    print()

    print(box.text)

    print("Left :", box.left)

    print("Right:", box.right)

    print("Top  :", box.top)

    print("Bottom:", box.bottom)

    print("Center:", box.center_x, box.center_y)