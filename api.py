import json
import os
import shutil
import subprocess

from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# -------------------------------------------------
# Paths
# -------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

import sys

PYTHON = sys.executable

print("BASE_DIR :", BASE_DIR)
print("PYTHON   :", PYTHON)
print("Exists   :", os.path.exists(PYTHON))

PIPELINE = [
    "app/preprocessing/preprocess.py",
    "app/ocr/extract.py",
    "app/parser/parser.py",
]


# -------------------------------------------------
# API
# -------------------------------------------------

@app.post("/extract")
async def extract(file: UploadFile):

    upload_path = os.path.join(
        BASE_DIR,
        "uploads",
        "sample.png.jpeg"
    )

    output_json = os.path.join(
        BASE_DIR,
        "output",
        "final_output.json"
    )

    os.makedirs(
        os.path.dirname(upload_path),
        exist_ok=True
    )

    with open(upload_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    for script in PIPELINE:

        proc = subprocess.run(
            [PYTHON, script],
            cwd=BASE_DIR,
            capture_output=True,
            text=True
        )

        print(f"\nRunning : {script}")
        print(proc.stdout)

        if proc.returncode != 0:

            print(proc.stderr)

            raise HTTPException(
                status_code=500,
                detail=proc.stderr
            )

    with open(
        output_json,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)