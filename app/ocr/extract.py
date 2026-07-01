from paddleocr import PaddleOCR
import json
import os
from pprint import pprint

# Load OCR model once.
# enable_mkldnn=False  — disables OneDNN/MKL-DNN (avoids ConvertPirAttribute crash)
# use_angle_cls=False  — skips angle classifier (upright documents don't need it)
# det_db_score_mode    — 'fast' uses box mean score instead of poly mean (much faster)
# limit_side_len       — cap longest side at 1280px (image is already 2x upscaled)

import inspect

try:
    init_params = inspect.signature(PaddleOCR.__init__).parameters
except Exception:
    init_params = {}

kwargs = {}
if "lang" in init_params:
    kwargs["lang"] = "en"

if "text_det_limit_side_len" in init_params:
    # New PaddleOCR 2.8+ / Paddlex style parameters
    kwargs["ocr_version"] = "PP-OCRv4"
    kwargs["text_det_limit_side_len"] = 1280
    kwargs["text_det_unclip_ratio"] = 1.6
    kwargs["use_textline_orientation"] = False
    kwargs["enable_mkldnn"] = False
    kwargs["use_doc_orientation_classify"] = False
    kwargs["use_doc_unwarping"] = False
else:
    # Legacy parameters
    kwargs["ocr_version"] = "PP-OCRv4"
    if "enable_mkldnn" in init_params:
        kwargs["enable_mkldnn"] = False
    if "use_angle_cls" in init_params:
        kwargs["use_angle_cls"] = False
    if "det_db_score_mode" in init_params:
        kwargs["det_db_score_mode"] = "fast"
    if "det_db_unclip_ratio" in init_params:
        kwargs["det_db_unclip_ratio"] = 1.6
    if "limit_side_len" in init_params:
        kwargs["limit_side_len"] = 1280

ocr = PaddleOCR(**kwargs)


def run_ocr(image_path: str) -> str:
    """
    Run PaddleOCR on the image, convert the result to structured JSON,
    and return the path to the JSON file for the parser.
    """

    if hasattr(ocr, "predict"):
        result = ocr.predict(image_path)
    else:
        result = ocr.ocr(image_path, cls=False)

    os.makedirs("output", exist_ok=True)

    # Save raw result for debugging
    raw_output = os.path.join("output", "raw_ocr_result.txt")
    with open(raw_output, "w", encoding="utf-8") as f:
        f.write(str(result))
    print("Raw OCR result saved to:", raw_output)

    structured = []

    for page in (result or []):
        if not page:
            continue
        if hasattr(page, 'keys') and 'rec_texts' in page:
            # New PaddleOCR v2.8.x format (OCRResult object)
            texts = page.get('rec_texts', [])
            scores = page.get('rec_scores', [])
            polys = page.get('dt_polys', [])
            for i in range(len(texts)):
                try:
                    text = texts[i]
                    conf = scores[i]
                    bbox_raw = polys[i]
                    bbox = _normalise_bbox(bbox_raw)
                    structured.append({
                        "text": str(text),
                        "bbox": bbox,
                        "confidence": float(conf)
                    })
                except Exception as e:
                    print(f"Skipping malformed item at index {i}: {e}")
        else:
            # Old PaddleOCR 2.x format: list of [bbox, (text, conf)]
            for line in page:
                if line is None:
                    continue
                try:
                    bbox_raw, (text, conf) = line
                    bbox = _normalise_bbox(bbox_raw)
                    structured.append({
                        "text": str(text),
                        "bbox": bbox,
                        "confidence": float(conf)
                    })
                except Exception as e:
                    print(f"Skipping malformed line: {line!r} — {e}")

    # Save structured JSON
    json_output = os.path.join("output", "ocr_output.json")
    with open(json_output, "w", encoding="utf-8") as f:
        json.dump(structured, f, indent=4, ensure_ascii=False)

    print(f"Structured OCR JSON saved to: {json_output} ({len(structured)} items)")
    return json_output


def _normalise_bbox(bbox_raw):
    """
    Normalise various bbox formats to [[x,y],[x,y],[x,y],[x,y]] (4-point polygon).
    Handles: list of [x,y] pairs, flat list of 8 coords, numpy arrays, etc.
    """
    try:
        import numpy as np
        if isinstance(bbox_raw, np.ndarray):
            bbox_raw = bbox_raw.tolist()
    except ImportError:
        pass

    if not bbox_raw:
        return [[0, 0], [0, 0], [0, 0], [0, 0]]

    # Already [[x,y], [x,y], [x,y], [x,y]]
    if isinstance(bbox_raw[0], (list, tuple)) and len(bbox_raw) == 4:
        return [[float(p[0]), float(p[1])] for p in bbox_raw]

    # Flat list of 8 values [x1,y1,x2,y2,x3,y3,x4,y4]
    if isinstance(bbox_raw[0], (int, float)) and len(bbox_raw) == 8:
        coords = [float(v) for v in bbox_raw]
        return [
            [coords[0], coords[1]],
            [coords[2], coords[3]],
            [coords[4], coords[5]],
            [coords[6], coords[7]],
        ]

    # [x_min, y_min, x_max, y_max] rectangle
    if isinstance(bbox_raw[0], (int, float)) and len(bbox_raw) == 4:
        x1, y1, x2, y2 = [float(v) for v in bbox_raw]
        return [[x1, y1], [x2, y1], [x2, y2], [x1, y2]]

    # Nested list of more than 4 points — take first 4
    if isinstance(bbox_raw[0], (list, tuple)):
        return [[float(p[0]), float(p[1])] for p in bbox_raw[:4]]

    return [[0, 0], [0, 0], [0, 0], [0, 0]]


if __name__ == "__main__":
    run_ocr("processed/processed.png")