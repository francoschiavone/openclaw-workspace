"""
Digital Twins Platform - FastAPI Backend
Provides a REST API layer on top of Eclipse Ditto
"""

import asyncio
import json
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx
import structlog
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    FastAPI,
    HTTPException,
    Query,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings

# ============================================
# Configuration
# ============================================


class Settings(BaseSettings):
    """Application settings from environment variables"""

    ditto_api_url: str = "http://localhost:8080"
    ditto_ws_url: str = "ws://localhost:8081"
    ditto_devops_user: str = "devops"
    ditto_devops_password: str = "dittoPwd"
    mqtt_broker_url: str = "mqtt://localhost:1883"
    log_level: str = "INFO"

    model_config = {"env_file": ".env", "case_sensitive": False}


settings = Settings()

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
)

logger = structlog.get_logger()
logging.basicConfig(level=getattr(logging, settings.log_level))


# ============================================
# Ditto API Client
# ============================================


class DittoClient:
    """Client for interacting with Eclipse Ditto HTTP API"""

    def __init__(self, base_url: str, devops_user: str, devops_password: str):
        self.base_url = base_url.rstrip("/")
        self.auth = (devops_user, devops_password)
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        self._client: Optional[httpx.AsyncClient] = None

    async def connect(self):
        """Initialize the HTTP client"""
        if self._client is None:
            self._client = httpx.AsyncClient(
                auth=self.auth,
                headers=self.headers,
                timeout=30.0,
                follow_redirects=True,
            )
        logger.info("ditto_client_connected", base_url=self.base_url)

    async def disconnect(self):
        """Close the HTTP client"""
        if self._client:
            await self._client.aclose()
            self._client = None
        logger.info("ditto_client_disconnected")

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None:
            raise RuntimeError("DittoClient not connected. Call connect() first.")
        return self._client

    # ========================================
    # Policy Operations
    # ========================================

    async def create_policy(self, policy_id: str, policy: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new policy for access control"""
        url = f"{self.base_url}/api/2/policies/{policy_id}"
        response = await self.client.put(url, json=policy)
        response.raise_for_status()
        return response.json()

    async def get_policy(self, policy_id: str) -> Dict[str, Any]:
        """Retrieve a policy by ID"""
        url = f"{self.base_url}/api/2/policies/{policy_id}"
        response = await self.client.get(url)
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail=f"Policy {policy_id} not found")
        response.raise_for_status()
        return response.json()

    async def delete_policy(self, policy_id: str) -> None:
        """Delete a policy"""
        url = f"{self.base_url}/api/2/policies/{policy_id}"
        response = await self.client.delete(url)
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail=f"Policy {policy_id} not found")
        response.raise_for_status()

    # ========================================
    # Thing Operations
    # ========================================

    async def create_thing(
        self,
        thing_id: str,
        attributes: Optional[Dict[str, Any]] = None,
        features: Optional[Dict[str, Any]] = None,
        policy_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new digital twin (Thing)"""
        url = f"{self.base_url}/api/2/things/{thing_id}"

        # Create policy if not provided
        if not policy_id:
            policy_id = f"{thing_id}:policy"
            await self._create_default_policy(policy_id)

        thing = {
            "thingId": thing_id,
            "policyId": policy_id,
        }

        if attributes:
            thing["attributes"] = attributes
        if features:
            thing["features"] = features

        response = await self.client.put(url, json=thing)
        response.raise_for_status()
        return response.json()

    async def get_thing(self, thing_id: str) -> Dict[str, Any]:
        """Retrieve a digital twin by ID"""
        url = f"{self.base_url}/api/2/things/{thing_id}"
        response = await self.client.get(url)
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail=f"Thing {thing_id} not found")
        response.raise_for_status()
        return response.json()

    async def update_thing(
        self,
        thing_id: str,
        attributes: Optional[Dict[str, Any]] = None,
        features: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Update a digital twin's attributes or features"""
        thing = {}
        if attributes:
            thing["attributes"] = attributes
        if features:
            thing["features"] = features

        if not thing:
            raise HTTPException(status_code=400, detail="No update data provided")

        url = f"{self.base_url}/api/2/things/{thing_id}"
        response = await self.client.patch(
            url,
            json=thing,
            headers={"Content-Type": "application/merge-patch+json"},
        )
        response.raise_for_status()
        return response.json()

    async def delete_thing(self, thing_id: str) -> None:
        """Delete a digital twin"""
        url = f"{self.base_url}/api/2/things/{thing_id}"
        response = await self.client.delete(url)
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail=f"Thing {thing_id} not found")
        response.raise_for_status()

    async def list_things(
        self,
        filter_str: Optional[str] = None,
        option: Optional[str] = None,
        limit: int = 25,
    ) -> Dict[str, Any]:
        """List things with optional filtering"""
        url = f"{self.base_url}/api/2/things"
        params = {"limit": limit}

        if filter_str:
            params["filter"] = filter_str
        if option:
            params["option"] = option

        response = await self.client.get(url, params=params)
        response.raise_for_status()
        return response.json()

    # ========================================
    # Feature Operations
    # ========================================

    async def get_feature(self, thing_id: str, feature_id: str) -> Dict[str, Any]:
        """Get a specific feature of a thing"""
        url = f"{self.base_url}/api/2/things/{thing_id}/features/{feature_id}"
        response = await self.client.get(url)
        if response.status_code == 404:
            raise HTTPException(
                status_code=404, detail=f"Feature {feature_id} not found on thing {thing_id}"
            )
        response.raise_for_status()
        return response.json()

    async def update_feature(
        self, thing_id: str, feature_id: str, properties: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update a feature's properties"""
        url = f"{self.base_url}/api/2/things/{thing_id}/features/{feature_id}"
        feature = {"properties": properties}

        response = await self.client.put(url, json=feature)
        response.raise_for_status()
        return response.json()

    # ========================================
    # Helper Methods
    # ========================================

    async def _create_default_policy(self, policy_id: str) -> None:
        """Create a default policy with full access for the owner"""
        policy = {
            "policyId": policy_id,
            "entries": {
                "owner": {
                    "subjects": {
                        "nginx:ditto": {"type": "pre-authenticated"},
                    },
                    "resources": {
                        "thing:/": {
                            "grant": ["READ", "WRITE", "CREATE", "DELETE"],
                            "revoke": [],
                        },
                        "policy:/": {
                            "grant": ["READ", "WRITE"],
                            "revoke": [],
                        },
                        "message:/": {
                            "grant": ["READ", "WRITE"],
                            "revoke": [],
                        },
                    },
                },
            },
        }
        try:
            await self.create_policy(policy_id, policy)
            logger.info("default_policy_created", policy_id=policy_id)
        except httpx.HTTPStatusError as e:
            if e.response.status_code != 409:  # Ignore if already exists
                raise


# Global Ditto client instance
ditto_client = DittoClient(
    settings.ditto_api_url,
    settings.ditto_devops_user,
    settings.ditto_devops_password,
)


# ============================================
# Lifespan Manager
# ============================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    # Startup
    logger.info("application_starting")
    await ditto_client.connect()

    # Wait for Ditto to be ready
    max_retries = 30
    for i in range(max_retries):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{settings.ditto_api_url}/health", timeout=5.0)
                if response.status_code == 200:
                    logger.info("ditto_health_check_passed")
                    break
        except Exception as e:
            logger.warning("ditto_health_check_failed", attempt=i + 1, error=str(e))
            if i < max_retries - 1:
                await asyncio.sleep(2)
    else:
        logger.error("ditto_unavailable_after_retries")

    yield

    # Shutdown
    logger.info("application_shutting_down")
    await ditto_client.disconnect()


# ============================================
# FastAPI Application
# ============================================

app = FastAPI(
    title="Digital Twins Platform API",
    description="REST API for managing digital twins with Eclipse Ditto",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================
# Pydantic Models
# ============================================


class ThingCreate(BaseModel):
    """Model for creating a new digital twin"""

    thing_id: str = Field(..., description="Unique identifier for the thing (namespace:name)")
    attributes: Optional[Dict[str, Any]] = Field(
        default=None, description="Custom attributes for the thing"
    )
    features: Optional[Dict[str, Any]] = Field(
        default=None, description="Features and their properties"
    )
    policy_id: Optional[str] = Field(default=None, description="ID of the policy to use")

    @field_validator("thing_id")
    @classmethod
    def validate_thing_id(cls, v: str) -> str:
        if ":" not in v:
            raise ValueError("thing_id must be in format 'namespace:name'")
        return v


class ThingUpdate(BaseModel):
    """Model for updating a digital twin"""

    attributes: Optional[Dict[str, Any]] = Field(default=None)
    features: Optional[Dict[str, Any]] = Field(default=None)


class FeatureUpdate(BaseModel):
    """Model for updating a feature"""

    properties: Dict[str, Any] = Field(..., description="Feature properties")


class PolicyCreate(BaseModel):
    """Model for creating a policy"""

    policy_id: str = Field(..., description="Unique identifier for the policy")
    entries: Dict[str, Any] = Field(..., description="Policy entries defining access control")


class ThingListResponse(BaseModel):
    """Response model for listing things"""

    items: List[Dict[str, Any]] = Field(default_factory=list)
    next_page_cursor: Optional[str] = None


# ============================================
# Health Check Endpoint
# ============================================


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


# ============================================
# API Routes
# ============================================

things_router = APIRouter(prefix="/things", tags=["Things"])
policies_router = APIRouter(prefix="/policies", tags=["Policies"])


# ============================================
# Things Endpoints
# ============================================


@things_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Create a new digital twin",
)
async def create_thing(thing: ThingCreate):
    """
    Create a new digital twin (Thing) in Ditto.
    A default policy will be created if no policy_id is provided.
    """
    try:
        result = await ditto_client.create_thing(
            thing_id=thing.thing_id,
            attributes=thing.attributes,
            features=thing.features,
            policy_id=thing.policy_id,
        )
        logger.info("thing_created", thing_id=thing.thing_id)
        return result
    except httpx.HTTPStatusError as e:
        logger.error("thing_creation_failed", thing_id=thing.thing_id, error=str(e))
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Failed to create thing: {e.response.text}",
        )


