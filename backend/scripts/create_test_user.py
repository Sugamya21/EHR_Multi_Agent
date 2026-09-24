import bcrypt

from app.database.database import db


password = "Test@123"

password_hash = bcrypt.hashpw(
    password.encode("utf-8"),
    bcrypt.gensalt()
).decode("utf-8")


user = {
    "userId": "USR001",
    "email": "patient@test.com",
    "passwordHash": password_hash,
    "role": "PATIENT",
    "patientId": "PAT0001"
}


result = db.users.update_one(
    {"email": user["email"]},
    {"$set": user},
    upsert=True
)

print("Test user created/updated.")
print("Email:", user["email"])
print("Password:", password)
print("MongoDB result:", result.upserted_id)