# """
# label_matcher.py

# Creates Label -> Value pairs
# """

# import re


# # ----------------------------
# # Regex Patterns
# # ----------------------------

# NUMBER_PATTERN = r"\d+(?:\.\d+)?"

# DATE_PATTERN = r"\d{2}-\d{2}-\d{2,4}"

# PHONE_PATTERN = r"\+?\d[\d\-\sxX()]{6,}"

# EMAIL_PATTERN = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"


# def split_label_value(text):

#     text = text.strip()

#     # ------------------------
#     # Email
#     # ------------------------

#     email = re.search(
#         EMAIL_PATTERN,
#         text
#     )

#     if email:

#         value = email.group()

#         label = text.replace(
#             value,
#             ""
#         ).strip()

#         return label, value

#     # ------------------------
#     # Phone
#     # ------------------------

#     phone = re.search(
#         PHONE_PATTERN,
#         text
#     )

#     if phone:

#         value = phone.group()

#         label = text.replace(
#             value,
#             ""
#         ).strip()

#         return label, value

#     # ------------------------
#     # Date
#     # ------------------------

#     date = re.search(
#         DATE_PATTERN,
#         text
#     )

#     if date:

#         value = date.group()

#         label = text.replace(
#             value,
#             ""
#         ).strip()

#         return label, value

#     # ------------------------
#     # Number at End
#     # ------------------------

#     number = re.search(
#         NUMBER_PATTERN + r"$",
#         text
#     )

#     if number:

#         value = number.group()

#         label = text.replace(
#             value,
#             ""
#         ).strip()

#         return label, value

#     return text, ""


"""
label_matcher.py

Matches OCR text to known field labels using fuzzy matching.
"""

from difflib import get_close_matches

# --------------------------------------------------
# Known Labels
# --------------------------------------------------

KNOWN_LABELS = [

    "Full Name",
    "Gender",
    "DOB",
    "SSN",
    "Address",
    "Address 1",
    "Address 2",
    "City",
    "State",
    "Postal",
    "Country",
    "Email",
    "Contact",

    "Customer ID",
    "A/c Type",
    "A/c Name",
    "A/c Number",

    "Occupation",
    "Employer",
    "Employer Address",

    "Investment Objective",
    "Risk Tolerance",

    "Annual Income",
    "Net Worth",

    "Last Txn Date",
    "Last Txn Amount",

    "Bond Name",
    "Buying IPv4",

    "Attorney",
    "CPA",
    "Financial Advisor"

]


# --------------------------------------------------
# Normalize OCR text
# --------------------------------------------------

def normalize(text: str) -> str:
    """
    Normalize OCR text before matching.
    """

    return (
        text.upper()
        .replace(":", "")
        .replace("-", " ")
        .replace("_", " ")
        .strip()
    )


# --------------------------------------------------
# Match OCR label
# --------------------------------------------------

def match_label(text: str, cutoff=0.75):
    """
    Returns the closest known label.

    Example

    Ful Name
        ↓
    Full Name
    """

    normalized = normalize(text)

    mapping = {
        normalize(label): label
        for label in KNOWN_LABELS
    }

    match = get_close_matches(
        normalized,
        mapping.keys(),
        n=1,
        cutoff=cutoff
    )

    if match:
        return mapping[match[0]]

    return None


# --------------------------------------------------
# Check whether OCR text is a label
# --------------------------------------------------

def is_label(text: str):
    """
    Returns True if OCR text matches a known label.
    """

    return match_label(text) is not None