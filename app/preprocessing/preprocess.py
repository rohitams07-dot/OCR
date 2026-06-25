import cv2
import os


def preprocess_image(input_path, output_path):

    image = cv2.imread(input_path)

    if image is None:
        raise Exception(f"Image not found: {input_path}")

    # Resize 2x
    image = cv2.resize(
        image,
        None,
        fx=2,
        fy=2,
        interpolation=cv2.INTER_CUBIC
    )

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Light denoising
    gray = cv2.fastNlMeansDenoising(gray)

    # CLAHE (better than equalizeHist for documents)
    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8)
    )

    processed = clahe.apply(gray)

    os.makedirs(
        os.path.dirname(output_path),
        exist_ok=True
    )

    cv2.imwrite(
        output_path,
        processed
    )

    print("Image saved:")
    print(output_path)


if __name__ == "__main__":

    preprocess_image(
        "uploads/sample.png.jpeg",
        "processed/sample_processed.png"
    )