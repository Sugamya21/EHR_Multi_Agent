import sys
import os

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from app.database.patient_repository import get_ehr
from app.services.gemini_service import generate_patient_summary


PATIENT_ID = "PAT0001"


# --------------------------------------------------
# 1. Get updated EHR
# --------------------------------------------------

ehr_document = get_ehr(PATIENT_ID)

if ehr_document is None:
    print("Patient EHR not found.")
    sys.exit(1)


print("Updated EHR retrieved successfully.")


# --------------------------------------------------
# 2. Get FHIR Bundle
# --------------------------------------------------

ehr_data = ehr_document.get(
    "fhirBundle"
)

if not ehr_data:
    print("FHIR Bundle not found.")
    sys.exit(1)


# --------------------------------------------------
# 3. Generate summary
# --------------------------------------------------

print(
    "\nGenerating updated patient summary..."
)

summary = generate_patient_summary(
    ehr_data
)


# --------------------------------------------------
# 4. Display summary
# --------------------------------------------------

print(
    "\n========== UPDATED PATIENT SUMMARY ==========\n"
)

print(summary)

print(
    "\n=============================================\n"
)