import os
import requests


class ImageHandler:

    def __init__(self, page):
        self.page = page

    def capture(self):

        # Wait until iframe is available
        self.page.wait_for_selector("#MainContent_imageBox")

        frame = self.page.frame_locator("#MainContent_imageBox")

        img = frame.locator("#imageBox")

        img.wait_for()

        image_url = img.get_attribute("src")

        print("Image URL:", image_url)

        os.makedirs("automation/temp", exist_ok=True)

        image_path = "automation/temp/current_image.jpg"

        response = requests.get(image_url)

        response.raise_for_status()

        with open(image_path, "wb") as f:
            f.write(response.content)

        return image_path