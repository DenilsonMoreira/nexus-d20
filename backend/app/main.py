from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.errors import AppError, app_error_handler
from app.core.operations import OperationsMiddleware, prometheus_metrics


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    yield


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="API e motor de regras determinístico do Nexus d20.",
    lifespan=lifespan,
)
app.add_exception_handler(AppError, app_error_handler)  # type: ignore[arg-type]
app.add_middleware(OperationsMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok", "service": "nexus-d20-api"}


@app.get("/metrics", include_in_schema=False, response_class=PlainTextResponse)
def metrics(authorization: str | None = Header(default=None)) -> PlainTextResponse:
    if settings.secure_cookies and not settings.metrics_token:
        return PlainTextResponse("not found\n", status_code=404)
    if settings.metrics_token and authorization != f"Bearer {settings.metrics_token}":
        return PlainTextResponse("not found\n", status_code=404)
    return PlainTextResponse(prometheus_metrics(), media_type="text/plain; version=0.0.4")


app.include_router(api_router, prefix="/api/v1")
