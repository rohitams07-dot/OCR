# from automation.browser import BrowserManager
# from automation.login import LoginService
# from automation.image_handler import ImageHandler
# from automation.ocr_client import OCRClient
# from automation.form_filler import FormFiller


# def main():

#     browser = BrowserManager()

#     page = browser.start()

#     LoginService(page).login()

#     input(
#         "\nSelect Operational Day and Image.\n"
#         "Press ENTER after image is loaded..."
#     )

#     image_path = ImageHandler(page).capture()

#     print("Captured:", image_path)

#     json_data = OCRClient().extract(image_path)

#     print(json_data)

#     FormFiller(page).fill(json_data)

#     input("\nCompleted. Press ENTER to exit.")

#     browser.close()


# if __name__ == "__main__":
#     main()

from automation.browser import BrowserManager
from automation.login import LoginService
from automation.image_handler import ImageHandler
from automation.ocr_client import OCRClient
from automation.form_filler import FormFiller


def main():

    browser = BrowserManager()
    page = browser.start()

    try:
        # Step 1 - Login
        LoginService(page).login()

        input(
            "\nSelect the Operational Day and Raw Image.\n"
            "After the image is fully loaded, press ENTER..."
        )

        # Step 2 - Capture Image
        print("\n========== STEP 1 ==========")
        print("Capturing image...")

        image_path = ImageHandler(page).capture()

        print(f"Image saved at: {image_path}")

        # Step 3 - OCR API
        print("\n========== STEP 2 ==========")
        print("Calling OCR Backend...")

        ocr_client = OCRClient()

        json_data = ocr_client.extract(image_path)

        print("OCR completed successfully.\n")

        print("OCR JSON:")
        print(json_data)

        # Step 4 - Fill Form
        print("\n========== STEP 3 ==========")
        print("Filling form...")

        filler = FormFiller(page)
        filler.fill(json_data)

        print("\nAutomation Completed Successfully.")

        input("\nPress ENTER to close browser...")

    except Exception as e:

        print("\nERROR OCCURRED")
        print(type(e).__name__)
        print(e)

        input("\nPress ENTER to close browser...")

    finally:
        browser.close()


if __name__ == "__main__":
    main()