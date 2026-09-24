import sys
import os

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from app.database.database import db


result = db.ehr_data.update_one(
    {"patientId": "PAT0001"},
    {
        "$pull": {
            "fhirBundle.entry": {
                "resource.id": "dummy-hypertension-001"
            }
        }
    }
)

print("Modified documents:", result.modified_count)