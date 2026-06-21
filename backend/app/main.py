from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.db import engine
from app.database.base import Base

from app.models.repository import Repository
from app.api.repositories import router as repository_router
from app.models.commit import Commit
from app.models.file import File


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Software Archaeologist",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(repository_router)


@app.get("/")
def root():
    return {
        "message": "Software Archaeologist API Running"
    }