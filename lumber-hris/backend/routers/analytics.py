"""Analytics Router — Workforce, Performance, Training, Organization analytics"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import date, timedelta
from backend.models.database import (
    get_db, Employee, Department, Division, PerformanceReview, Certification,
    TrainingAssignment, Incident, Goal, Course,
)
from backend.routers.auth import get_current_user

analytics_router = APIRouter()


@analytics_router.get("/workforce")
async def workforce_analytics(db: Session = Depends(get_db), _=Depends(get_current_user)):
    """Headcount, turnover, tenure analysis."""
    today = date.today()

    # Headcount by department
    dept_headcount = db.query(
        Department.name, func.count(Employee.id)
    ).join(Employee, Employee.department_id == Department.id
    ).filter(Employee.status == "ACTIVE"
    ).group_by(Department.name).order_by(func.count(Employee.id).desc()).all()

    total_active = sum(c for _, c in dept_headcount)

    # Employee type distribution
    type_dist = db.query(
        Employee.employee_type, func.count(Employee.id)
    ).filter(Employee.status == "ACTIVE"
    ).group_by(Employee.employee_type).all()

    # Gender distribution
    gender_dist = db.query(
        Employee.gender, func.count(Employee.id)
    ).filter(Employee.status == "ACTIVE", Employee.gender.isnot(None)
    ).group_by(Employee.gender).all()

    # Status distribution (all statuses, not just active)
    status_dist = db.query(
        Employee.status, func.count(Employee.id)
    ).group_by(Employee.status).all()

    # Turnover rate: terminated in last 12 months / avg headcount * 100
    twelve_months_ago = today - timedelta(days=365)
    terminated_12m = db.query(func.count(Employee.id)).filter(
        Employee.status == "TERMINATED",
        Employee.termination_date >= twelve_months_ago,
    ).scalar() or 0
    avg_headcount = total_active + (terminated_12m / 2)
    turnover_rate = round((terminated_12m / avg_headcount) * 100, 1) if avg_headcount else 0

    # Average tenure in months
    active_employees = db.query(Employee).filter(Employee.status == "ACTIVE").all()
    if active_employees:
        total_days = sum((today - e.hire_date).days for e in active_employees)
        avg_tenure = round(total_days / len(active_employees) / 30.44, 1)
    else:
        avg_tenure = 0

    # Tenure distribution
    tenure_buckets = {"<1 year": 0, "1-3 years": 0, "3-5 years": 0, "5-10 years": 0, "10+ years": 0}
    for e in active_employees:
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
        "total_employees": total_active,
        "turnover_rate": turnover_rate,
        "avg_tenure": avg_tenure,
        "by_department": [{"name": n, "count": c} for n, c in dept_headcount],
        "by_type": [{"type": t.replace("_", " ").title(), "count": c} for t, c in type_dist],
        "by_gender": [{"gender": (g or "Not Specified").replace("_", " ").title(), "count": c} for g, c in gender_dist],
        "by_status": [{"status": s.replace("_", " ").title(), "count": c} for s, c in status_dist],
        "tenure_distribution": [{"label": k, "value": v} for k, v in tenure_buckets.items()],
        "trade_distribution": [{"label": t or "N/A", "value": c} for t, c in trade_dist],
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
    rating_sum = 0
    rating_count = 0
    for (r,) in ratings:
        bucket = min(5, max(1, round(r)))
        rating_dist[bucket] += 1
        rating_sum += r
        rating_count += 1

    avg_rating = round(rating_sum / rating_count, 2) if rating_count else None

    labels = {1: "Unsatisfactory", 2: "Needs Improvement", 3: "Meets Expectations",
              4: "Exceeds", 5: "Exceptional"}

    # Review completion
    total_reviews = db.query(func.count(PerformanceReview.id)).scalar() or 0
    completed = db.query(func.count(PerformanceReview.id)).filter(
        PerformanceReview.status == "COMPLETED"
    ).scalar() or 0
    review_completion_rate = round(completed / total_reviews * 100, 1) if total_reviews else 0

    # Avg rating by department
    dept_avg = db.query(
        Department.name, func.avg(PerformanceReview.overall_rating)
    ).join(Employee, Employee.id == PerformanceReview.employee_id
    ).join(Department, Department.id == Employee.department_id
    ).filter(
        PerformanceReview.status == "COMPLETED",
        PerformanceReview.overall_rating.isnot(None),
    ).group_by(Department.name).all()

    # Goal status
    goal_status = db.query(
        Goal.status, func.count(Goal.id)
    ).group_by(Goal.status).all()

    # Incident summary
    incident_types = db.query(
        Incident.type, func.count(Incident.id)
    ).group_by(Incident.type).all()

    return {
        "avg_rating": avg_rating,
        "review_completion_rate": review_completion_rate,
        "rating_distribution": [{"rating": labels.get(k, str(k)), "count": v} for k, v in sorted(rating_dist.items())],
        "by_department": [{"dept": n, "avg": round(a, 2) if a else 0} for n, a in dept_avg],
        "review_completion": {"total": total_reviews, "completed": completed, "rate": review_completion_rate},
        "goal_status": [{"label": s.replace("_", " ").title(), "value": c} for s, c in goal_status],
        "incident_summary": [{"label": t.replace("_", " ").title(), "value": c} for t, c in incident_types],
    }


@analytics_router.get("/training")
async def training_analytics(db: Session = Depends(get_db), _=Depends(get_current_user)):
    """Compliance, training hours, certification forecasts."""
    # Total courses
    total_courses = db.query(func.count(Course.id)).scalar() or 0

    # Compliance rate: VALID certs / total certs
    total_certs = db.query(func.count(Certification.id)).scalar() or 0
    valid_certs = db.query(func.count(Certification.id)).filter(
        Certification.status == "VALID"
    ).scalar() or 0
    compliance_rate = round((valid_certs / total_certs) * 100, 1) if total_certs else 0

    # Courses by category
    category_dist = db.query(
        Course.category, func.count(Course.id)
    ).filter(Course.category.isnot(None)
    ).group_by(Course.category).all()

    # Monthly completion trend (last 6 months)
    today = date.today()
    completion_trend = []
    for i in range(5, -1, -1):
        month_start = (today.replace(day=1) - timedelta(days=30 * i)).replace(day=1)
        if month_start.month == 12:
            month_end = month_start.replace(year=month_start.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            month_end = month_start.replace(month=month_start.month + 1, day=1) - timedelta(days=1)
        count = db.query(func.count(TrainingAssignment.id)).filter(
            TrainingAssignment.status == "COMPLETED",
            TrainingAssignment.completed_date >= month_start,
            TrainingAssignment.completed_date <= month_end,
        ).scalar() or 0
        completion_trend.append({
            "month": month_start.strftime("%b %Y"),
            "completed": count,
        })

    # Cert status distribution (keep existing)
    cert_status = db.query(
        Certification.status, func.count(Certification.id)
    ).group_by(Certification.status).all()

    # Training completion (keep existing)
    assign_status = db.query(
        TrainingAssignment.status, func.count(TrainingAssignment.id)
    ).group_by(TrainingAssignment.status).all()

    # Expiring forecast (keep existing)
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
        "total_courses": total_courses,
        "compliance_rate": compliance_rate,
        "by_category": [{"category": c or "Uncategorized", "count": n} for c, n in category_dist],
        "completion_trend": completion_trend,
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
    # Department count
    department_count = db.query(func.count(Department.id)).scalar() or 0

    # Span of control
    managers = db.query(Employee).filter(Employee.status == "ACTIVE").all()
    span_data = []
    for m in managers:
        direct = db.query(func.count(Employee.id)).filter(
            Employee.reports_to_id == m.id
        ).scalar() or 0
        if direct > 0:
            span_data.append(direct)

    # Hierarchy depth: max reporting chain
    def get_depth(emp_id, visited=None):
        if visited is None:
            visited = set()
        if emp_id in visited:
            return 0
        visited.add(emp_id)
        subordinates = db.query(Employee.id).filter(Employee.reports_to_id == emp_id).all()
        if not subordinates:
            return 1
        return 1 + max(get_depth(s.id, visited) for s in subordinates)

    top_managers = db.query(Employee).filter(
        Employee.status == "ACTIVE",
        Employee.reports_to_id.is_(None),
    ).all()
    hierarchy_depth = max((get_depth(m.id) for m in top_managers), default=0) if top_managers else 0

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

    # Division headcount + dept count per division
    div_data = db.query(
        Division.name,
        func.count(func.distinct(Employee.id)),
        func.count(func.distinct(Department.id)),
    ).join(Department, Department.division_id == Division.id
    ).join(Employee, Employee.department_id == Department.id
    ).filter(Employee.status == "ACTIVE"
    ).group_by(Division.name).all()

    return {
        "department_count": department_count,
        "hierarchy_depth": hierarchy_depth,
        "avg_span": round(sum(span_data) / len(span_data), 1) if span_data else 0,
        "span_of_control": [{"label": k, "value": v} for k, v in span_dist.items()],
        "by_division": [{"division": n, "employee_count": ec, "dept_count": dc} for n, ec, dc in div_data],
    }
