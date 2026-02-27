"""LMS Router — Courses, Certifications, Training Assignments, Rules"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from datetime import date, timedelta
from backend.models.database import (
    get_db, Employee, Department, Course, Certification, TrainingAssignment,
    TrainingRule,
)
from backend.routers.auth import get_current_user, User

lms_router = APIRouter()


@lms_router.get("/courses")
async def list_courses(
    category: Optional[str] = None, format: Optional[str] = None,
    required: Optional[bool] = None, trade: Optional[str] = None,
    db: Session = Depends(get_db), _=Depends(get_current_user),
):
    q = db.query(Course)
    if category:
        q = q.filter(Course.category == category)
    if format:
        q = q.filter(Course.format == format)
    if required is not None:
        q = q.filter(Course.is_required == required)
    if trade:
        q = q.filter(Course.trade_specific == trade)
    courses = q.order_by(Course.title).all()
    result = []
    for c in courses:
        completed = db.query(func.count(TrainingAssignment.id)).filter(
            TrainingAssignment.course_id == c.id, TrainingAssignment.status == "COMPLETED"
        ).scalar() or 0
        total = db.query(func.count(TrainingAssignment.id)).filter(
            TrainingAssignment.course_id == c.id
        ).scalar() or 0
        result.append({
            "id": c.id, "title": c.title, "description": c.description,
            "category": c.category, "format": c.format,
            "duration_hours": c.duration_hours, "is_required": c.is_required,
            "trade_specific": c.trade_specific, "provider": c.provider,
            "enrollment": {"completed": completed, "in_progress": total - completed, "total": total},
        })
    return result


@lms_router.get("/courses/{course_id}")
async def get_course(course_id: str, db: Session = Depends(get_db), _=Depends(get_current_user)):
    c = db.query(Course).get(course_id)
    if not c:
        raise HTTPException(404, "Course not found")
    return {
        "id": c.id, "title": c.title, "description": c.description,
        "category": c.category, "format": c.format,
        "duration_hours": c.duration_hours, "is_required": c.is_required,
        "trade_specific": c.trade_specific, "provider": c.provider,
    }


@lms_router.get("/certifications")
async def list_certifications(
    status: Optional[str] = None, employee_id: Optional[str] = None,
    department_id: Optional[str] = None,
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user),
):
    q = db.query(Certification)
    if status:
        q = q.filter(Certification.status == status)
    if employee_id:
        q = q.filter(Certification.employee_id == employee_id)
    if department_id:
        emp_ids = [e.id for e in db.query(Employee.id).filter(Employee.department_id == department_id).all()]
        q = q.filter(Certification.employee_id.in_(emp_ids))
    if current_user.role == "EMPLOYEE" and current_user.employee_id:
        q = q.filter(Certification.employee_id == current_user.employee_id)

    certs = q.order_by(Certification.expiration_date.asc()).all()
    result = []
    for c in certs:
        emp = db.query(Employee).get(c.employee_id)
        result.append({
            "id": c.id,
            "employee_name": f"{emp.first_name} {emp.last_name}" if emp else "Unknown",
            "employee_id": c.employee_id,
            "name": c.name, "certification_name": c.name,
            "issuing_body": c.issuing_body,
            "cert_number": c.cert_number,
            "issue_date": str(c.issue_date) if c.issue_date else None,
            "expiration_date": str(c.expiration_date) if c.expiration_date else None,
            "status": c.status,
        })
    return result


@lms_router.get("/compliance")
@lms_router.get("/certifications/dashboard")
async def compliance_dashboard(db: Session = Depends(get_db), _=Depends(get_current_user)):
    today = date.today()
    total = db.query(func.count(Certification.id)).scalar() or 1
    valid = db.query(func.count(Certification.id)).filter(Certification.status == "VALID").scalar() or 0
    expiring = db.query(func.count(Certification.id)).filter(Certification.status == "EXPIRING_SOON").scalar() or 0
    expired = db.query(func.count(Certification.id)).filter(Certification.status == "EXPIRED").scalar() or 0
    
    # By department
    dept_data = []
    depts = db.query(Department).all()
    for d in depts:
        emp_ids = [e.id for e in db.query(Employee.id).filter(Employee.department_id == d.id).all()]
        if not emp_ids:
            continue
        d_total = db.query(func.count(Certification.id)).filter(Certification.employee_id.in_(emp_ids)).scalar() or 0
        d_valid = db.query(func.count(Certification.id)).filter(
            Certification.employee_id.in_(emp_ids), Certification.status == "VALID"
        ).scalar() or 0
        dept_data.append({
            "department": d.name,
            "total": d_total, "valid": d_valid,
            "rate": round(d_valid / d_total * 100, 1) if d_total else 0,
        })

    return {
        "overall_rate": round(valid / total * 100, 1),
        "total": total, "valid": valid, "expiring": expiring, "expired": expired,
        "by_department": sorted(dept_data, key=lambda x: x["rate"]),
    }


@lms_router.get("/expiring")
@lms_router.get("/certifications/expiring")
async def expiring_certs(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db), _=Depends(get_current_user),
):
    today = date.today()
    cutoff = today + timedelta(days=days)
    certs = db.query(Certification).filter(
        Certification.expiration_date <= cutoff,
        Certification.expiration_date >= today,
    ).order_by(Certification.expiration_date.asc()).all()
    result = []
    for c in certs:
        emp = db.query(Employee).get(c.employee_id)
        result.append({
            "id": c.id, "name": c.name, "certification_name": c.name,
            "employee_name": f"{emp.first_name} {emp.last_name}" if emp else "Unknown",
            "employee_id": c.employee_id,
            "expiration_date": str(c.expiration_date),
            "days_remaining": (c.expiration_date - today).days,
            "days_until_expiry": (c.expiration_date - today).days,
        })
    return result


@lms_router.get("/assignments")
async def list_assignments(
    employee_id: Optional[str] = None, status: Optional[str] = None,
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user),
):
    q = db.query(TrainingAssignment)
    if employee_id:
        q = q.filter(TrainingAssignment.employee_id == employee_id)
    if status:
        q = q.filter(TrainingAssignment.status == status)
    if current_user.role == "EMPLOYEE" and current_user.employee_id:
        q = q.filter(TrainingAssignment.employee_id == current_user.employee_id)
    
    assignments = q.order_by(TrainingAssignment.due_date).all()
    result = []
    for a in assignments:
        emp = db.query(Employee).get(a.employee_id)
        course = db.query(Course).get(a.course_id) if a.course_id else None
        result.append({
            "id": a.id,
            "employee_name": f"{emp.first_name} {emp.last_name}" if emp else "Unknown",
            "employee_id": a.employee_id,
            "course_title": course.title if course else "Unknown",
            "course_id": a.course_id,
            "status": a.status,
            "due_date": str(a.due_date) if a.due_date else None,
            "completed_date": str(a.completed_date) if a.completed_date else None,
            "score": a.score,
        })
    return result


@lms_router.get("/rules")
async def list_rules(db: Session = Depends(get_db), _=Depends(get_current_user)):
    rules = db.query(TrainingRule).order_by(TrainingRule.name).all()
    return [{
        "id": r.id, "name": r.name, "trigger_type": r.trigger_type,
        "trigger_config": r.trigger_config_json, "is_active": r.is_active,
    } for r in rules]


@lms_router.get("/transcript/{employee_id}")
async def training_transcript(
    employee_id: str, db: Session = Depends(get_db), _=Depends(get_current_user),
):
    emp = db.query(Employee).get(employee_id)
    if not emp:
        raise HTTPException(404, "Employee not found")

    assignments = db.query(TrainingAssignment).filter(
        TrainingAssignment.employee_id == employee_id
    ).order_by(TrainingAssignment.due_date.desc()).all()
    certs = db.query(Certification).filter(
        Certification.employee_id == employee_id
    ).order_by(Certification.expiration_date.desc()).all()

    return {
        "employee": {
            "id": emp.id, "name": f"{emp.first_name} {emp.last_name}",
            "employee_number": emp.employee_number,
        },
        "assignments": [{
            "course_title": db.query(Course).get(a.course_id).title if a.course_id and db.query(Course).get(a.course_id) else "Unknown",
            "status": a.status, "due_date": str(a.due_date) if a.due_date else None,
            "completed_date": str(a.completed_date) if a.completed_date else None,
            "score": a.score,
        } for a in assignments],
        "certifications": [{
            "name": c.name, "issuing_body": c.issuing_body,
            "issue_date": str(c.issue_date) if c.issue_date else None,
            "expiration_date": str(c.expiration_date) if c.expiration_date else None,
            "status": c.status,
        } for c in certs],
    }
