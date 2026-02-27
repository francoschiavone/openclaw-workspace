"""
Employee Management Router — CRUD, search, filter, pagination
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, func
from typing import Optional, List
from pydantic import BaseModel
from datetime import date

from backend.models.database import get_db, Employee, Department, Division, Location, JobHistory, AuditLog, Certification, TrainingAssignment, Course, PerformanceReview, Incident, Commendation, ProjectAssignment, Project
from backend.routers.auth import get_current_user, require_role, User

employee_router = APIRouter()


# ---- Response Schemas ----

class EmployeeBrief(BaseModel):
    id: str
    employee_number: str
    first_name: str
    last_name: str
    job_title: str
    department_name: str = ""
    photo_url: Optional[str] = None

    class Config:
        from_attributes = True

class EmployeeResponse(BaseModel):
    id: str
    employee_number: str
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    ethnicity: Optional[str] = None
    veteran_status: bool = False
    photo_url: Optional[str] = None
    employee_type: str
    status: str
    hire_date: date
    job_title: str
    job_level: Optional[str] = None
    trade: Optional[str] = None
    pay_rate: float = 0
    pay_type: str = "HOURLY"
    department_id: Optional[str] = None
    department_name: str = ""
    division_name: str = ""
    location_name: Optional[str] = None
    reports_to_id: Optional[str] = None
    reports_to_name: Optional[str] = None
    union_name: Optional[str] = None
    union_local: Optional[str] = None
    cost_center: Optional[str] = None
    bonus_eligible: bool = False
    per_diem_eligible: bool = False
    notes: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    direct_reports_count: int = 0

    class Config:
        from_attributes = True

class EmployeeListResponse(BaseModel):
    items: List[EmployeeResponse]
    total: int
    page: int
    per_page: int

class EmployeeCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    employee_type: str = "FULL_TIME"
    hire_date: date
    job_title: str
    job_level: Optional[str] = None
    trade: Optional[str] = None
    pay_rate: float = 0
    pay_type: str = "HOURLY"
    department_id: Optional[str] = None
    division_id: Optional[str] = None
    location_id: Optional[str] = None
    reports_to_id: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    gender: Optional[str] = None
    union_name: Optional[str] = None
    union_local: Optional[str] = None

class EmployeeUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    status: Optional[str] = None
    employee_type: Optional[str] = None
    job_title: Optional[str] = None
    job_level: Optional[str] = None
    trade: Optional[str] = None
    pay_rate: Optional[float] = None
    pay_type: Optional[str] = None
    department_id: Optional[str] = None
    location_id: Optional[str] = None
    reports_to_id: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    notes: Optional[str] = None

class JobHistoryResponse(BaseModel):
    id: str
    job_title: Optional[str] = None
    department_name: Optional[str] = None
    location_name: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    reason: Optional[str] = None
    salary: Optional[float] = None

    class Config:
        from_attributes = True


# ---- Helper ----

def _build_employee_response(emp: Employee, db: Session) -> EmployeeResponse:
    dept_name = ""
    div_name = ""
    loc_name = None
    reports_name = None

    if emp.department_id:
        dept = db.query(Department).get(emp.department_id)
        if dept:
            dept_name = dept.name
            div = db.query(Division).get(dept.division_id) if dept.division_id else None
            div_name = div.name if div else ""

    if emp.location_id:
        loc = db.query(Location).get(emp.location_id)
        loc_name = loc.name if loc else None

    if emp.reports_to_id:
        mgr = db.query(Employee).get(emp.reports_to_id)
        reports_name = f"{mgr.first_name} {mgr.last_name}" if mgr else None

    direct_count = db.query(func.count(Employee.id)).filter(Employee.reports_to_id == emp.id).scalar() or 0

    return EmployeeResponse(
        id=emp.id, employee_number=emp.employee_number,
        first_name=emp.first_name, last_name=emp.last_name,
        email=emp.email, phone=emp.phone,
        city=emp.city, state=emp.state,
        date_of_birth=emp.date_of_birth, gender=emp.gender,
        ethnicity=emp.ethnicity, veteran_status=emp.veteran_status,
        photo_url=emp.photo_url,
        employee_type=emp.employee_type, status=emp.status,
        hire_date=emp.hire_date,
        job_title=emp.job_title, job_level=emp.job_level,
        trade=emp.trade, pay_rate=emp.pay_rate, pay_type=emp.pay_type,
        department_id=emp.department_id, department_name=dept_name,
        division_name=div_name, location_name=loc_name,
        reports_to_id=emp.reports_to_id, reports_to_name=reports_name,
        union_name=emp.union_name, union_local=emp.union_local,
        cost_center=emp.cost_center, bonus_eligible=emp.bonus_eligible,
        per_diem_eligible=emp.per_diem_eligible, notes=emp.notes,
        created_at=str(emp.created_at) if emp.created_at else None,
        updated_at=str(emp.updated_at) if emp.updated_at else None,
        direct_reports_count=direct_count,
    )


# ---- Endpoints ----

@employee_router.get("", response_model=EmployeeListResponse)
async def list_employees(
    page: int = Query(1, ge=1),
    per_page: int = Query(25, ge=1, le=100),
    search: Optional[str] = None,
    department_id: Optional[str] = None,
    status: Optional[str] = None,
    employee_type: Optional[str] = None,
    trade: Optional[str] = None,
    union_status: Optional[str] = None,  # "union" or "non-union"
    sort_by: str = "last_name",
    sort_order: str = "asc",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List employees with search, filters, pagination."""
    query = db.query(Employee)

    # Search
    if search:
        term = f"%{search}%"
        query = query.filter(or_(
            Employee.first_name.ilike(term),
            Employee.last_name.ilike(term),
            Employee.email.ilike(term),
            Employee.employee_number.ilike(term),
            Employee.job_title.ilike(term),
        ))

    # Filters
    if department_id:
        query = query.filter(Employee.department_id == department_id)
    if status:
        query = query.filter(Employee.status == status)
    if employee_type:
        query = query.filter(Employee.employee_type == employee_type)
    if trade:
        query = query.filter(Employee.trade == trade)
    if union_status == "union":
        query = query.filter(Employee.union_name.isnot(None))
    elif union_status == "non-union":
        query = query.filter(Employee.union_name.is_(None))

    # Role-based filtering
    if current_user.role == "FOREMAN" and current_user.employee_id:
        # Foreman sees only crew
        query = query.filter(Employee.reports_to_id == current_user.employee_id)
    elif current_user.role == "EMPLOYEE" and current_user.employee_id:
        # Employee sees only self
        query = query.filter(Employee.id == current_user.employee_id)

    # Count
    total = query.count()

    # Sort
    sort_col = getattr(Employee, sort_by, Employee.last_name)
    if sort_order == "desc":
        query = query.order_by(sort_col.desc())
    else:
        query = query.order_by(sort_col.asc())

    # Paginate
    employees = query.offset((page - 1) * per_page).limit(per_page).all()

    return EmployeeListResponse(
        items=[_build_employee_response(e, db) for e in employees],
        total=total, page=page, per_page=per_page,
    )


