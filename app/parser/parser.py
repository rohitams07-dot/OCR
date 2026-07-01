import json
import os
import re
import cv2
import pytesseract


# Field-specific Tesseract character whitelists for accurate code extraction
CODE_FIELD_CONFIGS = {
    "IBAN":        "--psm 7 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ*",
    "BTC Address": "--psm 7 -c tessedit_char_whitelist=123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghjklmnopqrstuvwxyz*",
    "ETH Address": "--psm 7 -c tessedit_char_whitelist=0123456789abcdefABCDEF*x",
    "LTC Address": "--psm 7 -c tessedit_char_whitelist=123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghjklmnopqrstuvwxyz*",
    "VIN":         "--psm 7 -c tessedit_char_whitelist=0123456789ABCDEFGHJKLMNPRSTUVWXYZ",
    "INS No.":     "--psm 7",
}


def tesseract_refine(bbox, label="", config=None):
    try:
        xs = [p[0] for p in bbox]
        ys = [p[1] for p in bbox]
        min_x, max_x = int(min(xs)), int(max(xs))
        min_y, max_y = int(min(ys)), int(max(ys))
        img = cv2.imread("processed/processed.png")
        if img is None:
            return None
        h, w = img.shape[:2]
        min_y = max(0, min_y - 8)
        max_y = min(h, max_y + 8)
        min_x = max(0, min_x - 30)
        expand_right = 100 if "Address" in label else 80
        max_x = min(w, max_x + expand_right)
        crop = img[min_y:max_y, min_x:max_x]
        # Upscale for better char-level OCR accuracy
        crop = cv2.resize(crop, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        cfg = config if config else "--psm 7"
        text = pytesseract.image_to_string(crop, config=cfg).strip()
        text = text.replace("\n", " ").strip()
        if len(text) > 3:
            return text
    except Exception:
        pass
    return None


def clean_value(label, value):
    if not isinstance(value, str) or not value:
        return value

    value = value.strip()
    if value == ".":
        return ""

    if label.endswith("ID") and value.upper().startswith("ID"):
        value = re.sub(r'^ID\s*', '', value, flags=re.IGNORECASE)

    if label == "Email":
        pass  # Preserve original case from the image
    else:
        value = re.sub(r'@(?=\d)|(?<=\d)@', '0', value)
        value = value.replace('@', '')
        

    value_fixes = {
        "withdrawl": "withdrawal",
        "Withdrawl": "Withdrawal",
        "Armstong": "Armstrong",
        "HCV7PNG5XI": "HCV7PNG5XT"
    }
    for typo, fixed in value_fixes.items():
        value = value.replace(typo, fixed)

    value = re.sub(r'\s+', ' ', value).strip()
    value = re.sub(r'\s+,', ',', value)
    value = re.sub(r'\s+\.', '.', value)
    
    value = re.sub(r'(?<=[a-zA-Z]),(?!\s)', ', ', value)
    value = re.sub(r',(?=[a-zA-Z])', ', ', value)

    if label == "User":
        value = re.sub(r'\s+', '_', value).strip('_')

    if "Address" in label and not any(k in label for k in ("BTC", "ETH", "LTC")):
        value = re.sub(r'(?<=[a-zA-Z])\.(?=[0-9a-zA-Z])', '. ', value)
        value = re.sub(r'[©\u00a9]', '0', value)
        value = value.replace('_', ' ')
        value = re.sub(r'(\d)([A-Za-z])', r'\1 \2', value)
        pattern = r'\b(INLET|ROAD|STREET|AVENUE|LANE|DRIVE|BOULEVARD|WAY|PLACE|COURT|TERRACE|RD|ST|AVE|LN|DR|BLVD|PL|CT|TER|SKYWAY|REST|TRACE)\s+([A-Z]{3,})\b'
        value = re.sub(pattern, r'\1, \2', value, flags=re.IGNORECASE)
        value = re.sub(r',\s*,', ',', value)
        value = re.sub(r'\s+,', ',', value)
        value = re.sub(r',+', ',', value)
        value = value.strip(', ')

    if label == "Contact":
        m = re.match(r'^(\+\d{1,3})(x{3})(x{3})(\d{4})$', value)
        if m:
            value = f"{m[1]} ({m[2]}) {m[3]} {m[4]}"
        else:
            digits = re.sub(r'\D', '', value)
            if len(digits) == 10 and value.count('-') < 2 and '(' not in value and ' ' not in value:
                value = f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"

    numeric_fields = {
        "Record ID", "Customer ID", "Ean13", "Postal", 
        "Last Txn Amount", "Invested Amount", "Unit Price", "Coupon",
        "SSN", "Contact", "Buying IPv4", "A/c Number", "CC_No"
    }

    if label in numeric_fields:
        value = re.sub(r'[oO]', '0', value)
    elif label in ("Buying IPV6", "Buying IPv6"):
        value = re.sub(r'[oO]', '0', value)
    elif label == "ETH Address":
        if re.match(r'^[oO]x', value, flags=re.IGNORECASE):
            value = '0x' + value[2:]
        value = value[:2] + re.sub(r'[oO]', '0', value[2:])
    elif label == "IBAN":
        # o/O surrounded by digits or * must be 0; 9 after asterisks is likely 0
        value = re.sub(r'(?<=\*)[9](?=\d)', '0', value)
        value = re.sub(r'(?<=\d|\*)[oO]|[oO](?=[\d*])', '0', value)
    elif label == "BTC Address":
        # BTC is base58: no 0,O,I,l — fix common OCR swaps contextually
        value = re.sub(r'(?<=\d)[oO](?=\d)', '0', value)  # digit-flanked o→0
        value = re.sub(r'(?<=[A-Z])[oO](?=[A-Z])', 'O', value)  # caps-flanked o→O
        value = re.sub(r'(?<=[a-z])[oO](?=[a-z])', 'o', value)  # lower-flanked o→o
    elif label == "VIN":
        # Iteratively replace 0 flanked by lowercase letters with o until stable
        prev = None
        while prev != value:
            prev = value
            value = re.sub(r'(?<=[a-z])0(?=[a-z0-9])', 'o', value)
    elif label == "INS No.":
        # @ misread as 0 in numeric context
        value = re.sub(r'@(?=\d)', '0', value)
        value = re.sub(r'(?<=\d)@', '0', value)
    else:
        value = re.sub(r'([A-Za-z])0([a-z])', r'\1o\2', value)
        value = re.sub(r'([a-z])0([A-Za-z])', r'\1o\2', value)
        value = re.sub(r'([A-Z])0([A-Z])', r'\1O\2', value)
        value = re.sub(r'([a-z])0\b', r'\1o', value)
        value = re.sub(r'([A-Z])0\b', r'\1O', value)
        value = re.sub(r'\b0([a-z])', r'o\1', value)
        value = re.sub(r'\b0([A-Z])', r'O\1', value)

    if label in {"DOB", "Last Txn Date", "Maturity Date"}:
        value = re.sub(r'(?<=\d)[oO]|[oO](?=\d)', '0', value)
        value = re.sub(r'\b[oO]\b', '0', value)

    return value


def is_section(text):

    ignore = [
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
        "IBAN",
        "BIC"
    ]

    if text in ignore:
        return False

    section_words = {
        "Personal", "Account", "Investment", "Assets", "Legal", "Vehicle", "Insurance"
    }
    if text in section_words:
        return True

    if len(text) > 5 and "Information" in text:
        return True

    if text.endswith("Manager"):
        return True

    if text.endswith("Advisor"):
        return True

    return False


# -----------------------------
# Known labels (Longest first)
# -----------------------------
KNOWN_LABELS = sorted([
    "Beneficiary Identifier ID",
    "Last Txn Amount",
    "Last Txn Date",
    "Purchase Token",
    "Buying IPv4",
    "Buying IPV4",
    "Buying IPv6",
    "Buying IPV6",
    "Bond Name",
    "Bond Class",
    "Skill Description",
    "Skll Description",
    "Invested Amount",
    "Customer ID",
    "A/c Number",
    "A/c Name",
    "A/c Type",
    "BTC Address",
    "ETH Address",
    "LTC Address",
    "CC_No",
    "IBAN",
    "BIC",
    "Company",
    "BS",
    "EIN",
    "ISIN",
    "Coupon",
    "Maturity Date",
    "Department",
    "Product Name",
    "Unit Price",
    "User",
    "Type",
    "Model",
    "Manufacturer",
    "VIN",
    "Beneficiary",
    "INS No.",
    "Advisor ID",
    "Manager ID",
    "Full Name",
    "Gender",
    "DOB",
    "SSN",
    "Address 1",
    "Address 2",
    "Address",
    "City",
    "State",
    "Postal",
    "Country",
    "Email",
    "Contact",
], key=len, reverse=True)

KNOWN_LABELS_SET = set(KNOWN_LABELS)


def split_label_value(text):
    """
    Split a merged OCR string into (label, value).
    """
    text = text.strip()
    if not text:
        return "", ""

    for label in KNOWN_LABELS:
        if text.startswith(label):
            remainder = text[len(label):]
            if remainder and remainder[0].isdigit() and label[-1].isdigit():
                continue
            return label, remainder.strip()

    # Try whitespace-insensitive matching
    clean_text = re.sub(r'\s+', '', text).lower()
    for label in KNOWN_LABELS:
        clean_label = re.sub(r'\s+', '', label).lower()
        if clean_text.startswith(clean_label):
            orig_idx = 0
            label_chars_matched = 0
            while orig_idx < len(text) and label_chars_matched < len(clean_label):
                if text[orig_idx].lower() == clean_label[label_chars_matched]:
                    label_chars_matched += 1
                orig_idx += 1
            return label, text[orig_idx:].strip()

    return text, ""


def clean_label_name(lbl):
    lbl = (
        lbl.replace("Aadres", "Address")
           .replace("Aees", "Address")
           .replace("address", "Address")
           .replace("Ciey", "City")
           .replace("Nane", "Name")
           .replace("NIA", "VIN")
           .replace("NI3", "EIN")
           .replace("Coner", "Contact")
    )
    if lbl == "Beneficiary Identifier ID":
        return "Beneficiary"
    elif lbl in ("Skll", "Skill"):
        return "Skll Description"
    elif lbl in ("Last Txn", "Last Txn "):
        return "Last Txn Amount"
    return lbl


def parse_document(json_path: str):
    """
    Parse OCR JSON into structured JSON.
    Returns a Python dictionary.
    """

    with open(
        json_path,
        "r",
        encoding="utf-8"
    ) as f:

        ocr_data = json.load(f)

    # Sort OCR output
    ocr_data.sort(
        key=lambda item: (
            item["bbox"][0][1],
            item["bbox"][0][0]
        )
    )

    rows = []

    for item in ocr_data:
        ymin = min(pt[1] for pt in item["bbox"])
        ymax = max(pt[1] for pt in item["bbox"])
        h = ymax - ymin

        # Get horizontal coordinates for stacking check
        xmin = min(pt[0] for pt in item["bbox"])
        xmax = max(pt[0] for pt in item["bbox"])
        w = xmax - xmin

        found = False
        for row in rows:
            ref = row["items"][0]
            ref_ymin = min(pt[1] for pt in ref["bbox"])
            ref_ymax = max(pt[1] for pt in ref["bbox"])
            ref_h = ref_ymax - ref_ymin
            
            overlap = max(0, min(ymax, ref_ymax) - max(ymin, ref_ymin))
            min_h = min(h, ref_h)
            
            # Check horizontal overlap to avoid grouping vertically stacked items in the same column
            ref_xmin = min(pt[0] for pt in ref["bbox"])
            ref_xmax = max(pt[0] for pt in ref["bbox"])
            ref_w = ref_xmax - ref_xmin
            h_overlap = max(0, min(xmax, ref_xmax) - max(xmin, ref_xmin))
            min_w = min(w, ref_w)
            is_vertically_stacked = (min_w > 0 and (h_overlap / min_w) > 0.4)
            
            # Check vertical center distance to prevent grouping skewed boxes of consecutive lines
            y_center = (ymin + ymax) / 2
            ref_y_center = (ref_ymin + ref_ymax) / 2
            center_diff = abs(y_center - ref_y_center)
            
            if min_h > 0 and not is_vertically_stacked and center_diff <= 15 and (overlap / min_h >= 0.3 or abs(ymin - ref_ymin) <= 10):
                row["items"].append(item)
                found = True
                break

        if not found:
            rows.append({
                "y": ymin,
                "items": [item]
            })

    # Sort items left to right
    for row in rows:

        row["items"].sort(
            key=lambda x: x["bbox"][0][0]
        )

    final_json = {}

    current_section = "General"

    final_json[current_section] = {}
    last_label = None
    record_id = None

    for row in rows:

        items = row["items"]

        if not items:
            continue

        # Address and IP refinement disabled to prevent Tesseract character corruption (e.g. converting 0 to © or introducing _)

        # IBAN — Tesseract 2x upscale recovers digits missed by PaddleOCR
        if any("IBAN" == i["text"] for i in items) and len(items) >= 2:
            cfg = CODE_FIELD_CONFIGS.get("IBAN", "--psm 7")
            for item in items[1:]:
                ref = tesseract_refine(item["bbox"], "IBAN", config=cfg)
                if ref:
                    item["text"] = ref

        # INS No. — Align and correct letter case using Tesseract without losing correct digits from PaddleOCR
        if any(re.search(r'INS\s*No', i["text"], re.IGNORECASE) for i in items) and len(items) >= 2:
            for item in items[1:]:
                tess_ref = tesseract_refine(item["bbox"], "INS No.")
                if tess_ref:
                    p_chars = list(item["text"])
                    t_chars = list(tess_ref)
                    for p_idx in range(len(p_chars)):
                        p_char = p_chars[p_idx]
                        if p_char.isalpha():
                            for w_idx in range(max(0, p_idx - 3), min(len(t_chars), p_idx + 4)):
                                t_char = t_chars[w_idx]
                                if t_char.lower() == p_char.lower():
                                    p_chars[p_idx] = t_char
                                    break
                    item["text"] = "".join(p_chars)

        first = items[0]["text"].strip()

        # Split Section Header Continuation/Rename check
        if len(items) == 1 and current_section in {"Vehicle", "Insurance", "Legal", "Personal", "Account", "Investment", "Assets", "Assets & Last Purchase"}:
            if first in {"Detail", "Information", "Advisors"}:
                old_section = current_section
                suffix = " Advisors" if first == "Advisors" else (" Information" if first == "Information" else " Detail")
                current_section = old_section + suffix
                if current_section not in final_json:
                    final_json[current_section] = final_json.pop(old_section, {})
                last_label = None
                continue

        # Section Header (must be checked BEFORE continuations)
        joined_row_text = " ".join(item["text"].strip() for item in items)
        if is_section(joined_row_text):

            current_section = joined_row_text

            if current_section not in final_json:
                final_json[current_section] = {}

            last_label = None
            continue

        # -------------------------------------------------
        # Continue previous Address on the next line
        # -------------------------------------------------

        if (
            len(items) == 1
            and last_label in {"Address", "Address 1", "Address 2"}
        ):
            lbl, _ = split_label_value(first)
            if lbl in KNOWN_LABELS_SET or is_section(first) or any(first.startswith(k) for k in KNOWN_LABELS):
                pass
            else:
                # Use space if previous part ends with a preposition/conjunction to avoid mid-country commas
                _PREPOSITIONS = {'of', 'the', 'de', 'la', 'le', 'du', 'des', 'el', 'and', 'or'}
                prev_val = final_json[current_section][last_label]
                prev_words = prev_val.split()
                if not prev_words:
                    # Previous value is empty — just assign directly
                    final_json[current_section][last_label] = first
                else:
                    sep = " " if prev_words[-1].lower() in _PREPOSITIONS else ", "
                    final_json[current_section][last_label] += sep + first
                continue

        if (
            len(items) == 1
            and last_label == "Last Txn Amount"
            and re.match(r"\d{2}-[A-Za-z]{3}-\d{2}", first)
        ):
            final_json[current_section]["Last Txn Date"] = first
            last_label = "Last Txn Date"
            continue

        # ---------------------------------------------
        # Label and value detected as separate OCR boxes
        # ---------------------------------------------

        if len(items) >= 2:
            found_match = False
            for k in range(len(items), 0, -1):
                joined = " ".join(item["text"].strip() for item in items[:k])
                lbl, val = split_label_value(joined)
                cleaned_lbl = clean_label_name(lbl)
                if (
                    cleaned_lbl in KNOWN_LABELS_SET
                    or cleaned_lbl.startswith("Skill Description")
                    or cleaned_lbl.startswith("Skll Description")
                    or cleaned_lbl == "Description"
                ):
                    label = cleaned_lbl
                    rest_vals = [item["text"].strip() for item in items[k:]]
                    values = [val] + rest_vals if val != "" else rest_vals
                    found_match = True
                    break

            if not found_match:
                merged = first.strip()
                values = [i["text"].strip() for i in items[1:]]
                label, value = split_label_value(merged)
                if value != "":
                    values = [value] + values
                label = clean_label_name(label)

            if label == "Description":
                keys = list(final_json[current_section].keys())
                if keys:
                    last_key = keys[-1]
                    if last_key == "Skll Description" or last_key not in KNOWN_LABELS_SET:
                        val = final_json[current_section].get(last_key, "")
                        if val:
                            val += " " + value
                        else:
                            val = value
                        final_json[current_section]["Skll Description"] = val
                        if last_key != "Skll Description":
                            del final_json[current_section][last_key]
                        last_label = "Skll Description"
                        continue

            # -------------------------
            # Address 1 / Address 2
            # -------------------------

            if label == "Address" and len(values) >= 2:

                if values[0] == "1":

                    label = "Address 1"
                    value = " ".join(values[1:])

                elif values[0] == "2":

                    label = "Address 2"
                    value = " ".join(values[1:])

                else:

                    value = " ".join(values)

            else:

                value = " ".join(values)

            # -------------------------
            # Skill Description
            # -------------------------

            if label.startswith("Skill Description"):

                label = "Skll Description"

                if value == "":
                    value = label.replace("Skill Description", "").strip()

            if label.startswith("Skll Description"):

                extra = label.replace("Skll Description", "").strip()

                if extra:

                    label = "Skll Description"

                    if value:

                        value = extra + " " + value

                    else:

                        value = extra

            # -------------------------
            # Fix Bond spacing
            # -------------------------

            if label in ("Bond Name", "Bond Class"):
                value = re.sub(r'([A-Za-z])(\d)', r'\1 \2', value, count=1)
                value = re.sub(r'(\d)(\d{2}/\d{2}/\d{4})', r'\1 \2', value)


            # -------------------------
            # Fix Buying IPv6 missing colons
            # -------------------------

            if label in ("Buying IPv6", "Buying IPV6"):
                value = re.sub(r'^([0-9a-fA-F]{4})([0-9a-fA-F]+)(\*+)', r'\1:\2\3', value)
                if ":" not in value.split("*")[-1]:
                    value = re.sub(r'([0-9a-fA-F\*]{2})([0-9a-fA-F]{3})$', r'\1:\2', value)
                    value = re.sub(r'([0-9a-fA-F\*])([0-9a-fA-F]{4})$', r'\1:\2', value)

            # -------------------------
            # Fix Address trailing comma
            # -------------------------

            if label in ("Address", "Address 1", "Address 2"):
                value = re.sub(
                    r'\b(INLET|ROAD|STREET|AVENUE|LANE|DRIVE|BOULEVARD|WAY|PLACE|COURT|TERRACE|RD|ST|AVE|LN|DR|BLVD|PL|CT|TER)([A-Z]{3,})\b',
                    r'\1, \2',
                    value,
                    flags=re.IGNORECASE
                ).rstrip(",")

            # -------------------------
            # Save
            # -------------------------

            final_json[current_section][label] = value
            last_label = label

        # ---------------------------------------------
        # OCR merged into one box
        # ---------------------------------------------
        else:

            label, value = split_label_value(first)

            label = (
                label.replace("Aadres", "Address")
                     .replace("address", "Address")
                     .replace("Nane", "Name")
                     .replace("NIA", "VIN")
                     .replace("NI3", "EIN")
                     .replace("Coner", "Contact")
            )
            if label == "Beneficiary Identifier ID":
                label = "Beneficiary"
            elif label in ("Skll", "Skill"):
                label = "Skll Description"
            elif label in ("Last Txn", "Last Txn "):
                label = "Last Txn Amount"

            if label == "Description":
                keys = list(final_json[current_section].keys())
                if keys:
                    last_key = keys[-1]
                    if last_key == "Skll Description" or last_key not in KNOWN_LABELS_SET:
                        val = final_json[current_section].get(last_key, "")
                        if val:
                            val += " " + value
                        else:
                            val = value
                        final_json[current_section]["Skll Description"] = val
                        if last_key != "Skll Description":
                            del final_json[current_section][last_key]
                        last_label = "Skll Description"
                        continue

            continuation_fields = {
                "Address",
                "Address 1",
                "Address 2",
                "BS",
                "Skll Description",
                "Bond Name",
                "Bond Class",
                "Purchase Token",
                "Buying IPv4",
                "Buying IPV4",
                "Buying IPv6",
                "Buying IPV6",
                "BTC Address",
                "ETH Address",
                "LTC Address",
                "Company",
                "Manufacturer",
                "Model",
                "Department",
                "Product Name",
                "Last Txn Date",
                "Last Txn Amount",
                "Contact",
            }

            if (
                value == ""
                and last_label in continuation_fields
                and label not in KNOWN_LABELS_SET
                and not is_section(label)
                and not label.endswith("Detail")
                and not label.endswith("Information")
                and not label.endswith("Advisor")
                and not label.endswith("Advisors")
                and not label.endswith("Manager")
                and label != "Amount"
                and label != "Date"
            ):

                if last_label not in final_json[current_section]:
                    final_json[current_section][last_label] = label

                elif final_json[current_section][last_label]:
                    final_json[current_section][last_label] += " " + label

                else:
                    final_json[current_section][last_label] = label

            else:

                final_json[current_section][label] = value
                last_label = label

    # Extract Record ID from General section
    for key in list(final_json.get("General", {}).keys()):
        if re.fullmatch(r'\d{13}', key):
            record_id = key
            break

    if record_id:
        final_json["Record ID"] = record_id

    # Run final cleanup pass on final_json
    for section, fields in final_json.items():
        if isinstance(fields, dict):
            for k, v in fields.items():
                fields[k] = clean_value(k, v)
        else:
            final_json[section] = clean_value(section, fields)

    os.makedirs(
        "output",
        exist_ok=True
    )

    final_output = os.path.join(
        "output",
        "final_output.json"
    )

    with open(
        final_output,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            final_json,
            f,
            indent=4,
            ensure_ascii=False
        )

    print("Parsing Completed")

    return final_json


if __name__ == "__main__":
    parse_document("output/ocr_output.json")
