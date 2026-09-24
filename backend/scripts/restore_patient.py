import sys
import os
import json

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from app.database.database import db


PATIENT_ID = "PAT0001"

BACKUP_FILE = "data/PAT0001_backup.json"


with open(
    BACKUP_FILE,
    "r",
    encoding="utf-8"
) as file:
    backup = json.load(file)


result = db.ehr_data.update_one(
    {"patientId": PATIENT_ID},
    {
        "$set": {
            "fhirBundle": backup["fhirBundle"]
        }
    }
)


if result.modified_count > 0:
    print(
        f"{PATIENT_ID} restored successfully."
    )
else:
    print(
        "Restore did not modify the document."
    )