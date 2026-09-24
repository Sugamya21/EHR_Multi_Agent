from fastapi import APIRouter
from app.database.database import db

router = APIRouter()

@router.get("/test-db")
def test_db():
    try:
        db.command("ping")

        return {
            "status": "success",
            "message": "MongoDB Connected Successfully!"
        }

    except Exception as e:

        return {
            "status": "error",
            "message": str(e)
        }