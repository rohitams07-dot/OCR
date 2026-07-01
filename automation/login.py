from config import (
    CLIENT_URL,
    CLIENT_USERNAME,
    CLIENT_PASSWORD,
)


class LoginService:

    def __init__(self, page):
        self.page = page

    def login(self):

        print("Opening Login Page...")

        self.page.goto(CLIENT_URL)

        self.page.wait_for_load_state("networkidle")

        print("Entering Username...")

        self.page.fill("#username", CLIENT_USERNAME)

        print("Entering Password...")

        self.page.fill("#password", CLIENT_PASSWORD)

        print("Clicking Login...")

        self.page.click("#btnLogin")

        self.page.wait_for_load_state("networkidle")

        print("Login Successful")