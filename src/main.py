import sentry_sdk
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse
from fastapi_versioning import VersionedFastAPI
from loguru import logger
from sqladmin import Admin
from starlette.middleware.base import BaseHTTPMiddleware

from src.admin.views import PatientAdmin, PatientRecordAdmin, UserAdmin
from src.auth.routers import auth_router, user_router
from src.patient.routers import patient_router
from src.patient_records.routers import patient_records_router

from .config import settings
from .database import async_engine
from .utils import get_api_key


sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
)


app = FastAPI(docs_url="/secure/docs", redoc_url=None, title="Clinic")

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


app.include_router(auth_router, tags=["AUTH"])
app.include_router(user_router, tags=["USER"])
app.include_router(patient_router, tags=["PATIENT"])
app.include_router(patient_records_router, tags=["PATIENT RECORDS"])


@app.get("/secure/docs", response_class=HTMLResponse)
async def get_docs(api_key: str = Depends(get_api_key)):
    return get_swagger_ui_html(openapi_url="/openapi.json", title="Clinic API Documentation")


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        logger.info(f"Входящий запрос: {request.method} {request.url}")

        response = await call_next(request)

        logger.info(f"Исходящий ответ: {response.status_code}")

        return response


app = VersionedFastAPI(
    app,
    version_format="{major}",
    prefix_format="/v{major}",
    middleware=[
        (
            CORSMiddleware,
            (),
            {
                "allow_origins": settings.CORS_ORIGINS,
                "allow_credentials": settings.CORS_CREDENTIALS,
                "allow_methods": settings.CORS_METHODS,
                "allow_headers": settings.CORS_HEADERS,
            },
        ),
        (LoggingMiddleware, (), {}),
    ],
)


admin = Admin(app, async_engine)

admin.add_view(UserAdmin)
admin.add_view(PatientAdmin)
admin.add_view(PatientRecordAdmin)