@things_router.get(
    "/",
    summary="List all digital twins",
)
async def list_things(
    filter: Optional[str] = Query(None, description="RQL filter expression"),
    limit: int = Query(25, ge=1, le=200, description="Maximum number of results"),
):
    """
    List digital twins with optional filtering.
    Supports RQL filter expressions.

    Example filters:
    - eq(attributes/type,"sensor")
    - gt(features/temperature/properties/value,25)
    """
    result = await ditto_client.list_things(filter_str=filter, limit=limit)
    return result


@things_router.get(
    "/{thing_id:path}",
    summary="Get a digital twin by ID",
)
async def get_thing(thing_id: str):
    """Retrieve a digital twin by its unique identifier."""
    return await ditto_client.get_thing(thing_id)


@things_router.patch(
    "/{thing_id:path}",
    summary="Update a digital twin",
)
async def update_thing(thing_id: str, update: ThingUpdate):
    """
    Update a digital twin's attributes or features.
    Uses JSON Merge Patch semantics.
    """
    result = await ditto_client.update_thing(
        thing_id=thing_id,
        attributes=update.attributes,
        features=update.features,
    )
    logger.info("thing_updated", thing_id=thing_id)
    return result


@things_router.delete(
    "/{thing_id:path}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a digital twin",
)
async def delete_thing(thing_id: str):
    """Delete a digital twin by ID."""
    await ditto_client.delete_thing(thing_id)
    logger.info("thing_deleted", thing_id=thing_id)


