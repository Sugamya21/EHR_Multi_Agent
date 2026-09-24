import sys
import os

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from app.services.patient_import_service import import_patient


if __name__ == "__main__":

    file_path = (
        "data/synthea/"
        "Aaron697_Brekke496_2fa15bc7-8866-461a-9000-f739e425860a (3).json"
    )

    patient = import_patient(
        file_path,
        "PAT0001"
    )

    print("\nPatient imported successfully!")

    print("Patient ID :", patient["patientId"])
    print("FHIR ID    :", patient["fhirId"])
    print("Name       :", patient["name"])
    print("Gender     :", patient["gender"])
    print("Birth Date :", patient["birthDate"])