from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app.middleware.cors import setup_cors
from app.middleware.auth import AuthMiddleware
from app.routers import upload, grading, results
from app.core.config import settings

app = FastAPI(
    title="AutoGrader API",
    description="AI-powered exam autograding system",
    version="1.0.0"
)

# Setup CORS
setup_cors(app)

# Add custom auth middleware
app.add_middleware(AuthMiddleware)

# Include routers
app.include_router(upload.router, prefix="/api/v1")
app.include_router(grading.router, prefix="/api/v1")
app.include_router(results.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "AutoGrader API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "main":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)