from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from core.logging import logger

async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global Error handling request {request.method} {request.url}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred. Please try again later."}
    )

async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning(f"HTTP Error {exc.status_code} at {request.url}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )
