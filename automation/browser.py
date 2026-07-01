from playwright.sync_api import sync_playwright
from config import HEADLESS


class BrowserManager:

    def __init__(self):
        self.playwright = None
        self.browser = None
        self.page = None

    def start(self):

        self.playwright = sync_playwright().start()

        self.browser = self.playwright.chromium.launch(
            headless=HEADLESS
        )

        self.page = self.browser.new_page(
            viewport={
                "width": 1600,
                "height": 900
            }
        )

        return self.page

    def close(self):

        if self.browser:
            self.browser.close()

        if self.playwright:
            self.playwright.stop()