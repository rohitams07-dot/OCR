from fastapi import APIRouter, UploadFile, File, HTTPException
import shutil
import os
import json
from app.preprocessing.preprocess import preprocess_image
from app.ocr.extract import run_ocr
from app.parser.parser import parse_document

router = APIRouter()

UPLOAD_DIR = "uploads"
PROCESSED_DIR = "processed"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)


# @router.post("/extract")
# async def extract(file: UploadFile = File(...)):

#     upload_path = os.path.join(
#         UPLOAD_DIR,
#         file.filename
#     )

#     try:
#         with open(upload_path, "wb") as buffer:
#             shutil.copyfileobj(file.file, buffer)
            
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"File save failed: {e}")

#     processed_path = os.path.join(
#         PROCESSED_DIR,
#         "processed.png"
#     )

#     try:
#         preprocess_image(upload_path, processed_path)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Preprocessing failed: {e}")

#     try:
#         ocr_json_path = run_ocr(processed_path)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"OCR failed: {e}")

#     try:
#         parsed_json = parse_document(ocr_json_path)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Parsing failed: {e}")

#     return parsed_json

@router.post("/extract")
async def extract(file: UploadFile = File(...)):

    upload_path = os.path.join(
        UPLOAD_DIR,
        file.filename
    )

    # Save uploaded file
    try:
        with open(upload_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"File save failed: {e}"
        )

    processed_path = os.path.join(
        PROCESSED_DIR,
        "processed.png"
    )

    # Preprocessing
    try:
        preprocess_image(upload_path, processed_path)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Preprocessing failed: {e}"
        )

    # OCR
    try:
        ocr_json_path = run_ocr(processed_path)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"OCR failed: {e}"
        )

    # Parsing
    try:
        parsed_json = parse_document(ocr_json_path)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Parsing failed: {e}"
        )

    return parsed_json


@router.get("/result")
async def get_result():

    result_path = os.path.join(
        "output",
        "final_output.json"
    )

    if not os.path.exists(result_path):
        raise HTTPException(
            status_code=404,
            detail="No OCR result found. Please upload an image first."
        )

    with open(
        result_path,
        "r",
        encoding="utf-8"
    ) as f:
        data = json.load(f)

    return data