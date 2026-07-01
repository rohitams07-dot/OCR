import json


class MappingGenerator:

    def __init__(self, page):
        self.page = page

    def generate(self):

        tabs = [
            "Personal Information",
            "Account Information",
            "Investment Information",
            "Assets Information",
            "Legal Advisors"
        ]

        mapping = {}

        for tab in tabs:

            print(f"\nOpening {tab}")

            self.page.get_by_text(tab, exact=True).click()

            self.page.wait_for_timeout(1000)

            labels = self.page.locator("td")

            divs = self.page.locator("div.input[contenteditable='true']")

            tab_map = {}

            count = min(labels.count(), divs.count())

            for i in range(count):

                try:

                    label = labels.nth(i).inner_text().strip()

                    if not label:
                        continue

                    field_id = divs.nth(i).get_attribute("id")

                    tab_map[label] = "#" + field_id

                except:
                    pass

            mapping[tab] = tab_map

        with open("automation/field_mapping.json", "w") as f:

            json.dump(mapping, f, indent=4)

        print("\nDone.")