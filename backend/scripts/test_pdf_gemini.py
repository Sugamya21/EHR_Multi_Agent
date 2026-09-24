import sys
import os
import json

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from app.services.gemini_service import (
    extract_ehr_from_text
)

from app.utils.ehr_validator import (
    validate_ehr_data
)

from scripts.extract_pdf import (
    extract_text
)


if __name__ == "__main__":

    pdf_path = "data/sample_doctor_medical_report.pdf"

    # --------------------------------------------------
    # Step 1: Extract PDF text
    # --------------------------------------------------

    pdf_text = extract_text(pdf_path)

    print("\nPDF text extracted successfully.\n")

    # --------------------------------------------------
    # Step 2: Gemini extraction
    # --------------------------------------------------

    extracted_data = extract_ehr_from_text(
        pdf_text
    )

    print(
        "\n========== GEMINI STRUCTURED DATA ==========\n"
    )

    print(
        json.dumps(
            extracted_data,
            indent=4
        )
    )

    # --------------------------------------------------
    # Step 3: Validate
    # --------------------------------------------------

    is_valid, errors = validate_ehr_data(
        extracted_data
    )

    print(
        "\n========== VALIDATION RESULT ==========\n"
    )

    if is_valid:

        print("EHR data is VALID.")

    else:

        print("EHR data is INVALID.")

        print("\nErrors:")

        for error in errors:
            print(f"- {error}")

    print(
        "\n========================================\n"
    )