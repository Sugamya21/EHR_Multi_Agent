import sys
import os

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from app.database.patient_repository import (
    get_ehr,
    update_ehr
)


if __name__ == "__main__":

    patient_id = "PAT0001"

    # Get current EHR
    ehr_document = get_ehr(patient_id)

    if ehr_document is None:
        print("Patient EHR not found.")
        sys.exit(1)

    bundle = ehr_document["fhirBundle"]

    # ------------------------------------------------
    # Dummy new medical information
    # Later this will come from the PDF Processing Agent
    # ------------------------------------------------

    new_condition = {
        "resourceType": "Condition",
        "id": "dummy-hypertension-001",
        "clinicalStatus": {
            "coding": [
                {
                    "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                    "code": "active",
                    "display": "Active"
                }
            ]
        },
        "code": {
            "coding": [
                {
                    "display": "Hypertension"
                }
            ],
            "text": "Hypertension"
        }
    }

    # Add new condition to the existing bundle
    bundle.setdefault("entry", [])

    bundle["entry"].append({
        "resource": new_condition
    })

    # Update the same MongoDB document
    updated = update_ehr(
        patient_id,
        bundle
    )

    if updated:
        print(
            f"{patient_id} EHR updated successfully!"
        )
    else:
        print(
            "No document was modified."
        )