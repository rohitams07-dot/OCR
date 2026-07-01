from typing import Dict


def calculate_score(report: Dict) -> int:
    """
    Calculate OCR readiness score (0 - 100).
    """

    score = 100

    # ---------------------------
    # Resolution
    # ---------------------------

    if report["resolution"]["status"] == "Low":
        score -= 20

    # ---------------------------
    # Brightness
    # ---------------------------

    if report["brightness"]["status"] == "Dark":
        score -= 10

    elif report["brightness"]["status"] == "Very Bright":
        score -= 5

    # ---------------------------
    # Contrast
    # ---------------------------

    if report["contrast"]["status"] == "Low":
        score -= 20

    # ---------------------------
    # Blur
    # ---------------------------

    if report["blur"]["status"] == "Blurry":
        score -= 25

    return max(score, 0)


def quality_grade(score: int) -> str:
    """
    Convert score to grade.
    """

    if score >= 90:
        return "Excellent"

    elif score >= 75:
        return "Good"

    elif score >= 60:
        return "Fair"

    elif score >= 40:
        return "Poor"

    return "Very Poor"


def print_final_report(report: Dict):
    """
    Print OCR quality report.
    """

    score = calculate_score(report)

    grade = quality_grade(score)

    print("\n")
    print("=" * 55)
    print("            OCR IMAGE QUALITY REPORT")
    print("=" * 55)

    print(
        f"Resolution : "
        f"{report['resolution']['width']} x "
        f"{report['resolution']['height']}"
    )

    print(
        f"Brightness : "
        f"{report['brightness']['value']} "
        f"({report['brightness']['status']})"
    )

    print(
        f"Contrast   : "
        f"{report['contrast']['value']} "
        f"({report['contrast']['status']})"
    )

    print(
        f"Blur Score : "
        f"{report['blur']['value']} "
        f"({report['blur']['status']})"
    )

    print("-" * 55)

    print(f"OCR Score  : {score}/100")
    print(f"Grade      : {grade}")

    print("-" * 55)

    if report["recommendations"]:

        print("Recommended Enhancements:")

        for item in report["recommendations"]:
            print(f"  ✔ {item}")

    else:

        print("No preprocessing required.")

    print("=" * 55)
    print()


def ocr_ready(report: Dict) -> bool:
    """
    Returns True if image is good enough for OCR.
    """

    score = calculate_score(report)

    return score >= 60