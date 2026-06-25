"""
label_matcher.py

Creates Label -> Value pairs
"""

import re


# ----------------------------
# Regex Patterns
# ----------------------------

NUMBER_PATTERN = r"\d+(?:\.\d+)?"

DATE_PATTERN = r"\d{2}-\d{2}-\d{2,4}"

PHONE_PATTERN = r"\+?\d[\d\-\sxX()]{6,}"

EMAIL_PATTERN = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"


def split_label_value(text):

    text = text.strip()

    # ------------------------
    # Email
    # ------------------------

    email = re.search(
        EMAIL_PATTERN,
        text
    )

    if email:

        value = email.group()

        label = text.replace(
            value,
            ""
        ).strip()

        return label, value

    # ------------------------
    # Phone
    # ------------------------

    phone = re.search(
        PHONE_PATTERN,
        text
    )

    if phone:

        value = phone.group()

        label = text.replace(
            value,
            ""
        ).strip()

        return label, value

    # ------------------------
    # Date
    # ------------------------

    date = re.search(
        DATE_PATTERN,
        text
    )

    if date:

        value = date.group()

        label = text.replace(
            value,
            ""
        ).strip()

        return label, value

    # ------------------------
    # Number at End
    # ------------------------

    number = re.search(
        NUMBER_PATTERN + r"$",
        text
    )

    if number:

        value = number.group()

        label = text.replace(
            value,
            ""
        ).strip()

        return label, value

    return text, ""