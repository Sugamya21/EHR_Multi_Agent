import os
import shutil
import uuid

from app.auth.dependencies import get_current_user
from fastapi import Depends
from fastapi import Depends, HTTPException
from app.database.database import db

from fastapi import (
    APIRouter,
    HTTPException,
    UploadFile,
    File
)

from app.services.ehr_service import (
    get_patient_ehr_sections
)

from scripts.extract_pdf import (
    extract_text
)

from app.services.gemini_service import (
    extract_ehr_from_text
)

from app.utils.ehr_validator import (
    validate_ehr_data
)

from app.agents.ehr_update_agent import (
    update_patient_ehr
)

from app.agents.ehr_analysis_agent import (
    analyze_patient
)


router = APIRouter(
    prefix="/patients",
    tags=["EHR"]
)


# ============================================================
# Existing EHR endpoint
# ============================================================

@router.get("/{patient_id}/ehr")
def get_ehr(
    patient_id: str,
    current_user: dict = Depends(get_current_user)
):

    # -----------------------------------------
    # Get logged-in user's database record
    # -----------------------------------------
    user = db.users.find_one({
        "userId": current_user["userId"]
    })

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # -----------------------------------------
    # PATIENT ACCESS
    # -----------------------------------------
    if current_user["role"] == "PATIENT":

        # Patient can only access their own EHR
        if user.get("patientId") != patient_id:
            raise HTTPException(
                status_code=403,
                detail="You can only access your own EHR"
            )

    # -----------------------------------------
    # DOCTOR ACCESS
    # -----------------------------------------
    elif current_user["role"] == "DOCTOR":

        doctor_id = user.get("doctorId")

        if not doctor_id:
            raise HTTPException(
                status_code=404,
                detail="Doctor profile not found"
            )

        # Doctor must have an ACTIVE relationship
        relationship = db.doctor_patient.find_one({
            "doctorId": doctor_id,
            "patientId": patient_id,
            "status": "ACTIVE"
        })

        if not relationship:
            raise HTTPException(
                status_code=403,
                detail="You are not authorized to access this patient's EHR"
            )

    # -----------------------------------------
    # Unknown role
    # -----------------------------------------
    else:
        raise HTTPException(
            status_code=403,
            detail="Invalid user role"
        )

    # -----------------------------------------
    # Authorized → return EHR
    # -----------------------------------------
    return get_patient_ehr_sections(patient_id)

# ============================================================
# Upload Medical Report
# ============================================================

@router.post("/{patient_id}/upload-report")
async def upload_medical_report(
    patient_id: str,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):

        # --------------------------------------------------------
    # Authorization
    # --------------------------------------------------------

    user = db.users.find_one({
        "userId": current_user["userId"]
    })

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # Patient can upload only to their own EHR
    if current_user["role"] == "PATIENT":

        if user.get("patientId") != patient_id:
            raise HTTPException(
                status_code=403,
                detail="You can only upload reports to your own EHR"
            )

    # Doctor can upload only for an ACTIVE patient
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
                detail="You are not authorized to upload a report for this patient"
            )

    else:
        raise HTTPException(
            status_code=403,
            detail="Invalid user role"
        )

    # --------------------------------------------------------
    # 1. Validate file
    # --------------------------------------------------------

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file provided."
        )

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported."
        )


    # --------------------------------------------------------
    # 2. Save uploaded PDF temporarily
    # --------------------------------------------------------

    os.makedirs(
        "app/uploads",
        exist_ok=True
    )

    temp_filename = (
        f"{uuid.uuid4()}_{file.filename}"
    )

    pdf_path = os.path.join(
        "app/uploads",
        temp_filename
    )


    try:

        with open(
            pdf_path,
            "wb"
        ) as buffer:

            shutil.copyfileobj(
                file.file,
                buffer
            )


        # ----------------------------------------------------
        # 3. Extract PDF text
        # ----------------------------------------------------

        pdf_text = extract_text(
            pdf_path
        )

        if not pdf_text.strip():

            raise HTTPException(
                status_code=400,
                detail="Could not extract text from PDF."
            )


        # ----------------------------------------------------
        # 4. Gemini structured extraction
        # ----------------------------------------------------

        extracted_data = extract_ehr_from_text(
            pdf_text
        )


        # ----------------------------------------------------
        # 5. Validate extracted EHR
        # ----------------------------------------------------

        is_valid, errors = validate_ehr_data(
            extracted_data
        )

        if not is_valid:

            raise HTTPException(
                status_code=400,
                detail={
                    "message": "Extracted EHR data is invalid.",
                    "errors": errors
                }
            )


        # ----------------------------------------------------
        # 6. Patient ID safety check
        # ----------------------------------------------------

        extracted_patient_id = (
            extracted_data.get(
                "patientId",
                ""
            )
        )

        if (
            extracted_patient_id
            and extracted_patient_id != patient_id
        ):

            raise HTTPException(
                status_code=400,
                detail={
                    "message": "Patient ID mismatch.",
                    "selectedPatientId": patient_id,
                    "pdfPatientId": extracted_patient_id
                }
            )


        # ----------------------------------------------------
        # 7. Update patient's EHR
        # ----------------------------------------------------

        update_result = update_patient_ehr(
            patient_id,
            extracted_data,
            dry_run=False
        )


        # ----------------------------------------------------
        # 8. Generate updated summary
        # ----------------------------------------------------

        summary = analyze_patient(
            patient_id
        )


        # ----------------------------------------------------
        # 9. Return response to frontend
        # ----------------------------------------------------

        return {
            "success": True,
            "patientId": patient_id,
            "fileName": file.filename,
            "addedResources": update_result.get(
                "addedResources",
                []
            ),
            "skippedResources": update_result.get(
                "skippedResources",
                []
            ),
            "summary": summary
        }


    except HTTPException:
        raise


    except ValueError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Failed to process medical report: {str(e)}"
        )


    finally:

        # ----------------------------------------------------
        # 10. Remove temporary PDF
        # ----------------------------------------------------

        if os.path.exists(pdf_path):

            os.remove(
                pdf_path
            )