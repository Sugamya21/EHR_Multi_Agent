import json

from app.database.patient_repository import (
    save_patient,
    save_ehr
)


def load_fhir_bundle(file_path):
    """Load a complete FHIR bundle from a JSON file."""

    with open(file_path, "r", encoding="utf-8") as file:
        bundle = json.load(file)

    return bundle


def extract_patient_data(bundle):
    """Extract basic patient information from a FHIR Bundle."""

    for entry in bundle.get("entry", []):

        resource = entry.get("resource", {})

        if resource.get("resourceType") == "Patient":

            fhir_id = resource.get("id")
            gender = resource.get("gender")
            birth_date = resource.get("birthDate")

            name = "Unknown"

            names = resource.get("name", [])

            if names:
                first_name = " ".join(
                    names[0].get("given", [])
                )

                family_name = names[0].get(
                    "family", ""
                )

                name = f"{first_name} {family_name}".strip()

            return {
                "fhirId": fhir_id,
                "name": name,
                "gender": gender,
                "birthDate": birth_date
            }

    return None


def import_patient(file_path, patient_id):
    """
    Import one FHIR patient into MongoDB.
    """

    # 1. Load complete FHIR Bundle
    bundle = load_fhir_bundle(file_path)

    # 2. Extract patient metadata
    patient_data = extract_patient_data(bundle)

    if patient_data is None:
        raise ValueError("Patient resource not found.")

    # 3. Add our application-level Patient ID
    patient_data["patientId"] = patient_id

    # 4. Save metadata
    save_patient(patient_data)

    # 5. Save complete FHIR Bundle
    save_ehr(patient_id, bundle)

    return patient_data

def extract_relevant_ehr_data(bundle):
    """
    Extract clinically relevant resources from a FHIR Bundle.
    """

    relevant_data = {
        "patient": [],
        "conditions": [],
        "observations": [],
        "medications": [],
        "encounters": [],
        "procedures": [],
        "carePlans": []
    }

    for entry in bundle.get("entry", []):

        resource = entry.get("resource", {})

        resource_type = resource.get("resourceType")

        if resource_type == "Patient":
            relevant_data["patient"].append(resource)

        elif resource_type == "Condition":
            relevant_data["conditions"].append(resource)

        elif resource_type == "Observation":
            relevant_data["observations"].append(resource)

        elif resource_type in [
            "MedicationRequest",
            "MedicationStatement"
        ]:
            relevant_data["medications"].append(resource)

        elif resource_type == "Encounter":
            relevant_data["encounters"].append(resource)

        elif resource_type == "Procedure":
            relevant_data["procedures"].append(resource)

        elif resource_type == "CarePlan":
            relevant_data["carePlans"].append(resource)

    return relevant_data