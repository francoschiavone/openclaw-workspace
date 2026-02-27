"""Analytics Router — Workforce, Performance, Training, Organization analytics"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import date, timedelta
from backend.models.database import (
    get_db, Employee, Department, Division, PerformanceReview, Certification,
    TrainingAssignment, Incident, Goal,
)
from backend.routers.auth import get_current_user

analytics_router = APIRouter()


@analytics_router.get("/workforce")
async def workforce_analytics(db: Session = Depends(get_db), _=Depends(get_current_user)):
    """Headcount, turnover, tenure analysis."""
    # Headcount by department
    dept_headcount = db.query(
        Department.name, func.count(Employee.id)
    ).join(Employee, Employee.department_id == Department.id
    ).filter(Employee.status == "ACTIVE"
    ).group_by(Department.name).order_by(func.count(Employee.id).desc()).all()

    # Employee type distribution
    type_dist = db.query(
        Employee.employee_type, func.count(Employee.id)
    ).filter(Employee.status == "ACTIVE"
    ).group_by(Employee.employee_type).all()

    # Tenure distribution
    today = date.today()
    tenure_buckets = {"<1 year": 0, "1-3 years": 0, "3-5 years": 0, "5-10 years": 0, "10+ years": 0}
    employees = db.query(Employee).filter(Employee.status == "ACTIVE").all()
    for e in employees:
        years = (today - e.hire_date).days / 365.25
        if years < 1:
            tenure_buckets["<1 year"] += 1
        elif years < 3:
            tenure_buckets["1-3 years"] += 1
        elif years < 5:
            tenure_buckets["3-5 years"] += 1
        elif years < 10:
            tenure_buckets["5-10 years"] += 1
        else:
            tenure_buckets["10+ years"] += 1

    # Trade distribution
    trade_dist = db.query(
        Employee.trade, func.count(Employee.id)
    ).filter(Employee.status == "ACTIVE", Employee.trade.isnot(None)
    ).group_by(Employee.trade).order_by(func.count(Employee.id).desc()).all()

    return {
        "headcount_by_department": [{"label": n, "value": c} for n, c in dept_headcount],
        "employee_type": [{"label": t.replace("_", " ").title(), "value": c} for t, c in type_dist],
        "tenure_distribution": [{"label": k, "value": v} for k, v in tenure_buckets.items()],
        "trade_distribution": [{"label": t or "N/A", "value": c} for t, c in trade_dist],
        "total_active": sum(c for _, c in dept_headcount),
    }


@analytics_router.get("/performance")
async def performance_analytics(db: Session = Depends(get_db), _=Depends(get_current_user)):
    """Rating distributions, trends, goal completion."""
    # Rating distribution
    ratings = db.query(PerformanceReview.overall_rating).filter(
        PerformanceReview.status == "COMPLETED",
        PerformanceReview.overall_rating.isnot(None),
    ).all()
    rating_dist = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for (r,) in ratings:
        bucket = min(5, max(1, round(r)))
        rating_dist[bucket] += 1

    labels = {1: "Unsatisfactory", 2: "Needs Improvement", 3: "Meets Expectations",
              4: "Exceeds", 5: "Exceptional"}

    # Review completion
    total_reviews = db.query(func.count(PerformanceReview.id)).scalar() or 0
    completed = db.query(func.count(PerformanceReview.id)).filter(
        PerformanceReview.status == "COMPLETED"
    ).scalar() or 0

    # Goal status
    goal_status = db.query(
        Goal.status, func.count(Goal.id)
    ).group_by(Goal.status).all()

    # Incident summary
    incident_types = db.query(
        Incident.type, func.count(Incident.id)
    ).group_by(Incident.type).all()

    return {
        "rating_distribution": [{"label": labels.get(k, str(k)), "value": v} for k, v in sorted(rating_dist.items())],
        "review_completion": {"total": total_reviews, "completed": completed,
                             "rate": round(completed / total_reviews * 100, 1) if total_reviews else 0},
        "goal_status": [{"label": s.replace("_", " ").title(), "value": c} for s, c in goal_status],
        "incident_summary": [{"label": t.replace("_", " ").title(), "value": c} for t, c in incident_types],
    }


@analytics_router.get("/training")
async def training_analytics(db: Session = Depends(get_db), _=Depends(get_current_user)):
    """Compliance, training hours, certification forecasts."""
    # Cert status distribution
    cert_status = db.query(
        Certification.status, func.count(Certification.id)
    ).group_by(Certification.status).all()

    # Training completion
    assign_status = db.query(
        TrainingAssignment.status, func.count(TrainingAssignment.id)
    ).group_by(TrainingAssignment.status).all()

    # Expiring forecast
    today = date.today()
    exp_30 = db.query(func.count(Certification.id)).filter(
        Certification.expiration_date.between(today, today + timedelta(days=30))
    ).scalar() or 0
    exp_60 = db.query(func.count(Certification.id)).filter(
        Certification.expiration_date.between(today + timedelta(days=31), today + timedelta(days=60))
    ).scalar() or 0
    exp_90 = db.query(func.count(Certification.id)).filter(
        Certification.expiration_date.between(today + timedelta(days=61), today + timedelta(days=90))
    ).scalar() or 0

    return {
        "cert_status": [{"label": s.replace("_", " ").title(), "value": c} for s, c in cert_status],
        "training_completion": [{"label": s.replace("_", " ").title(), "value": c} for s, c in assign_status],
        "expiring_forecast": [
            {"label": "30 days", "value": exp_30},
            {"label": "60 days", "value": exp_60},
            {"label": "90 days", "value": exp_90},
        ],
    }


@analytics_router.get("/organization")
async def organization_analytics(db: Session = Depends(get_db), _=Depends(get_current_user)):
    """Span of control, hierarchy stats."""
    # Span of control
    managers = db.query(Employee).filter(Employee.status == "ACTIVE").all()
    span_data = []
    for m in managers:
        direct = db.query(func.count(Employee.id)).filter(
            Employee.reports_to_id == m.id
        ).scalar() or 0
        if direct > 0:
            span_data.append(direct)

    span_dist = {"1-4": 0, "5-8": 0, "9-12": 0, "13+": 0}
    for s in span_data:
        if s <= 4:
            span_dist["1-4"] += 1
        elif s <= 8:
            span_dist["5-8"] += 1
        elif s <= 12:
            span_dist["9-12"] += 1
        else:
            span_dist["13+"] += 1

    # Division headcount
    div_data = db.query(
        Division.name, func.count(Employee.id)
    ).join(Department, Department.division_id == Division.id
    ).join(Employee, Employee.department_id == Department.id
    ).filter(Employee.status == "ACTIVE"
    ).group_by(Division.name).all()

    return {
        "span_of_control": [{"label": k, "value": v} for k, v in span_dist.items()],
        "avg_span": round(sum(span_data) / len(span_data), 1) if span_data else 0,
        "division_headcount": [{"label": n, "value": c} for n, c in div_data],
    }
