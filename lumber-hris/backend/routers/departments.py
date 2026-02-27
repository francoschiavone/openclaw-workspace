"""Departments, Divisions, Locations endpoints"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from pydantic import BaseModel
from backend.models.database import get_db, Department, Division, Location, Employee
from backend.routers.auth import get_current_user

department_router = APIRouter()

class DepartmentResponse(BaseModel):
    id: str
    name: str
    code: str
    division_id: str
    division_name: str = ""
    cost_center: str | None = None
    employee_count: int = 0
    class Config:
        from_attributes = True

class DivisionResponse(BaseModel):
    id: str
    name: str
    code: str
    class Config:
        from_attributes = True

class LocationResponse(BaseModel):
    id: str
    name: str
    address: str | None = None
    city: str | None = None
    state: str | None = None
    type: str = "FIELD"
    class Config:
        from_attributes = True

@department_router.get("", response_model=List[DepartmentResponse])
async def list_departments(db: Session = Depends(get_db), _=Depends(get_current_user)):
    depts = db.query(Department).order_by(Department.name).all()
    result = []
    for d in depts:
        div = db.query(Division).get(d.division_id) if d.division_id else None
        count = db.query(func.count(Employee.id)).filter(Employee.department_id == d.id).scalar() or 0
        result.append(DepartmentResponse(
            id=d.id, name=d.name, code=d.code, division_id=d.division_id or "",
            division_name=div.name if div else "", cost_center=d.cost_center,
            employee_count=count,
        ))
    return result

@department_router.get("/divisions", response_model=List[DivisionResponse])
async def list_divisions(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return [DivisionResponse.model_validate(d) for d in db.query(Division).all()]

@department_router.get("/locations", response_model=List[LocationResponse])
async def list_locations(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return [LocationResponse.model_validate(l) for l in db.query(Location).all()]
