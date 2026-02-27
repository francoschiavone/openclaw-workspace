"""Dashboard KPIs and charts"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from datetime import date, timedelta
from backend.models.database import (
    get_db, Employee, PerformanceReview, Certification, Project, Department,
    TrainingAssignment,
)
from backend.routers.auth import get_current_user

dashboard_router = APIRouter()

@dashboard_router.get("/kpis")
async def get_kpis(db: Session = Depends(get_db), _=Depends(get_current_user)):
    today = date.today()
    active = db.query(func.count(Employee.id)).filter(Employee.status == "ACTIVE").scalar() or 0
    pending = db.query(func.count(PerformanceReview.id)).filter(
        PerformanceReview.status.in_(["DRAFT", "SELF_REVIEW", "MANAGER_REVIEW", "PENDING_SIGN_OFF"])
    ).scalar() or 0
    exp_certs = db.query(func.count(Certification.id)).filter(
        Certification.expiration_date <= today + timedelta(days=30),
        Certification.expiration_date >= today,
        Certification.status != "REVOKED",
    ).scalar() or 0
    expired = db.query(func.count(Certification.id)).filter(
        Certification.status == "EXPIRED"
    ).scalar() or 0
    active_proj = db.query(func.count(Project.id)).filter(Project.status == "ACTIVE").scalar() or 0

    total_certs = db.query(func.count(Certification.id)).scalar() or 1
    valid_certs = db.query(func.count(Certification.id)).filter(
        Certification.status == "VALID"
    ).scalar() or 0
    compliance_pct = round((valid_certs / total_certs) * 100, 1) if total_certs else 0

    # Average tenure in months
    avg_tenure = db.query(
        func.avg(func.julianday('now') - func.julianday(Employee.hire_date))
    ).filter(Employee.status == "ACTIVE").scalar() or 0
    avg_months = round(avg_tenure / 30.44, 1)

    # Compute turnover rate: terminated in last 12 months / avg headcount * 100
    twelve_months_ago = today - timedelta(days=365)
    terminated_12m = db.query(func.count(Employee.id)).filter(
        Employee.status == "TERMINATED",
        Employee.termination_date >= twelve_months_ago,
    ).scalar() or 0
    avg_headcount = active + (terminated_12m / 2)
    turnover_rate = round((terminated_12m / avg_headcount) * 100, 1) if avg_headcount else 0

    return {
        "total_headcount": active,
        "open_positions": 0,
        "pending_reviews": pending,
        "expiring_certs": exp_certs + expired,
        "turnover_rate": turnover_rate,
        "avg_tenure_months": avg_months,
        "training_compliance_pct": compliance_pct,
        "active_projects": active_proj,
    }

@dashboard_router.get("/charts")
async def get_all_charts(db: Session = Depends(get_db), _=Depends(get_current_user)):
    """Combined charts data for the dashboard."""
    # Headcount by department
    dept_results = db.query(
        Department.name, func.count(Employee.id)
    ).join(Employee, Employee.department_id == Department.id
    ).filter(Employee.status == "ACTIVE"
    ).group_by(Department.name).order_by(func.count(Employee.id).desc()).all()
    
    # Employee type distribution
    type_results = db.query(
        Employee.employee_type, func.count(Employee.id)
    ).filter(Employee.status == "ACTIVE"
    ).group_by(Employee.employee_type).all()
    
    # Cert compliance
    cert_results = db.query(
        Certification.status, func.count(Certification.id)
    ).group_by(Certification.status).all()
    
    return {
        "by_department": [{"name": name, "count": count} for name, count in dept_results],
        "by_type": [{"name": t.replace("_", " ").title(), "value": c} for t, c in type_results],
        "by_cert_status": [{"name": s.replace("_", " ").title(), "value": c} for s, c in cert_results],
    }


@dashboard_router.get("/charts/headcount-by-dept")
async def headcount_by_dept(db: Session = Depends(get_db), _=Depends(get_current_user)):
    results = db.query(
        Department.name, func.count(Employee.id)
    ).join(Employee, Employee.department_id == Department.id
    ).filter(Employee.status == "ACTIVE"
    ).group_by(Department.name).order_by(func.count(Employee.id).desc()).all()
    return [{"label": name, "value": count} for name, count in results]

@dashboard_router.get("/charts/employee-type")
async def employee_type_dist(db: Session = Depends(get_db), _=Depends(get_current_user)):
    results = db.query(
        Employee.employee_type, func.count(Employee.id)
    ).filter(Employee.status == "ACTIVE"
    ).group_by(Employee.employee_type).all()
    return [{"label": t.replace("_", " ").title(), "value": c} for t, c in results]

@dashboard_router.get("/charts/cert-compliance")
async def cert_compliance(db: Session = Depends(get_db), _=Depends(get_current_user)):
    results = db.query(
        Certification.status, func.count(Certification.id)
    ).group_by(Certification.status).all()
    return [{"label": s.replace("_", " ").title(), "value": c} for s, c in results]

@dashboard_router.get("/activity")
async def recent_activity(db: Session = Depends(get_db), _=Depends(get_current_user)):
    # Most recent reviews, incidents, etc.
    recent_reviews = db.query(PerformanceReview).order_by(
        PerformanceReview.created_at.desc()
    ).limit(5).all()
    activities = []
    for r in recent_reviews:
        emp = db.query(Employee).get(r.employee_id)
        name = f"{emp.first_name} {emp.last_name}" if emp else "Unknown"
        activities.append({
            "type": "review",
            "description": f"Performance review for {name} — {r.status}",
            "timestamp": str(r.created_at),
        })
    return activities
