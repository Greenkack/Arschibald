"""
FastAPI Backend Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Import API routers
from api.v1 import system_settings, database

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title=os.getenv("APP_NAME", "Solar Calculator Pro"),
    version=os.getenv("APP_VERSION", "1.0.0"),
    description="Backend API for Solar Calculator Pro Desktop Application",
)

# Configure CORS
origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(system_settings.router, prefix="/api/v1")
app.include_router(database.router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": os.getenv("APP_NAME", "Solar Calculator Pro"),
        "version": os.getenv("APP_VERSION", "1.0.0"),
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Solar Calculator Pro API",
        "version": os.getenv("APP_VERSION", "1.0.0"),
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("DEBUG", "True") == "True",
    )
