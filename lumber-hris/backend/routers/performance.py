"""Performance Management Router — Reviews, Goals, Incidents, Commendations, PIPs"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from pydantic import BaseModel
from datetime import date
from backend.models.database import (
    get_db, Employee, Department, PerformanceReview, ReviewCycle, ReviewCriteria,
    Goal, Incident, Commendation, PIP, PIPMilestone,
)
from backend.routers.auth import get_current_user, require_role, User

performance_router = APIRouter()

# ---- Schemas ----

class ReviewBrief(BaseModel):
    id: str
    employee_name: str
    employee_id: str
    reviewer_name: str
    type: str
    status: str
    due_date: Optional[date] = None
    overall_rating: Optional[float] = None
    created_at: Optional[str] = None

class ReviewDetail(ReviewBrief):
    period_start: Optional[date] = None
    period_end: Optional[date] = None
    manager_comments: Optional[str] = None
    employee_comments: Optional[str] = None
    development_plan: Optional[str] = None
    criteria: list = []

class GoalResponse(BaseModel):
    id: str
    employee_name: str
    employee_id: str
    title: str
    description: Optional[str] = None
    category: str
    target_date: Optional[date] = None
    weight: float = 1.0
    percent_complete: int = 0
    status: str

class IncidentResponse(BaseModel):
    id: str
    employee_name: str
    employee_id: str
    reported_by_name: str
    type: str
    severity: str
    description: str
    incident_date: Optional[date] = None
    location: Optional[str] = None
    status: str
    resolution: Optional[str] = None
    created_at: Optional[str] = None

class CommendationResponse(BaseModel):
    id: str
    employee_name: str
    employee_id: str
    awarded_by_name: str
    category: str
    stars: int
    description: str
    is_public: bool = True
    created_at: Optional[str] = None

def _emp_name(db, emp_id):
    if not emp_id:
        return "Unknown"
    e = db.query(Employee).get(emp_id)
    return f"{e.first_name} {e.last_name}" if e else "Unknown"

# ---- Reviews ----

@performance_router.get("/reviews", response_model=List[ReviewBrief])
async def list_reviews(
    cycle_id: Optional[str] = None,
    status: Optional[str] = None,
    page: int = 1, per_page: int = 25,
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user),
):
    q = db.query(PerformanceReview)
    if cycle_id:
        q = q.filter(PerformanceReview.review_cycle_id == cycle_id)
    if status:
        q = q.filter(PerformanceReview.status == status)
    if current_user.role == "EMPLOYEE" and current_user.employee_id:
        q = q.filter(PerformanceReview.employee_id == current_user.employee_id)
    elif current_user.role == "FOREMAN" and current_user.employee_id:
        crew_ids = [e.id for e in db.query(Employee.id).filter(Employee.reports_to_id == current_user.employee_id).all()]
        crew_ids.append(current_user.employee_id)
        q = q.filter(PerformanceReview.employee_id.in_(crew_ids))

    reviews = q.order_by(PerformanceReview.created_at.desc()).offset((page-1)*per_page).limit(per_page).all()
    return [ReviewBrief(
        id=r.id, employee_name=_emp_name(db, r.employee_id), employee_id=r.employee_id,
        reviewer_name=_emp_name(db, r.reviewer_id), type=r.type, status=r.status,
        due_date=r.due_date, overall_rating=r.overall_rating,
        created_at=str(r.created_at) if r.created_at else None,
    ) for r in reviews]

@performance_router.get("/reviews/{review_id}", response_model=ReviewDetail)
async def get_review(review_id: str, db: Session = Depends(get_db), _=Depends(get_current_user)):
    r = db.query(PerformanceReview).get(review_id)
    if not r:
        raise HTTPException(404, "Review not found")
    criteria = db.query(ReviewCriteria).filter(ReviewCriteria.review_id == r.id).all()
    return ReviewDetail(
        id=r.id, employee_name=_emp_name(db, r.employee_id), employee_id=r.employee_id,
        reviewer_name=_emp_name(db, r.reviewer_id), type=r.type, status=r.status,
        due_date=r.due_date, overall_rating=r.overall_rating,
        period_start=r.period_start, period_end=r.period_end,
        manager_comments=r.manager_comments, employee_comments=r.employee_comments,
        development_plan=r.development_plan,
        created_at=str(r.created_at) if r.created_at else None,
        criteria=[{"id": c.id, "name": c.name, "category": c.category,
                   "weight": c.weight, "rating": c.rating, "comments": c.comments} for c in criteria],
    )

@performance_router.get("/cycles")
async def list_cycles(db: Session = Depends(get_db), _=Depends(get_current_user)):
    cycles = db.query(ReviewCycle).order_by(ReviewCycle.period_start.desc()).all()
    result = []
    for c in cycles:
        total = db.query(func.count(PerformanceReview.id)).filter(
            PerformanceReview.review_cycle_id == c.id).scalar() or 0
        completed = db.query(func.count(PerformanceReview.id)).filter(
            PerformanceReview.review_cycle_id == c.id,
            PerformanceReview.status == "COMPLETED").scalar() or 0
        result.append({
            "id": c.id, "name": c.name, "type": c.type,
            "period_start": str(c.period_start), "period_end": str(c.period_end),
            "status": c.status, "total_reviews": total,
            "completed_reviews": completed,
            "progress": round(completed / total * 100, 1) if total else 0,
        })
    return result

# ---- Goals ----

@performance_router.get("/goals", response_model=List[GoalResponse])
async def list_goals(
    employee_id: Optional[str] = None, status: Optional[str] = None,
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user),
):
    q = db.query(Goal)
    if employee_id:
        q = q.filter(Goal.employee_id == employee_id)
    if status:
        q = q.filter(Goal.status == status)
    if current_user.role == "EMPLOYEE" and current_user.employee_id:
        q = q.filter(Goal.employee_id == current_user.employee_id)
    goals = q.order_by(Goal.target_date).all()
    return [GoalResponse(
        id=g.id, employee_name=_emp_name(db, g.employee_id), employee_id=g.employee_id,
        title=g.title, description=g.description, category=g.category,
        target_date=g.target_date, weight=g.weight,
        percent_complete=g.percent_complete, status=g.status,
    ) for g in goals]

# ---- Incidents ----

@performance_router.get("/incidents", response_model=List[IncidentResponse])
async def list_incidents(
    type: Optional[str] = None, severity: Optional[str] = None,
    db: Session = Depends(get_db), _=Depends(get_current_user),
):
    q = db.query(Incident)
    if type:
        q = q.filter(Incident.type == type)
    if severity:
        q = q.filter(Incident.severity == severity)
    incidents = q.order_by(Incident.created_at.desc()).all()
    return [IncidentResponse(
        id=i.id, employee_name=_emp_name(db, i.employee_id), employee_id=i.employee_id,
        reported_by_name=_emp_name(db, i.reported_by_id),
        type=i.type, severity=i.severity, description=i.description,
        incident_date=i.incident_date, location=i.location,
        status=i.status, resolution=i.resolution,
        created_at=str(i.created_at) if i.created_at else None,
    ) for i in incidents]

# ---- Commendations ----

@performance_router.get("/commendations", response_model=List[CommendationResponse])
async def list_commendations(db: Session = Depends(get_db), _=Depends(get_current_user)):
    comms = db.query(Commendation).order_by(Commendation.created_at.desc()).all()
    return [CommendationResponse(
        id=c.id, employee_name=_emp_name(db, c.employee_id), employee_id=c.employee_id,
        awarded_by_name=_emp_name(db, c.awarded_by_id),
        category=c.category, stars=c.stars, description=c.description,
        is_public=c.is_public, created_at=str(c.created_at) if c.created_at else None,
    ) for c in comms]

# ---- PIPs ----

@performance_router.get("/pips")
async def list_pips(db: Session = Depends(get_db), _=Depends(get_current_user)):
    pips = db.query(PIP).order_by(PIP.created_at.desc()).all()
    result = []
    for p in pips:
        milestones = db.query(PIPMilestone).filter(PIPMilestone.pip_id == p.id).order_by(PIPMilestone.due_date).all()
        result.append({
            "id": p.id, "employee_name": _emp_name(db, p.employee_id),
            "employee_id": p.employee_id,
            "issue_description": p.issue_description,
            "start_date": str(p.start_date), "end_date": str(p.end_date),
            "status": p.status,
            "milestones": [{"id": m.id, "title": m.title, "due_date": str(m.due_date),
                           "status": m.status, "completed_date": str(m.completed_date) if m.completed_date else None}
                          for m in milestones],
        })
    return result

# ---- Calibration 9-box ----

@performance_router.get("/calibration/nine-box")
async def calibration_grid(
    cycle_id: Optional[str] = None,
    db: Session = Depends(get_db), _=Depends(get_current_user),
):
    q = db.query(PerformanceReview).filter(PerformanceReview.status == "COMPLETED")
    if cycle_id:
        q = q.filter(PerformanceReview.review_cycle_id == cycle_id)
    reviews = q.all()

    # Build 3x3 grid: rows = High/Medium/Low potential, cols = Low/Medium/High performance
    grid = [[{"count": 0, "employees": []} for _ in range(3)] for _ in range(3)]

    total_reviewed = 0
    for r in reviews:
        if r.overall_rating is None:
            continue
        total_reviewed += 1
        perf_idx = 0 if r.overall_rating < 2.5 else (1 if r.overall_rating < 3.5 else 2)
        pot_idx = 1  # Default medium potential
        grid[pot_idx][perf_idx]["count"] += 1
        grid[pot_idx][perf_idx]["employees"].append({
            "name": _emp_name(db, r.employee_id),
            "rating": r.overall_rating,
        })

    return {"grid": grid, "total_reviewed": total_reviewed}
