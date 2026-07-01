from automation.field_mapper import (
    PERSONAL_INFORMATION,
    ACCOUNT_INFORMATION,
    INVESTMENT_INFORMATION,
    ASSETS_INFORMATION,
    LEGAL_ADVISORS,
)


class FormFiller:

    def __init__(self, page):
        self.page = page

    # ----------------------------
    # Set value into editable div
    # ----------------------------

    def set_value(self, selector, value):

        if value is None:
            return

        value = str(value).strip()

        if not value:
            return

        locator = self.page.locator(selector)

        locator.wait_for(state="visible")

        locator.click()

        self.page.keyboard.press("Control+A")
        self.page.keyboard.press("Backspace")

        locator.evaluate(
            "(el, v) => {"
            "  el.focus();"
            "  el.textContent = '';"
            "  document.execCommand('insertText', false, v);"
            "  el.dispatchEvent(new Event('input', {bubbles:true}));"
            "  el.dispatchEvent(new Event('change', {bubbles:true}));"
            "  el.dispatchEvent(new Event('blur', {bubbles:true}));"
            "}",
            value,
        )

        self.page.keyboard.press("Tab")

    # ----------------------------
    # Fill Record ID
    # ----------------------------

    def fill_record_id(self, record_id):

        if not record_id:
            return

        locator = self.page.locator("#MainContent_i100")

        if locator.count() > 0:
            self.set_value("#MainContent_i100", record_id)
    # ----------------------------
    # OCR Key Normalizer
    # ----------------------------

    def normalize(self, data):

        result = {}

        for key, value in data.items():

            key = key.strip()

            if key.startswith("Skll Description"):
                key = "Skll Description"

            elif key.startswith("Maturity Date"):
                key = "Maturity Date"

            elif key == "Buying IPV4":
                key = "Buying IPv4"

            elif key == "Buying IPv6":
                key = "Buying IPV6"

            elif key == "Beneficiary Identifier ID":
                key = "Beneficiary"

           # Keep Address unchanged for Legal Advisors
            elif key == "Address":
                result[key] = value
                continue

            result[key] = value

        return result

    # ----------------------------
    # Fill one section
    # ----------------------------

    def fill_section(self, mapping, section):

        section = self.normalize(section)

        print("\n============================")
        print("OCR SECTION")
        print(section)
        print("============================\n")

        for field, selector in mapping.items():

            value = section.get(field)

            print(f"Field    : {field}")
            print(f"Selector : {selector}")
            print(f"Value    : {value}")
            print("--------------------------------")

            if value:

                self.set_value(selector, value)

    # ----------------------------
    # Fill Legal Advisors
    # ----------------------------

    def fill_legal(self, ocr_json):

        for group, mapping in LEGAL_ADVISORS.items():

            print(f"\n{group}")

            data = ocr_json.get(group, {})

            self.fill_section(mapping, data)

    # ----------------------------
    # Main
    # ----------------------------

    def fill(self, ocr_json):

        record_id = ocr_json.get("Record ID", "")

        print("\nOpening Personal Information")

        self.page.get_by_text(
            "Personal Information",
            exact=True,
        ).click()

        self.page.wait_for_timeout(500)

        self.fill_section(
            PERSONAL_INFORMATION,
            ocr_json.get("Personal Information", {}),
        )

        self.fill_record_id(record_id)

        print("\nOpening Account Information")

        self.page.get_by_text(
            "Account Information",
            exact=True,
        ).click()

        self.page.wait_for_timeout(500)

        self.fill_section(
            ACCOUNT_INFORMATION,
            ocr_json.get("Account Information", {}),
        )

        self.fill_record_id(record_id)

        print("\nOpening Investment Information")

        self.page.get_by_text(
            "Investment Information",
            exact=True,
        ).click()

        self.page.wait_for_timeout(500)

        self.fill_section(
            INVESTMENT_INFORMATION,
            ocr_json.get("Investment Information", {}),
        )

        self.fill_record_id(record_id)

        print("\nOpening Assets Information")

        self.page.get_by_text(
            "Assets Information",
            exact=True,
        ).click()

        self.page.wait_for_timeout(500)

        assets_data = {}
        assets_data.update(ocr_json.get("Assets & Last Purchase Information", {}))
        assets_data.update(ocr_json.get("Vehicle Detail", {}))
        assets_data.update(ocr_json.get("Vehicle", {}))
        assets_data.update(ocr_json.get("Insurance Detail", {}))
        assets_data.update(ocr_json.get("Insurance", {}))
        self.fill_section(
            ASSETS_INFORMATION,
            assets_data,
        )

        self.fill_record_id(record_id)

        print("\nOpening Legal Advisors")

        self.page.get_by_text(
            "Legal Advisors",
            exact=True,
        ).click()

        self.page.wait_for_timeout(500)

        self.fill_legal(ocr_json)

        self.fill_record_id(record_id)

        print("\nAll Sections Completed.")