@employee_router.get("/brief", response_model=List[EmployeeBrief])
async def list_employees_brief(
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Brief employee list for dropdowns, org chart nodes."""
    query = db.query(Employee).filter(Employee.status == "ACTIVE")
    if search:
        term = f"%{search}%"
        query = query.filter(or_(
            Employee.first_name.ilike(term),
            Employee.last_name.ilike(term),
        ))
    employees = query.order_by(Employee.last_name).limit(500).all()
    result = []
    for e in employees:
        dept_name = ""
        if e.department_id:
            dept = db.query(Department).get(e.department_id)
            dept_name = dept.name if dept else ""
        result.append(EmployeeBrief(
            id=e.id, employee_number=e.employee_number,
            first_name=e.first_name, last_name=e.last_name,
            job_title=e.job_title, department_name=dept_name,
            photo_url=e.photo_url,
        ))
    return result


@employee_router.get("/{employee_id}", response_model=EmployeeResponse)
async def get_employee(
    employee_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get single employee with full details."""
    emp = db.query(Employee).get(employee_id)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    # Employee role can only see themselves
    if current_user.role == "EMPLOYEE" and current_user.employee_id != employee_id:
        raise HTTPException(status_code=403, detail="Access denied")
    return _build_employee_response(emp, db)


@employee_router.post("", response_model=EmployeeResponse, status_code=201)
async def create_employee(
    data: EmployeeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN", "HR_MANAGER")),
):
    """Create a new employee."""
    from sqlalchemy import text
    max_num = db.execute(text(
        "SELECT employee_number FROM employees ORDER BY employee_number DESC LIMIT 1"
    )).scalar()
    if max_num:
        num = int(max_num.split("-")[1]) + 1
    else:
        num = 10001

    emp = Employee(
        id=str(__import__('uuid').uuid4()),
        employee_number=f"SCG-{num:05d}",
        first_name=data.first_name, last_name=data.last_name,
        email=data.email, phone=data.phone,
        employee_type=data.employee_type, status="ACTIVE",
        hire_date=data.hire_date, job_title=data.job_title,
        job_level=data.job_level, trade=data.trade,
        pay_rate=data.pay_rate, pay_type=data.pay_type,
        department_id=data.department_id, division_id=data.division_id,
        location_id=data.location_id, reports_to_id=data.reports_to_id,
        city=data.city, state=data.state,
        gender=data.gender, union_name=data.union_name,
        union_local=data.union_local,
    )
    db.add(emp)

    # Audit log
    audit = AuditLog(
        id=str(__import__('uuid').uuid4()),
        entity_type="Employee", entity_id=emp.id,
        action="CREATE", user_id=current_user.id,
    )
    db.add(audit)
    db.commit()
    db.refresh(emp)
    return _build_employee_response(emp, db)


@employee_router.put("/{employee_id}", response_model=EmployeeResponse)
async def update_employee(
    employee_id: str,
    data: EmployeeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN", "HR_MANAGER")),
):
    """Update an employee."""
    emp = db.query(Employee).get(employee_id)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        old_val = getattr(emp, field, None)
        setattr(emp, field, value)
        # Audit each field change
        if old_val != value:
            audit = AuditLog(
                id=str(__import__('uuid').uuid4()),
                entity_type="Employee", entity_id=emp.id,
                action="UPDATE", field=field,
                old_value=str(old_val) if old_val else None,
                new_value=str(value) if value else None,
                user_id=current_user.id,
            )
            db.add(audit)

    db.commit()
    db.refresh(emp)
    return _build_employee_response(emp, db)


@employee_router.get("/{employee_id}/history", response_model=List[JobHistoryResponse])
async def get_job_history(
    employee_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get job history for an employee."""
    history = db.query(JobHistory).filter(
        JobHistory.employee_id == employee_id
    ).order_by(JobHistory.start_date.desc()).all()
    return [JobHistoryResponse.model_validate(h) for h in history]


@employee_router.post("/{employee_id}/status")
async def change_status(
    employee_id: str,
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN", "HR_MANAGER")),
):
    """Change employee status with reason and effective date."""
    emp = db.query(Employee).get(employee_id)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    old_status = emp.status
    new_status = data.get("status", emp.status)
    reason = data.get("reason", "")
    
    # Create job history entry
    from backend.models.database import JobHistory
    import uuid
    history = JobHistory(
        id=str(uuid.uuid4()),
        employee_id=emp.id,
        job_title=emp.job_title,
        department_name=emp.department.name if emp.department else "",
        start_date=emp.hire_date,
        reason=f"Status change: {old_status} → {new_status}. {reason}",
    )
    db.add(history)
    
    emp.status = new_status
    if new_status == "TERMINATED":
        from datetime import date
        emp.termination_date = date.today()
        emp.termination_reason = reason
    
    # Audit
    audit = AuditLog(
        id=str(__import__('uuid').uuid4()),
        entity_type="Employee", entity_id=emp.id,
        action="UPDATE", field="status",
        old_value=old_status, new_value=new_status,
        user_id=current_user.id,
    )
    db.add(audit)
    db.commit()
    return {"status": "ok", "old": old_status, "new": new_status}


@employee_router.get("/export/csv")
async def export_csv(
    search: Optional[str] = None,
    department_id: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN", "HR_MANAGER")),
):
    """Export employees as CSV."""
    from fastapi.responses import StreamingResponse
    import io, csv
    
    query = db.query(Employee)
    if search:
        term = f"%{search}%"
        query = query.filter(or_(
            Employee.first_name.ilike(term),
            Employee.last_name.ilike(term),
            Employee.email.ilike(term),
        ))
    if department_id:
        query = query.filter(Employee.department_id == department_id)
    if status:
        query = query.filter(Employee.status == status)
    
    employees = query.order_by(Employee.last_name).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Employee #", "First Name", "Last Name", "Email", "Phone",
                     "Job Title", "Department", "Trade", "Status", "Type",
                     "Hire Date", "Pay Rate", "Pay Type"])
    for e in employees:
        dept = db.query(Department).get(e.department_id) if e.department_id else None
        writer.writerow([
            e.employee_number, e.first_name, e.last_name, e.email, e.phone or "",
            e.job_title, dept.name if dept else "", e.trade or "", e.status,
            e.employee_type, str(e.hire_date), e.pay_rate, e.pay_type,
        ])
    
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=employees.csv"},
    )


@employee_router.get("/{employee_id}/summary")
async def get_employee_summary(
    employee_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a comprehensive summary for the employee profile — certs, reviews, projects, etc."""
    emp = db.query(Employee).get(employee_id)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    certs = db.query(Certification).filter(Certification.employee_id == employee_id).all()
    assignments = db.query(TrainingAssignment).filter(TrainingAssignment.employee_id == employee_id).all()
    reviews = db.query(PerformanceReview).filter(PerformanceReview.employee_id == employee_id).order_by(PerformanceReview.created_at.desc()).limit(5).all()
    incidents = db.query(Incident).filter(Incident.employee_id == employee_id).all()
    commendations = db.query(Commendation).filter(Commendation.employee_id == employee_id).all()
    proj_assigns = db.query(ProjectAssignment).filter(ProjectAssignment.employee_id == employee_id).all()
    
    return {
        "certifications": [{
            "id": c.id, "name": c.name, "status": c.status,
            "expiration_date": str(c.expiration_date) if c.expiration_date else None,
        } for c in certs],
        "training": [{
            "course": db.query(Course).get(a.course_id).title if a.course_id and db.query(Course).get(a.course_id) else "N/A",
            "status": a.status,
            "due_date": str(a.due_date) if a.due_date else None,
        } for a in assignments],
        "reviews": [{
            "id": r.id, "type": r.type, "status": r.status,
            "rating": r.overall_rating, "period": f"{r.period_start} - {r.period_end}",
        } for r in reviews],
        "incidents": [{"type": i.type, "severity": i.severity, "date": str(i.incident_date)} for i in incidents],
        "commendations": [{"category": c.category, "stars": c.stars, "description": c.description[:80]} for c in commendations],
        "projects": [{
            "name": db.query(Project).get(pa.project_id).name if pa.project_id and db.query(Project).get(pa.project_id) else "N/A",
            "role": pa.role, "crew": pa.crew_name,
        } for pa in proj_assigns],
        "cert_summary": {
            "valid": sum(1 for c in certs if c.status == "VALID"),
            "expiring": sum(1 for c in certs if c.status == "EXPIRING_SOON"),
            "expired": sum(1 for c in certs if c.status == "EXPIRED"),
        },
    }


@employee_router.get("/{employee_id}/audit")
async def get_audit_trail(
    employee_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN", "HR_MANAGER")),
):
    """Get audit trail for an employee."""
    logs = db.query(AuditLog).filter(
        AuditLog.entity_type == "Employee",
        AuditLog.entity_id == employee_id,
    ).order_by(AuditLog.timestamp.desc()).limit(100).all()
    return [{
        "id": l.id, "action": l.action, "field": l.field,
        "old_value": l.old_value, "new_value": l.new_value,
        "timestamp": str(l.timestamp),
    } for l in logs]
