from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .db.session import get_db, engine
from .db import models
from .core.config import settings

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="NDA Validator API",
    description="API for validating and analyzing NDA documents",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Import and include routers
from .api.endpoints import documents, feedback, validation
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
app.include_router(feedback.router, prefix="/api/feedback", tags=["feedback"])
app.include_router(validation.router, prefix="/api/validation", tags=["validation"]) 