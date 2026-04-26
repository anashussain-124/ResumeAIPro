from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import os
from app.config import settings
from app.database import init_indexes
from app.routes.resumes import router as resume_router

app = FastAPI(
    title="Resume Builder API",
    description="AI-powered resume optimization SaaS",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(resume_router, prefix="/api", tags=["Resume"])

@app.on_event("startup")
async def startup_event():
    try:
        init_indexes()
        print("Database indexes created")
    except Exception as e:
        print(f"Database connection note: {e}")

@app.get("/")
async def root():
    return {
        "message": "Resume Builder API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "resume-builder-api"}

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "detail": str(exc) if settings.razorpay_key_id else "Configuration error"
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)