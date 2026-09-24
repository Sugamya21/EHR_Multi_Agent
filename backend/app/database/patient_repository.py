from app.database.database import db


def save_patient(patient_data):
    """
    Save basic patient information in the patients collection.
    """

    result = db.patients.insert_one(patient_data)

    return result.inserted_id


def save_ehr(patient_id, bundle):
    """
    Save the complete FHIR Bundle for a patient.
    """

    ehr_document = {
        "patientId": patient_id,
        "version": 1,
        "fhirBundle": bundle
    }

    result = db.ehr_data.insert_one(ehr_document)

    return result.inserted_id


def get_patient(patient_id):
    """
    Retrieve patient metadata using our application Patient ID.
    """

    return db.patients.find_one(
        {"patientId": patient_id},
        {"_id": 0}
    )


def get_ehr(patient_id):
    """
    Retrieve the patient's complete EHR.
    """

    return db.ehr_data.find_one(
        {"patientId": patient_id},
        {"_id": 0}
    )

def update_ehr(patient_id, updated_bundle):
    """
    Replace the patient's current FHIR Bundle
    with the updated Bundle.
    """

    result = db.ehr_data.update_one(
        {"patientId": patient_id},
        {
            "$set": {
                "fhirBundle": updated_bundle
            }
        }
    )

    return result.modified_count > 0

