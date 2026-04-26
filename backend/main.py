from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from routes.resume import router as resume_router
from core.config import settings
from core.exceptions import global_exception_handler, http_exception_handler
from core.logging import logger

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="Interview Magnet API", version="2.0.0")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:3000", "http://127.0.0.1:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(resume_router, prefix="/api")

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up Interview Magnet API")

@app.get("/")
async def root():
    return {"message": "Resume Builder API is running securely."}

@app.get("/health")
async def health():
    return {"status": "healthy"}