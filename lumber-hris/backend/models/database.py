"""
Lumber HRIS — SQLAlchemy Models & Database Configuration
All 20+ models for Summit Construction Group HRIS
"""
import uuid
import os
from datetime import datetime, date
from enum import Enum as PyEnum

from sqlalchemy import (
    Column, String, Integer, Float, Boolean, Text, Date, DateTime,
    ForeignKey, Enum as SAEnum, create_engine, event,
)
from sqlalchemy.orm import relationship, sessionmaker, declarative_base

Base = declarative_base()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./lumber_hris.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=False,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def uid():
    return str(uuid.uuid4())


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    # Enable WAL mode for SQLite (better concurrent reads)
    if "sqlite" in DATABASE_URL:
        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
    Base.metadata.create_all(bind=engine)


# ============================================================
# ENUMS
# ============================================================

class RoleEnum(str, PyEnum):
    ADMIN = "ADMIN"
    HR_MANAGER = "HR_MANAGER"
    PROJECT_MANAGER = "PROJECT_MANAGER"
    FOREMAN = "FOREMAN"
    EMPLOYEE = "EMPLOYEE"

class EmployeeTypeEnum(str, PyEnum):
    FULL_TIME = "FULL_TIME"
    PART_TIME = "PART_TIME"
    CONTRACTOR = "CONTRACTOR"
    CASUAL = "CASUAL"

class EmployeeStatusEnum(str, PyEnum):
    ACTIVE = "ACTIVE"
    ON_LEAVE = "ON_LEAVE"
    SUSPENDED = "SUSPENDED"
    TERMINATED = "TERMINATED"