@things_router.get(
    "/{thing_id:path}/features/{feature_id}",
    summary="Get a specific feature",
)
async def get_feature(thing_id: str, feature_id: str):
    """Get a specific feature from a digital twin."""
    return await ditto_client.get_feature(thing_id, feature_id)


@things_router.put(
    "/{thing_id:path}/features/{feature_id}",
    summary="Update a feature",
)
async def update_feature(thing_id: str, feature_id: str, feature: FeatureUpdate):
    """Update a feature's properties."""
    result = await ditto_client.update_feature(
        thing_id=thing_id, feature_id=feature_id, properties=feature.properties
    )
    logger.info("feature_updated", thing_id=thing_id, feature_id=feature_id)
    return result


# ============================================
# Policies Endpoints
# ============================================


@policies_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Create a new policy",
)
async def create_policy(policy: PolicyCreate):
    """Create a new access control policy."""
    try:
        result = await ditto_client.create_policy(policy.policy_id, {"policyId": policy.policy_id, "entries": policy.entries})
        logger.info("policy_created", policy_id=policy.policy_id)
        return result
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Failed to create policy: {e.response.text}",
        )


@policies_router.get(
    "/{policy_id:path}",
    summary="Get a policy by ID",
)
async def get_policy(policy_id: str):
    """Retrieve an access control policy."""
    return await ditto_client.get_policy(policy_id)


