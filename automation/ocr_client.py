import requests
from pathlib import Path


class OCRClient:
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.extract_url = f"{base_url}/extract"

    def extract(self, image_path: str):
        """
        Send image to FastAPI OCR backend.

        Args:
            image_path (str): Local path of the image.

        Returns:
            dict: JSON response from OCR API.
        """

        image_file = Path(image_path)

        if not image_file.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        with open(image_file, "rb") as file:

            files = {
                "file": (
                    image_file.name,
                    file,
                    "image/png"
                )
            }

            response = requests.post(
                self.extract_url,
                files=files,
                timeout=300
            )

        if response.status_code != 200:
            raise Exception(
                f"OCR API Error ({response.status_code})\n"
                f"{response.text}"
            )

        return response.json()