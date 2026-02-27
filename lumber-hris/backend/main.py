"""
Lumber HRIS API — Main Application Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: create database tables."""
    try:
        from backend.models.database import create_tables
        create_tables()
        print("✅ Database tables created")
    except Exception as e:
        print(f"⚠️ Could not create tables: {e}")
    yield


app = FastAPI(
    title="Lumber HRIS API",
    version="1.0.0",
    description="Human Resource Information System for Summit Construction Group",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routers with graceful fallback
def _include(module_path: str, router_name: str, prefix: str, tags: list):
    try:
        mod = __import__(module_path, fromlist=[router_name])
        app.include_router(getattr(mod, router_name), prefix=prefix, tags=tags)
    except (ImportError, AttributeError) as e:
        print(f"⚠️ Router {prefix} not loaded: {e}")

_include("backend.routers.auth", "auth_router", "/api/auth", ["Authentication"])
_include("backend.routers.employees", "employee_router", "/api/employees", ["Employees"])
_include("backend.routers.departments", "department_router", "/api/departments", ["Departments"])
_include("backend.routers.org_chart", "org_chart_router", "/api/org-chart", ["Org Chart"])
_include("backend.routers.performance", "performance_router", "/api/performance", ["Performance"])
_include("backend.routers.lms", "lms_router", "/api/lms", ["LMS"])
_include("backend.routers.analytics", "analytics_router", "/api/analytics", ["Analytics"])
_include("backend.routers.dashboard", "dashboard_router", "/api/dashboard", ["Dashboard"])


@app.get("/api")
async def api_root():
    return {"message": "Lumber HRIS API", "version": "1.0.0", "docs": "/docs"}


@app.get("/api/health")
async def health():
    return {"status": "ok"}


# Mount frontend static files (MUST be last — catch-all route)
try:
    from backend.routers.static import mount_static
    mount_static(app)
    print("✅ Frontend static files mounted")
except Exception as e:
    print(f"⚠️ Frontend not mounted: {e}")