@policies_router.delete(
    "/{policy_id:path}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a policy",
)
async def delete_policy(policy_id: str):
    """Delete an access control policy."""
    await ditto_client.delete_policy(policy_id)
    logger.info("policy_deleted", policy_id=policy_id)


# Include routers
app.include_router(things_router)
app.include_router(policies_router)


# ============================================
# WebSocket Connection Manager
# ============================================


class ConnectionManager:
    """Manage WebSocket connections for real-time updates"""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info("websocket_connected", total_connections=len(self.active_connections))

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info("websocket_disconnected", total_connections=len(self.active_connections))

    async def broadcast(self, message: dict):
        """Broadcast a message to all connected clients"""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.warning("broadcast_failed", error=str(e))


manager = ConnectionManager()


@app.websocket("/ws/events")
async def websocket_events(websocket: WebSocket):
    """
    WebSocket endpoint for real-time digital twin events.

    Connect to receive live updates when things change.

    Message format:
    {
        "event": "thing.created" | "thing.updated" | "thing.deleted",
        "thingId": "namespace:name",
        "data": { ... }
    }
    """
    await manager.connect(websocket)
    try:
        while True:
            # Wait for any message from client (ping/pong or subscribe)
            data = await websocket.receive_text()

            # Echo back for now - in production, implement subscription logic
            if data == "ping":
                await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error("websocket_error", error=str(e))
        manager.disconnect(websocket)


@app.websocket("/ws/ditto")
async def websocket_ditto_proxy(websocket: WebSocket):
    """
    WebSocket proxy to Eclipse Ditto's WebSocket API.

    This provides direct access to Ditto's WebSocket for advanced use cases.
    """
    import websockets

    await websocket.accept()
    logger.info("ditto_websocket_proxy_connected")

    try:
        async with websockets.connect(
            f"{settings.ditto_ws_url}/ws/2",
            extra_headers={
                "Authorization": f"Basic {settings.ditto_devops_user}:{settings.ditto_devops_password}"
            },
        ) as ditto_ws:
            # Create tasks for bidirectional message forwarding
            async def forward_to_ditto():
                try:
                    while True:
                        data = await websocket.receive_text()
                        await ditto_ws.send(data)
                except WebSocketDisconnect:
                    pass

            async def forward_from_ditto():
                try:
                    async for message in ditto_ws:
                        await websocket.send_text(message)
                except Exception:
                    pass

            # Run both directions concurrently
            await asyncio.gather(forward_to_ditto(), forward_from_ditto())

    except WebSocketDisconnect:
        logger.info("ditto_websocket_proxy_disconnected")
    except Exception as e:
        logger.error("ditto_websocket_proxy_error", error=str(e))
        await websocket.close()


# ============================================
# Search Endpoints
# ============================================

search_router = APIRouter(prefix="/search", tags=["Search"])


@search_router.get("/things")
async def search_things(
    q: str = Query(..., description="Search query (RQL expression)"),
    limit: int = Query(25, ge=1, le=200),
):
    """
    Search for digital twins using RQL query syntax.

    Examples:
    - ?q=eq(attributes/type,"temperature-sensor")
    - ?q=and(gt(features/temperature/properties/value,20),lt(features/humidity/properties/value,80))
    - ?q=like(attributes/name,"Room*")
    """
    result = await ditto_client.list_things(filter_str=q, limit=limit)
    return result


app.include_router(search_router)


# ============================================
# Main entry point
# ============================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
