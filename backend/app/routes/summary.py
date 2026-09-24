from fastapi import APIRouter, HTTPException, Depends
from app.auth.dependencies import get_current_user
from app.database.database import db
from app.agents.summary_orchestrator import generate_patient_summary

router = APIRouter(
    prefix="/patients",
    tags=["AI Summary"]
)

@router.post("/{patient_id}/summary")
def generate_summary(
    patient_id: str,
    current_user: dict = Depends(get_current_user)
):
    user = db.users.find_one({
        "userId": current_user["userId"]
    })

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if current_user["role"] == "PATIENT":
        if user.get("patientId") != patient_id:
            raise HTTPException(
                status_code=403,
                detail="You can only generate a summary for your own EHR"
            )

    elif current_user["role"] == "DOCTOR":
        doctor_id = user.get("doctorId")

        if not doctor_id:
            raise HTTPException(
                status_code=404,
                detail="Doctor profile not found"
            )

        relationship = db.doctor_patient.find_one({
            "doctorId": doctor_id,
            "patientId": patient_id,
            "status": "ACTIVE"
        })

        if not relationship:
            raise HTTPException(
                status_code=403,
                detail="You are not authorized to generate a summary for this patient"
            )

    else:
        raise HTTPException(
            status_code=403,
            detail="Invalid user role"
        )

    try:
        summary = generate_patient_summary(patient_id)

        return {
            "patientId": patient_id,
            "summary": summary
        }

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate summary: {str(e)}"
        )