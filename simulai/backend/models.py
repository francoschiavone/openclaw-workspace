"""
Pydantic models for the Digital Twins Platform API
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


# ============================================
# Thing Models
# ============================================


class FeatureProperties(BaseModel):
    """Properties of a feature"""

    model_config = {"extra": "allow"}  # Allow any additional fields


class Feature(BaseModel):
    """A feature of a digital twin"""

    properties: Optional[Dict[str, Any]] = Field(default_factory=dict)
    definition: Optional[List[str]] = Field(default=None)


class ThingAttributes(BaseModel):
    """Attributes of a digital twin"""

    model_config = {"extra": "allow"}


class Thing(BaseModel):
    """Complete digital twin representation"""

    thing_id: str = Field(..., alias="thingId")
    policy_id: str = Field(..., alias="policyId")
    attributes: Optional[Dict[str, Any]] = Field(default_factory=dict)
    features: Optional[Dict[str, Feature]] = Field(default_factory=dict)
    _revision: Optional[int] = Field(default=None, alias="_revision")
    _created: Optional[datetime] = Field(default=None, alias="_created")
    _modified: Optional[datetime] = Field(default=None, alias="_modified")

    model_config = {"populate_by_name": True, "extra": "allow"}


class ThingCreate(BaseModel):
    """Model for creating a new thing"""

    thing_id: str = Field(..., alias="thingId")
    policy_id: Optional[str] = Field(None, alias="policyId")
    attributes: Optional[Dict[str, Any]] = None
    features: Optional[Dict[str, Any]] = None

    @field_validator("thing_id")
    @classmethod
    def validate_thing_id(cls, v: str) -> str:
        if ":" not in v:
            raise ValueError("thing_id must be in format 'namespace:name'")
        return v

    model_config = {"populate_by_name": True}


class ThingUpdate(BaseModel):
    """Model for updating a thing (merge patch)"""

    attributes: Optional[Dict[str, Any]] = None
    features: Optional[Dict[str, Any]] = None


# ============================================
# Policy Models
# ============================================


class PolicySubject(BaseModel):
    """A subject in a policy entry"""

    type: str = "generated"


class PolicyResource(BaseModel):
    """Resource permissions in a policy"""

    grant: List[str] = Field(default_factory=list)
    revoke: List[str] = Field(default_factory=list)


class PolicyEntry(BaseModel):
    """A policy entry defining access for subjects"""

    subjects: Dict[str, PolicySubject] = Field(default_factory=dict)
    resources: Dict[str, PolicyResource] = Field(default_factory=dict)


class Policy(BaseModel):
    """Complete policy representation"""

    policy_id: str = Field(..., alias="policyId")
    entries: Dict[str, PolicyEntry] = Field(default_factory=dict)
    _revision: Optional[int] = Field(default=None, alias="_revision")
    _created: Optional[datetime] = Field(default=None, alias="_created")
    _modified: Optional[datetime] = Field(default=None, alias="_modified")

    model_config = {"populate_by_name": True}


class PolicyCreate(BaseModel):
    """Model for creating a new policy"""

    policy_id: str = Field(..., alias="policyId")
    entries: Dict[str, PolicyEntry]

    model_config = {"populate_by_name": True}


# ============================================
# Search Models
# ============================================


class SearchResult(BaseModel):
    """Search result container"""

    items: List[Dict[str, Any]] = Field(default_factory=list, alias="items")
    next_page_cursor: Optional[str] = Field(None, alias="nextPageCursor")

    model_config = {"populate_by_name": True}


# ============================================
# Event Models
# ============================================


class ThingEvent(BaseModel):
    """Event emitted when a thing changes"""

    event: str  # thing.created, thing.updated, thing.deleted
    thing_id: str
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class FeatureEvent(BaseModel):
    """Event emitted when a feature changes"""

    event: str  # feature.created, feature.updated, feature.deleted
    thing_id: str
    feature_id: str
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ============================================
# Error Models
# ============================================


class ErrorResponse(BaseModel):
    """Standard error response"""

    status: int
    error: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    path: Optional[str] = None
