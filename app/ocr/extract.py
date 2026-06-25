from paddleocr import PaddleOCR
import json
import os

# Initialize OCR
ocr = PaddleOCR(
    use_angle_cls=True,
    lang="en"
)

# Run OCR
result = ocr.ocr(
    "processed/sample_processed.png",
    cls=True
)

ocr_output = []

for page in result:

    for line in page:

        bbox = line[0]

        text = line[1][0]

        confidence = float(line[1][1])

        ocr_output.append({
            "text": text,
            "bbox": bbox,
            "confidence": confidence
        })

# Create output folder
os.makedirs("output", exist_ok=True)

# Save JSON
with open(
    "output/ocr_output.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        ocr_output,
        f,
        indent=4,
        ensure_ascii=False
    )

print("OCR Extraction Completed")
print(f"Total OCR Items : {len(ocr_output)}")
print("Saved : output/ocr_output.json")