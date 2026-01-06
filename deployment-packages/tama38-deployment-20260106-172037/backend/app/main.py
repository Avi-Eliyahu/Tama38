"""
TAMA38 Backend Application
Main FastAPI application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import setup_logging
from app.api.middleware import RequestIDMiddleware
from app.api.v1 import auth, projects, buildings, units, owners, wizard, interactions, documents, approvals, majority, tasks, dashboard, whatsapp, files, agents, reports, alerts, users

# Setup logging first
setup_logging()

app = FastAPI(
    title="TAMA38 API",
    description="Urban Renewal Management Platform API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request ID middleware
app.add_middleware(RequestIDMiddleware)

# Include routers
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(projects.router, prefix=settings.API_V1_PREFIX)
app.include_router(buildings.router, prefix=settings.API_V1_PREFIX)
app.include_router(units.router, prefix=settings.API_V1_PREFIX)
app.include_router(owners.router, prefix=settings.API_V1_PREFIX)
app.include_router(wizard.router, prefix=settings.API_V1_PREFIX)
app.include_router(interactions.router, prefix=settings.API_V1_PREFIX)
app.include_router(documents.router, prefix=settings.API_V1_PREFIX)
app.include_router(approvals.router, prefix=settings.API_V1_PREFIX)
app.include_router(majority.router, prefix=settings.API_V1_PREFIX)
app.include_router(tasks.router, prefix=settings.API_V1_PREFIX)
app.include_router(dashboard.router, prefix=settings.API_V1_PREFIX)
app.include_router(whatsapp.router, prefix=settings.API_V1_PREFIX)
app.include_router(files.router, prefix=settings.API_V1_PREFIX)
app.include_router(agents.router, prefix=settings.API_V1_PREFIX)
app.include_router(reports.router, prefix=settings.API_V1_PREFIX)
app.include_router(alerts.router, prefix=settings.API_V1_PREFIX)
app.include_router(users.router, prefix=settings.API_V1_PREFIX)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0.0"}


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "TAMA38 API",
        "version": "1.0.0",
        "docs": "/docs",
    }

