import sys
import os
import json


# ============================================================
# Add backend directory to Python path
# ============================================================

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)


# ============================================================
# Imports
# ============================================================

from scripts.extract_pdf import (
    extract_text
)

from app.services.gemini_service import (
    extract_ehr_from_text
)

from app.utils.ehr_validator import (
    validate_ehr_data
)

from app.agents.ehr_update_agent import (
    update_patient_ehr
)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    patient_id = "PAT0001"

    pdf_path = (
        "data/sample_doctor_medical_report.pdf"
    )

    # --------------------------------------------------------
    # 1. Extract PDF text
    # --------------------------------------------------------

    pdf_text = extract_text(
        pdf_path
    )

    print(
        "\nPDF extracted successfully."
    )

    # --------------------------------------------------------
    # 2. Gemini extraction
    # --------------------------------------------------------

    extracted_data = extract_ehr_from_text(
        pdf_text
    )

    print(
        "\nGemini extraction completed."
    )

    # --------------------------------------------------------
    # 3. Validation
    # --------------------------------------------------------

    is_valid, errors = validate_ehr_data(
        extracted_data
    )

    if not is_valid:

        print(
            "\nEHR data is INVALID."
        )

        for error in errors:

            print(
                f"- {error}"
            )

        sys.exit(1)

    print(
        "\nEHR data is VALID."
    )

    # --------------------------------------------------------
    # 4. Patient ID safety check
    # --------------------------------------------------------

    extracted_patient_id = (
        extracted_data.get(
            "patientId",
            ""
        )
    )

    if (
        extracted_patient_id
        and extracted_patient_id != patient_id
    ):

        print(
            "\nERROR: Patient ID mismatch."
        )

        print(
            f"Selected patient : {patient_id}"
        )

        print(
            f"PDF patient      : {extracted_patient_id}"
        )

        sys.exit(1)

    # --------------------------------------------------------
    # 5. DRY RUN
    #
    # IMPORTANT:
    # True = MongoDB will NOT be modified.
    # --------------------------------------------------------

    result = update_patient_ehr(
        patient_id,
        extracted_data,
        dry_run=True
    )

    # --------------------------------------------------------
    # 6. Display result
    # --------------------------------------------------------

    print(
        "\n========== EHR UPDATE DRY RUN ==========\n"
    )

    print(
        json.dumps(
            result,
            indent=4
        )
    )

    print(
        "\n========================================\n"
    )

    # --------------------------------------------------------
    # 7. Confirm whether MongoDB was modified
    # --------------------------------------------------------

    if result.get("dryRun") is True:

        print(
            "MongoDB was NOT modified."
        )

    else:

        print(
            "MongoDB was modified."
        )