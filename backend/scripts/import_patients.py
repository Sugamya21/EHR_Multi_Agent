import os
import sys

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from app.services.patient_import_service import import_patient
from app.database.database import db


DATA_FOLDER = "data/synthea"
TARGET_PATIENTS = 15


def get_next_patient_number():
    """Find the next available application Patient ID."""

    patients = db.patients.find(
        {},
        {"patientId": 1}
    )

    max_number = 0

    for patient in patients:

        patient_id = patient.get("patientId", "")

        if patient_id.startswith("PAT"):

            try:
                number = int(patient_id[3:])
                max_number = max(max_number, number)

            except ValueError:
                pass

    return max_number + 1


def get_existing_patient_count():
    return db.patients.count_documents({})


if __name__ == "__main__":

    existing_count = get_existing_patient_count()

    if existing_count >= TARGET_PATIENTS:
        print(
            f"Database already contains "
            f"{existing_count} patients."
        )
        sys.exit(0)

    next_number = get_next_patient_number()

    files = [
        file
        for file in os.listdir(DATA_FOLDER)
        if file.lower().endswith(".json")
    ]

    files.sort()

    patients_to_import = (
        TARGET_PATIENTS - existing_count
    )

    imported_count = 0

    for file_name in files:

        if imported_count >= patients_to_import:
            break

        patient_id = f"PAT{next_number:04d}"

        file_path = os.path.join(
            DATA_FOLDER,
            file_name
        )

        try:

            patient = import_patient(
                file_path,
                patient_id
            )

            print(
                f"Imported {patient_id} - "
                f"{patient['name']}"
            )

            imported_count += 1
            next_number += 1

        except Exception as e:

            print(
                f"Failed to import {file_name}: {e}"
            )

    print(
        f"\nImport completed. "
        f"Imported {imported_count} new patients."
    )