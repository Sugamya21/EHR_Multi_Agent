from app.database.patient_repository import get_ehr
from app.services.patient_import_service import extract_relevant_ehr_data
from app.agents.trend_insight_agent import analyze_trends


def generate_patient_summary(patient_id):

    ehr_document = get_ehr(patient_id)

    if ehr_document is None:
        raise ValueError(
            f"No EHR found for {patient_id}"
        )

    bundle = ehr_document.get("fhirBundle")

    if not bundle:
        raise ValueError(
            f"Patient EHR does not contain a FHIR Bundle for {patient_id}"
        )

    relevant_data = extract_relevant_ehr_data(bundle)

    analysis = analyze_trends(
        relevant_data
    )

    return {
        "patientId": patient_id,
        "overview": analysis.get(
            "overview",
            "No clinical overview available."
        ),
        "trends": analysis.get(
            "trends",
            []
        ),
        "recentChanges": analysis.get(
            "recentChanges",
            []
        )
    }