from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .db import init_db
from .routers.questions import router as questions_router
from .routers.quizzes import router as quizzes_router
from .routers.import_export import router as import_export_router
from .routers.assist import router as assist_router

app = FastAPI(title="QUIZ_CREATOR", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register import/export before questions to avoid dynamic path conflicts
app.include_router(import_export_router, prefix="/api/questions", tags=["import-export"])
app.include_router(questions_router, prefix="/api/questions", tags=["questions"])
app.include_router(quizzes_router, prefix="/api/quizzes", tags=["quizzes"])
app.include_router(assist_router, prefix="/api/assist", tags=["assist"])

# Initialize DB at import time so tests have tables ready
init_db()


@app.get("/")
async def root():
    return {"project": "QUIZ_CREATOR", "organization": "YOUR_ORG", "ui_mode": "api-only"}