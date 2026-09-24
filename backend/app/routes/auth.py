from datetime import datetime, timedelta, timezone

import bcrypt
from jose import jwt
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.database.database import db


router = APIRouter(prefix="/auth", tags=["Authentication"])


SECRET_KEY = "CHANGE_THIS_SECRET_KEY"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

class SignupRequest(BaseModel):
    email: str
    password: str
    role: str

    # Patient fields
    name: str | None = None
    gender: str | None = None
    birthDate: str | None = None

    # Doctor fields
    specialization: str | None = None

class LoginRequest(BaseModel):
    email: str
    password: str


def create_access_token(data: dict):
    payload = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload.update({"exp": expire})

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


@router.post("/signup")
def signup(request: SignupRequest):

    # Validate role
    if request.role not in ["PATIENT", "DOCTOR"]:
        raise HTTPException(
            status_code=400,
            detail="Role must be PATIENT or DOCTOR"
        )

    # Check duplicate email
    existing_user = db.users.find_one({
        "email": request.email
    })

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    # -----------------------------
    # Generate next User ID
    # -----------------------------
    users = list(db.users.find({}, {"userId": 1}))

    max_user_number = 0

    for user in users:
        user_id = user.get("userId", "")

        if user_id.startswith("USR"):
            try:
                number = int(user_id.replace("USR", ""))
                max_user_number = max(max_user_number, number)
            except ValueError:
                pass

    user_id = f"USR{max_user_number + 1:03d}"

    # -----------------------------
    # Hash password
    # -----------------------------
    password_hash = bcrypt.hashpw(
        request.password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    # -----------------------------
    # PATIENT SIGNUP
    # -----------------------------
    if request.role == "PATIENT":

        if not request.name or not request.gender or not request.birthDate:
            raise HTTPException(
                status_code=400,
                detail="Name, gender and birthDate are required for patients"
            )

        # Generate patient ID
        patients = list(db.patients.find({}, {"patientId": 1}))

        max_patient_number = 0

        for patient in patients:
            patient_id = patient.get("patientId", "")

            if patient_id.startswith("PAT"):
                try:
                    number = int(patient_id.replace("PAT", ""))
                    max_patient_number = max(max_patient_number, number)
                except ValueError:
                    pass

        patient_id = f"PAT{max_patient_number + 1:04d}"

        # Create user
        user = {
            "userId": user_id,
            "email": request.email,
            "passwordHash": password_hash,
            "role": "PATIENT",
            "patientId": patient_id
        }

        db.users.insert_one(user)

        # Create patient profile
        patient_profile = {
            "patientId": patient_id,
            "userId": user_id,
            "name": request.name,
            "gender": request.gender,
            "birthDate": request.birthDate
        }

        db.patients.insert_one(patient_profile)

        return {
            "message": "Patient signup successful",
            "user": {
                "userId": user_id,
                "email": request.email,
                "role": "PATIENT",
                "patientId": patient_id
            }
        }

    # -----------------------------
    # DOCTOR SIGNUP
    # -----------------------------
    if not request.name or not request.specialization:
        raise HTTPException(
            status_code=400,
            detail="Name and specialization are required for doctors"
        )

    # Generate doctor ID
    doctors = list(db.doctors.find({}, {"doctorId": 1}))

    max_doctor_number = 0

    for doctor in doctors:
        doctor_id = doctor.get("doctorId", "")

        if doctor_id.startswith("DOC"):
            try:
                number = int(doctor_id.replace("DOC", ""))
                max_doctor_number = max(max_doctor_number, number)
            except ValueError:
                pass

    doctor_id = f"DOC{max_doctor_number + 1:03d}"

    # Create user
    user = {
        "userId": user_id,
        "email": request.email,
        "passwordHash": password_hash,
        "role": "DOCTOR",
        "doctorId": doctor_id
    }

    db.users.insert_one(user)

    # Create doctor profile
    doctor_profile = {
        "doctorId": doctor_id,
        "userId": user_id,
        "name": request.name,
        "specialization": request.specialization
    }

    db.doctors.insert_one(doctor_profile)

    return {
        "message": "Doctor signup successful",
        "user": {
            "userId": user_id,
            "email": request.email,
            "role": "DOCTOR",
            "doctorId": doctor_id
        }
    }

@router.post("/login")
def login(request: LoginRequest):

    user = db.users.find_one({
        "email": request.email
    })

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    password_valid = bcrypt.checkpw(
        request.password.encode("utf-8"),
        user["passwordHash"].encode("utf-8")
    )

    if not password_valid:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    token_data = {
        "sub": user["userId"],
        "role": user["role"]
    }

    token = create_access_token(token_data)

    return {
        "message": "Login successful",
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "userId": user["userId"],
            "role": user["role"],
            "patientId": user.get("patientId"),
            "doctorId": user.get("doctorId")
        }
    }