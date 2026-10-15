import asyncio
import contextlib
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import settings
from app.db import engine
from app.routers import admin, auth, catalog, chat
from app.services.embeddings import get_product_embeddings

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("app")


async def _warm_embeddings() -> None:
    try:
        await get_product_embeddings()
    except Exception:
        logger.exception("Failed to initialize embeddings")


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    # Embeddings are built in the background so startup isn't blocked on the LLM API.
    warmup = asyncio.create_task(_warm_embeddings()) if settings.openrouter_api_key else None
    if warmup is None:
        logger.warning("OPENROUTER_API_KEY not set; chat will be unavailable")
    yield
    if warmup is not None:
        warmup.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await warmup
    await engine.dispose()


app = FastAPI(title="Wardrobe Catalog API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.frontend_origin.split(",")],
    allow_methods=["*"],
    allow_headers=["*"],
)

settings.uploads_dir.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.uploads_dir), name="uploads")

VALIDATION_MESSAGES = {"body": "Invalid body", "query": "Invalid query", "path": "Invalid id"}


@app.exception_handler(RequestValidationError)
async def validation_error_handler(_request: Request, exc: RequestValidationError) -> JSONResponse:
    """400 with `{message, issues}`, the error shape the frontend already handles."""
    errors = exc.errors()
    location = errors[0]["loc"][0] if errors and errors[0].get("loc") else "body"
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "message": VALIDATION_MESSAGES.get(location, "Invalid request"),
            "issues": jsonable_encoder(
                [{"path": list(e["loc"]), "message": e["msg"], "type": e["type"]} for e in errors]
            ),
        },
    )


@app.exception_handler(StarletteHTTPException)
async def http_error_handler(_request: Request, exc: StarletteHTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code, content={"message": exc.detail}, headers=exc.headers
    )


@app.exception_handler(Exception)
async def unhandled_error_handler(_request: Request, exc: Exception) -> JSONResponse:
    logger.error("Unhandled error", exc_info=exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": "Internal server error"}
    )


@app.get("/api/health", tags=["health"])
async def health() -> dict[str, bool]:
    return {"ok": True}


app.include_router(auth.router)
app.include_router(catalog.router)
app.include_router(admin.router)
app.include_router(chat.router)
