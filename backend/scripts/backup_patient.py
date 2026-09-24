import sys
import os
import json

# Add backend directory to Python path
sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from app.database.database import db


PATIENT_ID = "PAT0001"


patient = db.ehr_data.find_one(
    {"patientId": PATIENT_ID}
)

if patient is None:
    print(f"Patient {PATIENT_ID} not found.")
    sys.exit(1)


# Remove MongoDB ObjectId because it isn't JSON serializable
patient.pop("_id", None)


backup_file = "data/PAT0001_backup.json"


with open(
    backup_file,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        patient,
        file,
        indent=4,
        default=str
    )


print(
    f"Backup created successfully: {backup_file}"
)