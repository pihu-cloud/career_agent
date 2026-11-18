"""
FastAPI Master Application Entry Point
Intelligent Career Pathway Navigator with Adaptive Skill-Gap Analysis
"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from backend.core.config import settings
from backend.core.logging import logger
from backend.db.init_db import init_db
from backend.services.ml_service import ml_service

# Middlewares
from backend.middleware.error_handler import add_exception_handlers
from backend.middleware.audit_log import AuditLogMiddleware
from backend.middleware.rate_limiter import RateLimiterMiddleware
from backend.middleware.sanitizer import SanitizerMiddleware

# Routers
from backend.api.auth import router as auth_router
from backend.api.profile import router as profile_router
from backend.api.resume import router as resume_router
from backend.api.academics import router as academics_router
from backend.api.progress import router as progress_router
from backend.api.notifications import router as notifications_router
from backend.api.health import router as health_router
from backend.api.admin import router as admin_router
from backend.api.recommendations import router as recommendations_router
from backend.api.resume_analysis import router as resume_analysis_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.app_name} v{settings.app_version}...")
    os.makedirs(settings.upload_dir, exist_ok=True)
    os.makedirs(os.path.join(settings.upload_dir, "resumes"), exist_ok=True)
    
    # Initialize DB schema & seed admin
    await init_db()
    
    # Ensure ML models are loaded
    ml_service.load_models()
    
    yield
    logger.info("Application shutdown completed.")

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Official Web Application for Intelligent Career Pathway Navigator with Adaptive Skill-Gap Analysis",
    lifespan=lifespan
)

# 1. Register Error Handlers
add_exception_handlers(app)

# 2. CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Custom Security & Monitoring Middlewares
app.add_middleware(RateLimiterMiddleware, rate_limit=settings.rate_limit_per_minute)
app.add_middleware(SanitizerMiddleware)
app.add_middleware(AuditLogMiddleware)

# 4. Include API Routers
app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(resume_router)
app.include_router(academics_router)
app.include_router(progress_router)
app.include_router(notifications_router)
app.include_router(health_router)
app.include_router(admin_router)
app.include_router(recommendations_router)
app.include_router(resume_analysis_router)

# 5. Serve Frontend Static Build if present
frontend_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "dist"))
if os.path.exists(frontend_dist):
    assets_dir = os.path.join(frontend_dist, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")
    app.mount("/app", StaticFiles(directory=frontend_dist, html=True), name="frontend")

@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")
