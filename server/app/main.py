from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
from app.core.config import settings
from app.routers import upload, grading, results, auth  # Added auth

# Initialize FastAPI app
app = FastAPI(
    title="Exam Autograding API",
    description="AI-powered exam grading system with authentication",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create upload directory
os.makedirs("uploads", exist_ok=True)

# Mount static files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])  # Added auth
app.include_router(upload.router, prefix="/api/v1", tags=["Upload"])
app.include_router(grading.router, prefix="/api/v1", tags=["Grading"])
app.include_router(results.router, prefix="/api/v1", tags=["Results"])

@app.get("/")
async def root():
    return {"message": "Exam Autograding API", "status": "running", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )