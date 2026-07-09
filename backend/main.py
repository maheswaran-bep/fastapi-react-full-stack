"""
=============================================================================
MAIN.PY - FastAPI Application Entry Point
=============================================================================

FastAPI backend for the React User CRUD application.

Development frontend:
    http://localhost:5173

EC2 frontend:
    http://13.235.113.90:5173

Backend:
    http://13.235.113.90:8000

Swagger docs:
    http://13.235.113.90:8000/docs
=============================================================================
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import users


# -----------------------------------------------------------------------------
# CREATE FASTAPI APPLICATION
# -----------------------------------------------------------------------------

app = FastAPI(
    title="FastAPI React Full Stack API",
    description="Backend API for React User CRUD application",
    version="1.0.0",
)


# -----------------------------------------------------------------------------
# CORS CONFIGURATION
# -----------------------------------------------------------------------------

allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:8081",
    "http://13.235.113.90:5173",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------------------------------------------------------
# ROOT ENDPOINT
# -----------------------------------------------------------------------------

@app.get("/")
def root():
    return {
        "message": "FastAPI backend is running",
        "status": "healthy",
    }


# -----------------------------------------------------------------------------
# HEALTH CHECK ENDPOINT
# -----------------------------------------------------------------------------

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "fastapi-react-full-stack-backend",
    }


# -----------------------------------------------------------------------------
# REGISTER ROUTERS
# -----------------------------------------------------------------------------

app.include_router(
    users.router,
    prefix="/api/users",
    tags=["users"],
)
