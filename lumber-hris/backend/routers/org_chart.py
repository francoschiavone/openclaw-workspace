"""Org Chart endpoints — corporate hierarchy and project/crew views"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from backend.models.database import (
    get_db, Employee, Department, Division, Project, ProjectAssignment, Certification,
)
from backend.routers.auth import get_current_user

org_chart_router = APIRouter()


def _build_node(emp, db, include_children=False, depth=0, max_depth=10):
    """Build an org chart node for an employee."""
    dept = db.query(Department).get(emp.department_id) if emp.department_id else None
    direct_count = db.query(func.count(Employee.id)).filter(
        Employee.reports_to_id == emp.id
    ).scalar() or 0

    # Cert status
    from datetime import date, timedelta
    today = date.today()
    certs = db.query(Certification).filter(Certification.employee_id == emp.id).all()
    cert_status = "ok"
    for c in certs:
        if c.status == "EXPIRED":
            cert_status = "expired"
            break
        elif c.status == "EXPIRING_SOON":
            cert_status = "expiring"

    node = {
        "id": emp.id,
        "employee_number": emp.employee_number,
        "name": f"{emp.first_name} {emp.last_name}",
        "first_name": emp.first_name,
        "last_name": emp.last_name,
        "job_title": emp.job_title,
        "department": dept.name if dept else "",
        "trade": emp.trade,
        "photo_url": emp.photo_url,
        "reports_to_id": emp.reports_to_id or "",
        "direct_reports_count": direct_count,
        "cert_status": cert_status,
        "span_color": "green" if direct_count <= 8 else ("yellow" if direct_count <= 12 else "red"),
    }

    if include_children and depth < max_depth:
        children = db.query(Employee).filter(
            Employee.reports_to_id == emp.id,
            Employee.status == "ACTIVE",
        ).order_by(Employee.last_name).all()
        node["children"] = [_build_node(c, db, True, depth + 1, max_depth) for c in children]

    return node


@org_chart_router.get("/corporate")
async def corporate_hierarchy(
    depth: int = Query(3, ge=1, le=10),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """Full corporate hierarchy tree starting from CEO (no reports_to)."""
    roots = db.query(Employee).filter(
        Employee.reports_to_id.is_(None),
        Employee.status == "ACTIVE",
    ).all()
    return [_build_node(r, db, include_children=True, max_depth=depth) for r in roots]


@org_chart_router.get("/flat")
async def flat_org_data(db: Session = Depends(get_db), _=Depends(get_current_user)):
    """Flat list of all employees for d3-org-chart (it builds the tree client-side)."""
    employees = db.query(Employee).filter(Employee.status == "ACTIVE").all()
    nodes = []
    for emp in employees:
        dept = db.query(Department).get(emp.department_id) if emp.department_id else None
        direct_count = db.query(func.count(Employee.id)).filter(
            Employee.reports_to_id == emp.id
        ).scalar() or 0
        certs = db.query(Certification).filter(Certification.employee_id == emp.id).all()
        cert_status = "ok"
        for c in certs:
            if c.status == "EXPIRED":
                cert_status = "expired"
                break
            elif c.status == "EXPIRING_SOON":
                cert_status = "expiring"

        nodes.append({
            "id": emp.id,
            "parentId": emp.reports_to_id or "",
            "employee_number": emp.employee_number,
            "name": f"{emp.first_name} {emp.last_name}",
            "job_title": emp.job_title,
            "department": dept.name if dept else "",
            "trade": emp.trade or "",
            "photo_url": emp.photo_url or "",
            "direct_reports": direct_count,
            "cert_status": cert_status,
        })
    return nodes


@org_chart_router.get("/projects")
async def project_crews(db: Session = Depends(get_db), _=Depends(get_current_user)):
    """Project/Crew tree view."""
    projects = db.query(Project).filter(Project.status == "ACTIVE").all()
    result = []
    for proj in projects:
        pm = db.query(Employee).get(proj.project_manager_id) if proj.project_manager_id else None
        assignments = db.query(ProjectAssignment).filter(
            ProjectAssignment.project_id == proj.id
        ).all()

        # Group by crew
        crews = {}
        for a in assignments:
            crew = a.crew_name or "Unassigned"
            if crew not in crews:
                crews[crew] = []
            emp = db.query(Employee).get(a.employee_id)
            if emp:
                crews[crew].append({
                    "id": emp.id,
                    "name": f"{emp.first_name} {emp.last_name}",
                    "job_title": emp.job_title,
                    "trade": emp.trade,
                    "role": a.role,
                })

        result.append({
            "id": proj.id,
            "name": proj.name,
            "code": proj.code,
            "status": proj.status,
            "project_manager": f"{pm.first_name} {pm.last_name}" if pm else "TBD",
            "total_workers": len(assignments),
            "crews": [{"name": k, "members": v} for k, v in crews.items()],
        })
    return result


@org_chart_router.get("/search")
async def search_org(
    q: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """Search employees in org context."""
    from sqlalchemy import or_
    term = f"%{q}%"
    employees = db.query(Employee).filter(
        Employee.status == "ACTIVE",
        or_(Employee.first_name.ilike(term), Employee.last_name.ilike(term)),
    ).limit(20).all()
    return [{"id": e.id, "name": f"{e.first_name} {e.last_name}", "job_title": e.job_title} for e in employees]
