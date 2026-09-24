from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.database.database import db
from app.auth.dependencies import get_current_user


router = APIRouter(
    prefix="/relationships",
    tags=["Doctor-Patient Relationships"]
)


class DoctorRequest(BaseModel):
    doctorId: str


# --------------------------------------------------
# PATIENT → REQUEST A DOCTOR
# --------------------------------------------------

@router.post("/request")
def request_doctor(
    request: DoctorRequest,
    current_user: dict = Depends(get_current_user)
):

    # Only patients can send requests
    if current_user["role"] != "PATIENT":
        raise HTTPException(
            status_code=403,
            detail="Only patients can request a doctor"
        )

    # Find logged-in patient
    user = db.users.find_one({
        "userId": current_user["userId"]
    })

    if not user or not user.get("patientId"):
        raise HTTPException(
            status_code=404,
            detail="Patient profile not found"
        )

    patient_id = user["patientId"]

    # Check doctor exists
    doctor = db.doctors.find_one({
        "doctorId": request.doctorId
    })

    if not doctor:
        raise HTTPException(
            status_code=404,
            detail="Doctor not found"
        )

    # Check existing relationship
    existing = db.doctor_patient.find_one({
        "doctorId": request.doctorId,
        "patientId": patient_id
    })

    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Relationship already exists with status: {existing['status']}"
        )

    relationship = {
        "doctorId": request.doctorId,
        "patientId": patient_id,
        "status": "PENDING"
    }

    db.doctor_patient.insert_one(relationship)

    return {
        "message": "Doctor request sent successfully",
        "doctorId": request.doctorId,
        "patientId": patient_id,
        "status": "PENDING"
    }


# --------------------------------------------------
# DOCTOR → VIEW PENDING REQUESTS
# --------------------------------------------------

@router.get("/doctor/pending")
def get_pending_requests(
    current_user: dict = Depends(get_current_user)
):

    if current_user["role"] != "DOCTOR":
        raise HTTPException(
            status_code=403,
            detail="Only doctors can view requests"
        )

    user = db.users.find_one({
        "userId": current_user["userId"]
    })

    if not user or not user.get("doctorId"):
        raise HTTPException(
            status_code=404,
            detail="Doctor profile not found"
        )

    doctor_id = user["doctorId"]

    requests = list(
        db.doctor_patient.find({
            "doctorId": doctor_id,
            "status": "PENDING"
        })
    )

    for request in requests:
        request["_id"] = str(request["_id"])

    return {
        "doctorId": doctor_id,
        "requests": requests
    }


@router.get("/doctor/active")
def get_active_patients(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "DOCTOR":
        raise HTTPException(
            status_code=403,
            detail="Only doctors can view active patients"
        )

    user = db.users.find_one({"userId": current_user["userId"]})

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    doctor_id = user.get("doctorId")

    if not doctor_id:
        raise HTTPException(
            status_code=400,
            detail="Doctor profile not found"
        )

    relationships = list(
        db.doctor_patient.find(
            {
                "doctorId": doctor_id,
                "status": "ACTIVE"
            },
            {
                "_id": 0
            }
        )
    )

    patients = []

    for relationship in relationships:
        patient_id = relationship.get("patientId")

        patient = db.patients.find_one(
            {"patientId": patient_id},
            {"_id": 0}
        )

        if patient:
            patients.append({
                "patientId": patient.get("patientId"),
                "name": patient.get("name", "Unknown Patient"),
                "gender": patient.get("gender", ""),
                "birthDate": patient.get("birthDate", ""),
                "status": "ACTIVE"
            })

    return {
        "doctorId": doctor_id,
        "patients": patients
    }

@router.get("/doctors")
def get_doctors(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "PATIENT":
        raise HTTPException(
            status_code=403,
            detail="Only patients can view doctors"
        )

    user = db.users.find_one({
        "userId": current_user["userId"]
    })

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    patient_id = user.get("patientId")

    if not patient_id:
        raise HTTPException(
            status_code=400,
            detail="Patient profile not found"
        )

    doctors = list(
        db.doctors.find(
            {},
            {
                "_id": 0,
                "doctorId": 1,
                "name": 1,
                "specialization": 1
            }
        )
    )

    result = []

    for doctor in doctors:
        relationship = db.doctor_patient.find_one({
            "doctorId": doctor.get("doctorId"),
            "patientId": patient_id
        })

        result.append({
            "doctorId": doctor.get("doctorId"),
            "name": doctor.get("name", "Doctor"),
            "specialization": doctor.get(
                "specialization",
                "General Medicine"
            ),
            "status": (
                relationship.get("status")
                if relationship
                else "NOT_CONNECTED"
            )
        })

    return {
        "patientId": patient_id,
        "doctors": result
    }

# --------------------------------------------------
# DOCTOR → ACCEPT PATIENT
# --------------------------------------------------

@router.put("/accept/{patient_id}")
def accept_patient(
    patient_id: str,
    current_user: dict = Depends(get_current_user)
):

    if current_user["role"] != "DOCTOR":
        raise HTTPException(
            status_code=403,
            detail="Only doctors can accept patients"
        )

    user = db.users.find_one({
        "userId": current_user["userId"]
    })

    if not user or not user.get("doctorId"):
        raise HTTPException(
            status_code=404,
            detail="Doctor profile not found"
        )

    doctor_id = user["doctorId"]

    relationship = db.doctor_patient.find_one({
        "doctorId": doctor_id,
        "patientId": patient_id,
        "status": "PENDING"
    })

    if not relationship:
        raise HTTPException(
            status_code=404,
            detail="Pending patient request not found"
        )

    db.doctor_patient.update_one(
        {
            "doctorId": doctor_id,
            "patientId": patient_id,
            "status": "PENDING"
        },
        {
            "$set": {
                "status": "ACTIVE"
            }
        }
    )

    return {
        "message": "Patient accepted successfully",
        "doctorId": doctor_id,
        "patientId": patient_id,
        "status": "ACTIVE"
    }

