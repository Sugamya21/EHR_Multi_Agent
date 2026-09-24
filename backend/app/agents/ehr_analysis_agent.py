from app.database.patient_repository import get_ehr

from app.services.patient_import_service import (
    extract_relevant_ehr_data
)

from app.services.gemini_service import (
    generate_patient_summary
)


def analyze_patient(patient_id):

    # Step 1: Get patient's EHR
    ehr_document = get_ehr(patient_id)

    if ehr_document is None:
        raise ValueError(
            f"No EHR found for {patient_id}"
        )

    # Step 2: Get complete FHIR Bundle
    bundle = ehr_document["fhirBundle"]

    # Step 3: Extract relevant medical information
    relevant_data = extract_relevant_ehr_data(
        bundle
    )

    # Step 4: Ask Gemini to analyze it
    summary = generate_patient_summary(
        relevant_data
    )

    return summary