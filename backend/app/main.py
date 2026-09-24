from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.test import router as test_router
from app.routes.ehr import router as ehr_router
from app.routes.summary import router as summary_router
from app.routes.auth import router as auth_router
from app.routes.relationships import router as relationships_router


app = FastAPI(
    title="EHR Multi-Agent API",
    version="1.0"
)


# Allow React frontend to communicate with FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(test_router)
app.include_router(ehr_router)
app.include_router(summary_router)
app.include_router(auth_router)
app.include_router(relationships_router)


@app.get("/")
def home():
    return {
        "message": "EHR Multi-Agent Backend Running 🚀"
    }