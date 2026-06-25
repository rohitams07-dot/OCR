import json
import os


# -----------------------------------------
# Load OCR JSON
# -----------------------------------------
with open(
    "output/ocr_output.json",
    "r",
    encoding="utf-8"
) as f:
    ocr_data = json.load(f)


# -----------------------------------------
# Sort by Y then X
# -----------------------------------------
ocr_data.sort(
    key=lambda item: (
        item["bbox"][0][1],
        item["bbox"][0][0]
    )
)


# -----------------------------------------
# Detect Section Headers
# -----------------------------------------
def is_section(text):

    ignore = [
        "Full Name",
        "Gender",
        "DOB",
        "SSN",
        "Address",
        "Address 1",
        "Address 2",
        "City",
        "State",
        "Postal",
        "Country",
        "Email",
        "Contact",
        "Customer ID",
        "A/c Type",
        "A/c Name",
        "A/c Number",
        "IBAN",
        "BIC"
    ]

    if text in ignore:
        return False

    if len(text) > 5 and "Information" in text:
        return True

    if text.endswith("Manager"):
        return True

    if text.endswith("Advisor"):
        return True

    return False


# -----------------------------------------
# Group by Row
# -----------------------------------------
rows = []

threshold = 15

for item in ocr_data:

    y = item["bbox"][0][1]

    found = False

    for row in rows:

        if abs(row["y"] - y) <= threshold:

            row["items"].append(item)

            found = True

            break

    if not found:

        rows.append({

            "y": y,

            "items": [item]

        })


# -----------------------------------------
# Sort every row by X
# -----------------------------------------
for row in rows:

    row["items"].sort(
        key=lambda x: x["bbox"][0][0]
    )


# -----------------------------------------
# Build Final JSON
# -----------------------------------------
final_json = {}

current_section = "General"

final_json[current_section] = {}

for row in rows:

    items = row["items"]

    if len(items) == 0:
        continue

    first = items[0]["text"]

    # Detect Section
    if len(items) == 1 and is_section(first):

        current_section = first

        final_json[current_section] = {}

        continue

    # Label -> Value
    if len(items) >= 2:

        label = items[0]["text"]

        value = " ".join(
            item["text"]
            for item in items[1:]
        )

        final_json[current_section][label] = value

    elif len(items) == 1:

        final_json[current_section][first] = ""


# -----------------------------------------
# Save Output
# -----------------------------------------
os.makedirs(
    "output",
    exist_ok=True
)

with open(
    "output/final_output.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        final_json,
        f,
        indent=4,
        ensure_ascii=False
    )


print("=" * 50)
print("Parsing Completed")
print("=" * 50)
print(json.dumps(final_json, indent=4))