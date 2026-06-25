import json

from row_detector import detect_rows


with open(
    "output/ocr_output.json",
    "r",
    encoding="utf-8"
) as f:

    ocr = json.load(f)


rows = detect_rows(ocr)

print("=" * 50)

print(f"TOTAL ROWS : {len(rows)}")

print("=" * 50)


for i, row in enumerate(rows):

    print()

    print(f"ROW {i+1}")

    print("-" * 40)

    for item in row["items"]:

        print(item["text"])