class GenderEnum(str, PyEnum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"
    PREFER_NOT_TO_SAY = "PREFER_NOT_TO_SAY"

class PayTypeEnum(str, PyEnum):
    HOURLY = "HOURLY"
    SALARY = "SALARY"

class LocationTypeEnum(str, PyEnum):
    OFFICE = "OFFICE"
    FIELD = "FIELD"
    WAREHOUSE = "WAREHOUSE"

class ProjectStatusEnum(str, PyEnum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    PLANNED = "PLANNED"

class ReviewTypeEnum(str, PyEnum):
    ANNUAL = "ANNUAL"
    MID_YEAR = "MID_YEAR"
    THIRTY_SIXTY_NINETY = "THIRTY_SIXTY_NINETY"
    PROJECT_CLOSEOUT = "PROJECT_CLOSEOUT"
    PIP = "PIP"

class ReviewStatusEnum(str, PyEnum):
    DRAFT = "DRAFT"
    SELF_REVIEW = "SELF_REVIEW"
    MANAGER_REVIEW = "MANAGER_REVIEW"
    PENDING_SIGN_OFF = "PENDING_SIGN_OFF"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class ReviewCycleStatusEnum(str, PyEnum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"

class GoalCategoryEnum(str, PyEnum):
    SAFETY = "SAFETY"
    QUALITY = "QUALITY"
    PRODUCTIVITY = "PRODUCTIVITY"
    DEVELOPMENT = "DEVELOPMENT"
    LEADERSHIP = "LEADERSHIP"

class GoalStatusEnum(str, PyEnum):
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    AT_RISK = "AT_RISK"
    COMPLETED = "COMPLETED"
    DEFERRED = "DEFERRED"

class IncidentTypeEnum(str, PyEnum):
    SAFETY = "SAFETY"
    ATTENDANCE = "ATTENDANCE"
    QUALITY = "QUALITY"
    CONDUCT = "CONDUCT"

class SeverityEnum(str, PyEnum):
    MINOR = "MINOR"
    MODERATE = "MODERATE"
    MAJOR = "MAJOR"
    CRITICAL = "CRITICAL"

class IncidentStatusEnum(str, PyEnum):
    OPEN = "OPEN"
    INVESTIGATING = "INVESTIGATING"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"

class CommendationCategoryEnum(str, PyEnum):
    SAFETY = "SAFETY"
    QUALITY = "QUALITY"
    TEAMWORK = "TEAMWORK"
    ABOVE_AND_BEYOND = "ABOVE_AND_BEYOND"

class CourseFormatEnum(str, PyEnum):
    E_LEARNING = "E_LEARNING"
    INSTRUCTOR_LED = "INSTRUCTOR_LED"
    TOOLBOX_TALK = "TOOLBOX_TALK"

class TrainingStatusEnum(str, PyEnum):
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    OVERDUE = "OVERDUE"

class CertStatusEnum(str, PyEnum):
    VALID = "VALID"
    EXPIRING_SOON = "EXPIRING_SOON"
    EXPIRED = "EXPIRED"
    REVOKED = "REVOKED"

class TrainingRuleTriggerEnum(str, PyEnum):
    NEW_HIRE = "NEW_HIRE"
    CERT_EXPIRING = "CERT_EXPIRING"
    LOW_REVIEW_SCORE = "LOW_REVIEW_SCORE"

class PIPStatusEnum(str, PyEnum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    EXTENDED = "EXTENDED"
    FAILED = "FAILED"

class MilestoneStatusEnum(str, PyEnum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    MISSED = "MISSED"

class AuditActionEnum(str, PyEnum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


# ============================================================
# MODELS
# ============================================================

class Company(Base):
    __tablename__ = "companies"
    id = Column(String(36), primary_key=True, default=uid)
    name = Column(String(200), nullable=False)
    code = Column(String(20), nullable=False)
    address = Column(String(300))
    city = Column(String(100))
    state = Column(String(50))
    zip = Column(String(20))
    divisions = relationship("Division", back_populates="company")


class Division(Base):
    __tablename__ = "divisions"
    id = Column(String(36), primary_key=True, default=uid)
    name = Column(String(200), nullable=False)
    code = Column(String(20), nullable=False)
    company_id = Column(String(36), ForeignKey("companies.id"))
    company = relationship("Company", back_populates="divisions")
    departments = relationship("Department", back_populates="division")


class Department(Base):
    __tablename__ = "departments"
    id = Column(String(36), primary_key=True, default=uid)
    name = Column(String(200), nullable=False)
    code = Column(String(20), nullable=False)
    division_id = Column(String(36), ForeignKey("divisions.id"))
    cost_center = Column(String(50))
    manager_id = Column(String(36), ForeignKey("employees.id"), nullable=True)
    division = relationship("Division", back_populates="departments")
    employees = relationship("Employee", back_populates="department", foreign_keys="Employee.department_id")


class Location(Base):
    __tablename__ = "locations"
    id = Column(String(36), primary_key=True, default=uid)
    name = Column(String(200), nullable=False)
    address = Column(String(300))
    city = Column(String(100))
    state = Column(String(50))
    type = Column(String(20), default="FIELD")


class User(Base):
    __tablename__ = "users"
    id = Column(String(36), primary_key=True, default=uid)
    email = Column(String(200), unique=True, index=True, nullable=False)
    password_hash = Column(String(300), nullable=False)
    role = Column(String(30), nullable=False, default="EMPLOYEE")
    employee_id = Column(String(36), ForeignKey("employees.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Employee(Base):
    __tablename__ = "employees"
    id = Column(String(36), primary_key=True, default=uid)
    employee_number = Column(String(20), unique=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(200), unique=True, nullable=False)
    phone = Column(String(30))
    address = Column(String(300))
    city = Column(String(100))
    state = Column(String(50))
    zip = Column(String(20))
    date_of_birth = Column(Date)
    ssn_last_four = Column(String(4))
    gender = Column(String(30))
    ethnicity = Column(String(50))
    veteran_status = Column(Boolean, default=False)
    photo_url = Column(String(500))

    employee_type = Column(String(20), nullable=False, default="FULL_TIME")
    status = Column(String(20), nullable=False, default="ACTIVE")
    hire_date = Column(Date, nullable=False)
    original_hire_date = Column(Date)
    termination_date = Column(Date)
    termination_reason = Column(String(300))

    department_id = Column(String(36), ForeignKey("departments.id"))
    division_id = Column(String(36), ForeignKey("divisions.id"))
    location_id = Column(String(36), ForeignKey("locations.id"))

    job_title = Column(String(200), nullable=False)
    job_level = Column(String(50))
    trade = Column(String(100))

    pay_rate = Column(Float, default=0)
    pay_type = Column(String(10), default="HOURLY")

    reports_to_id = Column(String(36), ForeignKey("employees.id"))

    union_name = Column(String(200))
    union_local = Column(String(100))
    union_seniority_date = Column(Date)

    cost_center = Column(String(50))
    bonus_eligible = Column(Boolean, default=False)
    per_diem_eligible = Column(Boolean, default=False)
    travel_auth_level = Column(String(50))
    vehicle_allowance = Column(Boolean, default=False)

    eeo_category = Column(String(50))
    i9_status = Column(String(50))
    work_auth_expiry = Column(Date)

    notes = Column(Text)
    emergency_contact_name = Column(String(200))
    emergency_contact_phone = Column(String(30))
    emergency_contact_relation = Column(String(100))

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    department = relationship("Department", back_populates="employees", foreign_keys=[department_id])
    reports_to = relationship("Employee", remote_side="Employee.id", foreign_keys=[reports_to_id])
    direct_reports = relationship("Employee", foreign_keys=[reports_to_id], overlaps="reports_to")
    job_history = relationship("JobHistory", back_populates="employee")
    reviews = relationship("PerformanceReview", back_populates="employee", foreign_keys="PerformanceReview.employee_id")
    goals = relationship("Goal", back_populates="employee")
    certifications = relationship("Certification", back_populates="employee")
    training_assignments = relationship("TrainingAssignment", back_populates="employee")
    project_assignments = relationship("ProjectAssignment", back_populates="employee")


class Project(Base):
    __tablename__ = "projects"
    id = Column(String(36), primary_key=True, default=uid)
    name = Column(String(200), nullable=False)
    code = Column(String(30), nullable=False)
    status = Column(String(20), default="ACTIVE")
    location_id = Column(String(36), ForeignKey("locations.id"))
    start_date = Column(Date)
    end_date = Column(Date)
    project_manager_id = Column(String(36), ForeignKey("employees.id"))
    project_manager = relationship("Employee", foreign_keys=[project_manager_id])
    assignments = relationship("ProjectAssignment", back_populates="project")


class ProjectAssignment(Base):
    __tablename__ = "project_assignments"
    id = Column(String(36), primary_key=True, default=uid)
    project_id = Column(String(36), ForeignKey("projects.id"))
    employee_id = Column(String(36), ForeignKey("employees.id"))
    role = Column(String(100))
    crew_name = Column(String(100))
    start_date = Column(Date)
    end_date = Column(Date)
    project = relationship("Project", back_populates="assignments")
    employee = relationship("Employee", back_populates="project_assignments")


class JobHistory(Base):
    __tablename__ = "job_history"
    id = Column(String(36), primary_key=True, default=uid)
    employee_id = Column(String(36), ForeignKey("employees.id"))
    job_title = Column(String(200))
    department_name = Column(String(200))
    location_name = Column(String(200))
    start_date = Column(Date)
    end_date = Column(Date)
    reason = Column(String(300))
    salary = Column(Float)
    changed_by_id = Column(String(36), ForeignKey("users.id"))
    employee = relationship("Employee", back_populates="job_history")


class ReviewCycle(Base):
    __tablename__ = "review_cycles"
    id = Column(String(36), primary_key=True, default=uid)
    name = Column(String(200), nullable=False)
    type = Column(String(50))
    period_start = Column(Date)
    period_end = Column(Date)
    status = Column(String(20), default="DRAFT")
    departments_json = Column(Text)


class PerformanceReview(Base):
    __tablename__ = "performance_reviews"
    id = Column(String(36), primary_key=True, default=uid)
    employee_id = Column(String(36), ForeignKey("employees.id"))
    reviewer_id = Column(String(36), ForeignKey("employees.id"))
    review_cycle_id = Column(String(36), ForeignKey("review_cycles.id"))
    type = Column(String(30), default="ANNUAL")
    status = Column(String(30), default="DRAFT")
    period_start = Column(Date)
    period_end = Column(Date)
    due_date = Column(Date)
    overall_rating = Column(Float)
    manager_comments = Column(Text)
    employee_comments = Column(Text)
    development_plan = Column(Text)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    employee = relationship("Employee", back_populates="reviews", foreign_keys=[employee_id])
    reviewer = relationship("Employee", foreign_keys=[reviewer_id])
    criteria = relationship("ReviewCriteria", back_populates="review")


class ReviewCriteria(Base):
    __tablename__ = "review_criteria"
    id = Column(String(36), primary_key=True, default=uid)
    review_id = Column(String(36), ForeignKey("performance_reviews.id"))
    name = Column(String(200))
    category = Column(String(100))
    weight = Column(Float, default=1.0)
    rating = Column(Integer)
    comments = Column(Text)
    review = relationship("PerformanceReview", back_populates="criteria")


class Goal(Base):
    __tablename__ = "goals"
    id = Column(String(36), primary_key=True, default=uid)
    employee_id = Column(String(36), ForeignKey("employees.id"))
    parent_goal_id = Column(String(36), ForeignKey("goals.id"))
    title = Column(String(300), nullable=False)
    description = Column(Text)
    category = Column(String(30), default="DEVELOPMENT")
    target_date = Column(Date)
    weight = Column(Float, default=1.0)
    percent_complete = Column(Integer, default=0)
    status = Column(String(20), default="NOT_STARTED")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    employee = relationship("Employee", back_populates="goals")


class Incident(Base):
    __tablename__ = "incidents"
    id = Column(String(36), primary_key=True, default=uid)
    employee_id = Column(String(36), ForeignKey("employees.id"))
    reported_by_id = Column(String(36), ForeignKey("employees.id"))
    type = Column(String(20))
    severity = Column(String(20))
    description = Column(Text, nullable=False)
    incident_date = Column(Date)
    location = Column(String(200))
    witnesses = Column(Text)
    status = Column(String(20), default="OPEN")
    resolution = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    employee = relationship("Employee", foreign_keys=[employee_id])
    reported_by = relationship("Employee", foreign_keys=[reported_by_id])


class Commendation(Base):
    __tablename__ = "commendations"
    id = Column(String(36), primary_key=True, default=uid)
    employee_id = Column(String(36), ForeignKey("employees.id"))
    awarded_by_id = Column(String(36), ForeignKey("employees.id"))
    category = Column(String(30))
    stars = Column(Integer, default=3)
    description = Column(Text, nullable=False)
    is_public = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    employee = relationship("Employee", foreign_keys=[employee_id])
    awarded_by = relationship("Employee", foreign_keys=[awarded_by_id])


class Course(Base):
    __tablename__ = "courses"
    id = Column(String(36), primary_key=True, default=uid)
    title = Column(String(300), nullable=False)
    description = Column(Text)
    category = Column(String(100))
    format = Column(String(30), default="INSTRUCTOR_LED")
    duration_hours = Column(Float, default=1.0)
    prerequisites_json = Column(Text)
    certification_granted = Column(String(200))
    provider = Column(String(200))
    is_required = Column(Boolean, default=False)
    trade_specific = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)


class TrainingAssignment(Base):
    __tablename__ = "training_assignments"
    id = Column(String(36), primary_key=True, default=uid)
    employee_id = Column(String(36), ForeignKey("employees.id"))
    course_id = Column(String(36), ForeignKey("courses.id"))
    assigned_by_id = Column(String(36), ForeignKey("users.id"))
    status = Column(String(20), default="ASSIGNED")
    due_date = Column(Date)
    completed_date = Column(Date)
    score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    employee = relationship("Employee", back_populates="training_assignments")
    course = relationship("Course")


class Certification(Base):
    __tablename__ = "certifications"
    id = Column(String(36), primary_key=True, default=uid)
    employee_id = Column(String(36), ForeignKey("employees.id"))
    name = Column(String(300), nullable=False)
    issuing_body = Column(String(200))
    cert_number = Column(String(100))
    issue_date = Column(Date)
    expiration_date = Column(Date)
    status = Column(String(20), default="VALID")
    attachment_url = Column(String(500))
    course_id = Column(String(36), ForeignKey("courses.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    employee = relationship("Employee", back_populates="certifications")
    course = relationship("Course")


class TrainingRule(Base):
    __tablename__ = "training_rules"
    id = Column(String(36), primary_key=True, default=uid)
    name = Column(String(200), nullable=False)
    trigger_type = Column(String(30))
    trigger_config_json = Column(Text)
    action_course_ids_json = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class PIP(Base):
    __tablename__ = "pips"
    id = Column(String(36), primary_key=True, default=uid)
    employee_id = Column(String(36), ForeignKey("employees.id"))
    created_by_id = Column(String(36), ForeignKey("users.id"))
    issue_description = Column(Text, nullable=False)
    improvement_targets_json = Column(Text)
    start_date = Column(Date)
    end_date = Column(Date)
    status = Column(String(20), default="ACTIVE")
    outcome = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    employee = relationship("Employee", foreign_keys=[employee_id])
    milestones = relationship("PIPMilestone", back_populates="pip")


class PIPMilestone(Base):
    __tablename__ = "pip_milestones"
    id = Column(String(36), primary_key=True, default=uid)
    pip_id = Column(String(36), ForeignKey("pips.id"))
    title = Column(String(300), nullable=False)
    description = Column(Text)
    due_date = Column(Date)
    completed_date = Column(Date)
    status = Column(String(20), default="PENDING")
    pip = relationship("PIP", back_populates="milestones")


class AuditLog(Base):
    __tablename__ = "audit_log"
    id = Column(String(36), primary_key=True, default=uid)
    entity_type = Column(String(100))
    entity_id = Column(String(36))
    action = Column(String(20))
    field = Column(String(200))
    old_value = Column(Text)
    new_value = Column(Text)
    user_id = Column(String(36), ForeignKey("users.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
