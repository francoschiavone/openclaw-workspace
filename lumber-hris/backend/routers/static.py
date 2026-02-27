"""Serve the built frontend from FastAPI"""
import os
from fastapi import APIRouter
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

static_router = APIRouter()

DIST_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend", "dist")


def mount_static(app):
    """Mount frontend static files to the FastAPI app."""
    if os.path.isdir(DIST_DIR):
        # Serve assets directory
        assets_dir = os.path.join(DIST_DIR, "assets")
        if os.path.isdir(assets_dir):
            app.mount("/assets", StaticFiles(directory=assets_dir), name="static-assets")
        
        # Catch-all for SPA routing
        @app.get("/{full_path:path}")
        async def serve_spa(full_path: str):
            # Don't catch API routes
            if full_path.startswith("api/") or full_path == "docs" or full_path == "openapi.json":
                return None
            
            # Try to serve the exact file first
            file_path = os.path.join(DIST_DIR, full_path)
            if os.path.isfile(file_path):
                return FileResponse(file_path)
            
            # Otherwise return index.html for SPA routing
            index_path = os.path.join(DIST_DIR, "index.html")
            if os.path.isfile(index_path):
                return FileResponse(index_path)
            
            return HTMLResponse("<h1>Frontend not built</h1>", status_code=404)
