import json

from app.parser.geometry_matcher import match_labels


with open(
    "output/ocr_output.json",
    "r",
    encoding="utf-8"
) as f:

    ocr = json.load(f)


pairs = match_labels(ocr)

print("=" * 50)

print(f"TOTAL PAIRS : {len(pairs)}")

print("=" * 50)

for pair in pairs[:40]:

    print()

    print(pair["label"])

    print(" -> ")

    print(pair["value"])