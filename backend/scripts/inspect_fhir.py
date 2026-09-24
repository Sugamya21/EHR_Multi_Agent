import sys
import os

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from app.services.patient_import_service import (
    load_fhir_bundle,
    extract_patient_data
)


if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Usage:")
        print("python scripts/inspect_fhir.py <path-to-json-file>")
        sys.exit(1)

    file_path = sys.argv[1]

    bundle = load_fhir_bundle(file_path)

    patient = extract_patient_data(bundle)

    if patient is None:
        print("Patient resource not found.")
    else:
        print("\n----- Patient Information -----")

        print("FHIR ID    :", patient["fhirId"])
        print("Name       :", patient["name"])
        print("Gender     :", patient["gender"])
        print("Birth Date :", patient["birthDate"])