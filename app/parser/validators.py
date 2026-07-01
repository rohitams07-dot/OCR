"""
validators.py

Field-specific validation and correction for OCR values.
"""

import re
import ipaddress


# --------------------------------------------------
# Common OCR Corrections
# --------------------------------------------------

OCR_CHAR_MAP = {
    "O": "0",
    "o": "0",
    "I": "1",
    "l": "1",
    "|": "1",
    "S": "5",
    "B": "8"
}


def replace_common_ocr_errors(text: str) -> str:
    """
    Replace common OCR mistakes.
    Used only for numeric fields.
    """

    result = ""

    for ch in text:
        result += OCR_CHAR_MAP.get(ch, ch)

    return result


# --------------------------------------------------
# Date
# --------------------------------------------------

DATE_PATTERN = re.compile(
    r"^\d{2}[-/][A-Za-z]{3}[-/]\d{2,4}$|^\d{2}[-/]\d{2}[-/]\d{2,4}$"
)


def validate_date(value: str):
    value = value.strip()

    if DATE_PATTERN.match(value):
        return value

    return value


# --------------------------------------------------
# Email
# --------------------------------------------------

EMAIL_PATTERN = re.compile(
    r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
)


def validate_email(value: str):

    value = value.strip()

    value = value.replace(" ", "")

    if EMAIL_PATTERN.match(value):
        return value

    return value


# --------------------------------------------------
# Phone
# --------------------------------------------------

PHONE_PATTERN = re.compile(
    r"^\+?[\d\s()\-]{7,20}$"
)


def validate_phone(value: str):

    value = value.strip()

    if PHONE_PATTERN.match(value):
        return value

    return value


# --------------------------------------------------
# SSN
# --------------------------------------------------

SSN_PATTERN = re.compile(
    r"^\d{3}-\d{2}-\d{4}$"
)


def validate_ssn(value: str):

    value = replace_common_ocr_errors(value)

    if SSN_PATTERN.match(value):
        return value

    return value


# --------------------------------------------------
# Customer ID
# --------------------------------------------------

def validate_customer_id(value: str):

    value = replace_common_ocr_errors(value)

    value = re.sub(r"\D", "", value)

    return value


# --------------------------------------------------
# Account Number
# --------------------------------------------------

def validate_account_number(value: str):

    value = replace_common_ocr_errors(value)

    value = re.sub(r"\s+", "", value)

    return value


# --------------------------------------------------
# Postal Code
# --------------------------------------------------

def validate_postal(value: str):

    return value.strip().upper()


# --------------------------------------------------
# IPv4
# --------------------------------------------------

def validate_ipv4(value: str):

    value = value.strip()

    try:
        ipaddress.IPv4Address(value)
        return value

    except Exception:
        return value


# --------------------------------------------------
# IPv6
# --------------------------------------------------

def validate_ipv6(value: str):

    value = value.strip()

    try:
        ipaddress.IPv6Address(value)
        return value

    except Exception:
        return value


# --------------------------------------------------
# VIN
# --------------------------------------------------

def validate_vin(value: str):

    value = value.strip().upper()

    value = value.replace(" ", "")

    if len(value) == 17:
        return value

    return value


# --------------------------------------------------
# IBAN
# --------------------------------------------------

def validate_iban(value: str):

    value = value.strip().upper()

    value = value.replace(" ", "")

    return value


# --------------------------------------------------
# Dispatcher
# --------------------------------------------------

def validate_field(label: str, value: str):
    """
    Route validation based on field name.
    """

    label = label.lower().strip()

    if not value:
        return value

    if "email" in label:
        return validate_email(value)

    if "phone" in label or "contact" in label:
        return validate_phone(value)

    if "dob" in label or "date" in label:
        return validate_date(value)

    if "ssn" in label:
        return validate_ssn(value)

    if "customer id" in label:
        return validate_customer_id(value)

    if "account" in label or "a/c" in label:
        return validate_account_number(value)

    if "postal" in label or "zip" in label:
        return validate_postal(value)

    if "ipv4" in label:
        return validate_ipv4(value)

    if "ipv6" in label:
        return validate_ipv6(value)

    if "vin" in label:
        return validate_vin(value)

    if "iban" in label:
        return validate_iban(value)

    return value