from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from sqladmin import Admin

from src.admin.views import PatientAdmin, PatientRecordAdmin, UserAdmin
from src.auth.routers import auth_router, user_router
from src.patient.routers import patient_router
from src.patient_records.routers import patient_records_router

from .config import settings
from .database import async_engine


app = FastAPI(docs_url="/secure/docs", redoc_url=None)

if settings.MODE != "TEST":
    logger.add(
        "critical_logs.log",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
        encoding="utf-8",
        level="CRITICAL",
        filter=lambda record: record["level"].name == "CRITICAL",
    )

    logger.add(
        "common_logs.log",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
        encoding="utf-8",
        rotation="500 MB",
        retention="7 days",
        level="INFO",
        filter=lambda record: record["level"].name == "INFO",
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_CREDENTIALS,
    allow_methods=settings.CORS_METHODS,
    allow_headers=settings.CORS_HEADERS,
)


app.include_router(auth_router, tags=["AUTH"])
app.include_router(user_router, tags=["USER"])
app.include_router(patient_router, tags=["PATIENT"])
app.include_router(patient_records_router, tags=["PATIENT RECORDS"])


admin = Admin(app, async_engine)

admin.add_view(UserAdmin)
admin.add_view(PatientAdmin)
admin.add_view(PatientRecordAdmin)
