"""
FastAPI Backend Application Entry Point

This is the main entry point for the FastAPI backend that wraps
the existing Streamlit application logic.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
backend_dir = Path(__file__).resolve().parent
project_root = backend_dir.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
from contextlib import asynccontextmanager
import socketio

from backend.core.config import settings
from backend.core.database import engine, Base
from backend.middleware.error_handler import setup_error_handlers
from backend.core.api_documentation import custom_openapi_schema
from backend.core.websocket_manager import get_websocket_manager
from backend.middleware.websocket_auth import WebSocketAuthMiddleware
from backend.core.security_manager import setup_security, SecurityPresets

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    """
    # Startup
    logger.info("Starting FastAPI backend...")
    
    # Create database tables
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
    
    # Initialize WebSocket manager
    logger.info("WebSocket server initialized and ready")
    
    yield
    
    # Shutdown
    logger.info("Shutting down FastAPI backend...")
    logger.info("WebSocket connections closed")


# Create FastAPI application
app = FastAPI(
    title="Solar Calculator Pro API",
    description="Backend API for Solar Calculator Pro Desktop Application",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)

# Setup CORS middleware for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup error handlers
setup_error_handlers(app)

# Setup custom OpenAPI schema
app.openapi = lambda: custom_openapi_schema(app)

# Setup security features
# Use production preset for production, development preset for development
security_preset = SecurityPresets.production() if not settings.DEBUG else SecurityPresets.development()
security_manager = setup_security(app, **security_preset)


@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify the backend is running
    """
    return {
        "status": "healthy",
        "service": "Solar Calculator Pro Backend",
        "version": "1.0.0"
    }


@app.get("/security/status")
async def security_status():
    """
    Security status endpoint to check enabled security features
    """
    if hasattr(app.state, 'security_manager'):
        return app.state.security_manager.get_security_status()
    return {"error": "Security manager not initialized"}


@app.get("/")
async def root():
    """
    Root endpoint
    """
    return {
        "message": "Solar Calculator Pro Backend API",
        "docs": "/api/docs",
        "health": "/health"
    }


# Import and include API routers
from backend.api.v1 import data, auth, solar, products, crm, websocket, pdf_templates

app.include_router(data.router, prefix="/api/v1/data", tags=["Data Management"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(solar.router, prefix="/api/v1", tags=["Solar Calculator"])
app.include_router(products.router, prefix="/api/v1", tags=["Product Management"])
app.include_router(crm.router, prefix="/api/v1", tags=["CRM"])
app.include_router(websocket.router, prefix="/api/v1/websocket", tags=["WebSocket"])
app.include_router(pdf_templates.router, prefix="/api/v1", tags=["PDF Templates"])

# Additional routers will be added in subsequent tasks
# from backend.api.v1 import heatpump, pricing, pdf, admin
# app.include_router(heatpump.router, prefix="/api/v1/heatpump", tags=["Heat Pump"])
# ... etc

# Mount Socket.IO app
ws_manager = get_websocket_manager()
socket_app = socketio.ASGIApp(
    ws_manager.sio,
    other_asgi_app=app,
    socketio_path='/socket.io'
)

# Replace the app with socket_app for Socket.IO support
# Note: This should be the last thing in the file before __main__
app = socket_app


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
