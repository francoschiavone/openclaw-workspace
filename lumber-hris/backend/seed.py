"""
Lumber HRIS — Comprehensive Seed Data Script
Summit Construction Group: 377 employees, 8 projects, 35 courses, 450+ certs
"""
import uuid
import random
from datetime import date, datetime, timedelta
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def uid():
    return str(uuid.uuid4())

def random_date(start: date, end: date) -> date:
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, max(delta, 1)))

def random_phone():
    return f"({random.randint(200,999)}) {random.randint(200,999)}-{random.randint(1000,9999)}"

# ============================================================
# CONSTANTS
# ============================================================
TODAY = date(2026, 2, 27)
STATES = ["FL", "GA", "SC", "NC", "VA", "TX", "CA", "NY"]
CITIES = {
    "FL": ["Miami", "Orlando", "Tampa", "Jacksonville"],
    "GA": ["Atlanta", "Savannah"],
    "SC": ["Charleston", "Columbia"],
    "NC": ["Charlotte", "Raleigh"],
    "VA": ["Richmond", "Norfolk"],
    "TX": ["Houston", "Dallas", "Austin"],
    "CA": ["Los Angeles", "San Francisco"],
    "NY": ["New York", "Buffalo"],
}

TRADES = [
    "Carpentry", "Electrical", "Plumbing", "Ironwork", "Concrete",
    "Welding", "Heavy Equipment", "HVAC", "Pipe Fitting", "Painting",
    "Roofing", "Drywall", "Masonry", "Glazing", "Insulation"
]

FIRST_NAMES_M = [
    "James", "Robert", "Michael", "William", "David", "Richard", "Joseph", "Thomas",
    "Charles", "Christopher", "Daniel", "Matthew", "Anthony", "Mark", "Donald",
    "Steven", "Paul", "Andrew", "Joshua", "Kenneth", "Kevin", "Brian", "George",
    "Timothy", "Ronald", "Edward", "Jason", "Jeffrey", "Ryan", "Jacob",
    "Carlos", "Miguel", "Juan", "Luis", "Jose", "Pedro", "Diego", "Andres",
    "Marco", "Rafael", "Victor", "Omar", "Alejandro", "Fernando", "Roberto",
]
FIRST_NAMES_F = [
    "Mary", "Patricia", "Jennifer", "Linda", "Barbara", "Elizabeth", "Susan",
    "Jessica", "Sarah", "Karen", "Lisa", "Nancy", "Betty", "Margaret", "Sandra",
    "Ashley", "Emily", "Donna", "Michelle", "Dorothy", "Carol", "Amanda",
    "Maria", "Rosa", "Carmen", "Ana", "Isabella", "Valentina", "Lucia", "Elena",
]
LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
    "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
    "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
    "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark",
    "Ramirez", "Lewis", "Robinson", "Walker", "Young", "Allen", "King",
    "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores", "Green",
    "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell",
    "Carter", "Roberts", "Chen", "Kim", "Patel", "O'Brien", "Foster",
    "Washington", "Murphy", "Park", "Chang", "Sullivan",
]

# ============================================================
# SEED FUNCTION
# ============================================================
def seed_database(session):
    """Main seed function — call with a SQLAlchemy session"""
    from backend.models.database import (
        Company, Division, Department, Location, Employee, User,
        Project, ProjectAssignment, JobHistory, PerformanceReview,
        ReviewCycle, ReviewCriteria, Goal, Incident, Commendation,
        Course, TrainingAssignment, Certification, TrainingRule,
        PIP, PIPMilestone, AuditLog
    )

    random.seed(42)  # Reproducible

    # ---- Company ----
    company = Company(id=uid(), name="Summit Construction Group", code="SCG",
                      address="1200 Corporate Blvd", city="Jacksonville", state="FL", zip="32256")
    session.add(company)

    # ---- Locations ----
    locations = []
    loc_data = [
        ("SCG Corporate HQ", "1200 Corporate Blvd", "Jacksonville", "FL", "OFFICE"),
        ("Southeast Regional Office", "500 Peachtree St", "Atlanta", "GA", "OFFICE"),
        ("Downtown Office Tower Site", "100 Main St", "Jacksonville", "FL", "FIELD"),
        ("I-95 Bridge Site", "I-95 Mile Marker 312", "Jacksonville", "FL", "FIELD"),
        ("Water Treatment Plant Site", "2400 Utility Rd", "Orlando", "FL", "FIELD"),
        ("Amazon DC Site", "8000 Logistics Pkwy", "Tampa", "FL", "FIELD"),
        ("Hospital Addition Site", "1500 Medical Center Dr", "Savannah", "GA", "FIELD"),
        ("Highway 301 Site", "Hwy 301 Expansion Zone", "Jacksonville", "FL", "FIELD"),
        ("Solar Farm Site", "12000 Solar Way", "Orlando", "FL", "FIELD"),
        ("Equipment Yard & Warehouse", "3500 Industrial Blvd", "Jacksonville", "FL", "WAREHOUSE"),
    ]
    for name, addr, city, state, ltype in loc_data:
        loc = Location(id=uid(), name=name, address=addr, city=city, state=state, type=ltype)
        locations.append(loc)
        session.add(loc)

    # ---- Divisions ----
    div_heavy = Division(id=uid(), name="Heavy Civil Division", code="HCD", company_id=company.id)
    div_building = Division(id=uid(), name="Building Division", code="BLD", company_id=company.id)
    div_specialty = Division(id=uid(), name="Specialty Division", code="SPD", company_id=company.id)
    div_corporate = Division(id=uid(), name="Corporate", code="CRP", company_id=company.id)
    divisions = [div_heavy, div_building, div_specialty, div_corporate]
    for d in divisions:
        session.add(d)

    # ---- Departments ----
    dept_data = [
        # (name, code, division, target_size)
        ("Bridge & Structures", "BRG", div_heavy, 45),
        ("Highway & Roads", "HWY", div_heavy, 52),
        ("Utilities", "UTL", div_heavy, 38),
        ("Commercial Construction", "COM", div_building, 48),
        ("Industrial Construction", "IND", div_building, 35),
        ("Renovation & Retrofit", "REN", div_building, 28),
        ("Electrical", "ELC", div_specialty, 32),
        ("Mechanical/HVAC", "MEC", div_specialty, 28),
        ("Plumbing & Fire Protection", "PLB", div_specialty, 22),
        ("Executive Office", "EXE", div_corporate, 8),
        ("Human Resources", "HR", div_corporate, 12),
        ("Finance & Accounting", "FIN", div_corporate, 10),
        ("Safety & Compliance", "SAF", div_corporate, 8),
        ("Estimating", "EST", div_corporate, 6),
        ("IT & Technology", "IT", div_corporate, 5),
    ]
    departments = []
    for name, code, div, size in dept_data:
        dept = Department(id=uid(), name=name, code=code, division_id=div.id,
                         cost_center=f"CC-{code}-001")
        departments.append((dept, size))
        session.add(dept)

    session.flush()  # Get IDs

    # ---- Generate Employees ----
    all_employees = []
    employee_number_counter = 10001
    used_names = set()
    used_emails = set()

    def make_employee(first, last, title, dept, level, trade, emp_type, pay_rate, pay_type,
                      hire_date, gender, reports_to=None, is_union=False):
        nonlocal employee_number_counter
        eid = uid()
        state = random.choice(STATES)
        city = random.choice(CITIES[state])
        base_email = f"{first.lower()}.{last.lower()}@summitcg.com"
        email = base_email
        suffix = 2
        while email in used_emails:
            email = f"{first.lower()}.{last.lower()}{suffix}@summitcg.com"
            suffix += 1
        used_emails.add(email)
        emp = Employee(
            id=eid,
            employee_number=f"SCG-{employee_number_counter:05d}",
            first_name=first, last_name=last,
            email=email,
            phone=random_phone(),
            city=city, state=state, zip=f"{random.randint(10000, 99999)}",
            date_of_birth=random_date(date(1960, 1, 1), date(2002, 1, 1)),
            gender=gender,
            ethnicity=random.choice(["White", "Hispanic", "Black", "Asian", "Two or More", "Other"]),
            veteran_status=random.random() < 0.08,
            employee_type=emp_type,
            status="ACTIVE",
            hire_date=hire_date,
            department_id=dept.id,
            division_id=dept.division_id if hasattr(dept, 'division_id') else div_corporate.id,
            location_id=random.choice(locations).id,
            job_title=title,
            job_level=level,
            trade=trade,
            pay_rate=pay_rate,
            pay_type=pay_type,
            reports_to_id=reports_to,
            union_name="International Brotherhood of Construction Workers" if is_union else None,
            union_local=f"Local {random.randint(100, 999)}" if is_union else None,
            union_seniority_date=hire_date if is_union else None,
            cost_center=dept.cost_center if hasattr(dept, 'cost_center') else None,
            bonus_eligible=level in ("Director", "VP", "C-Suite", "Superintendent"),
            per_diem_eligible=level in ("Foreman", "Journeyman", "Apprentice"),
            notes=None,
        )
        employee_number_counter += 1
        all_employees.append(emp)
        session.add(emp)
        return emp

    def pick_name(gender="M"):
        names = FIRST_NAMES_M if gender == "M" else FIRST_NAMES_F
        for _ in range(100):
            first = random.choice(names)
            last = random.choice(LAST_NAMES)
            key = f"{first}_{last}"
            if key not in used_names:
                used_names.add(key)
                return first, last
        # Fallback
        first = random.choice(names)
        last = random.choice(LAST_NAMES) + str(random.randint(1, 99))
        used_names.add(f"{first}_{last}")
        return first, last

    # ---- Executive team ----
    dept_exec = [d for d, _ in departments if d.code == "EXE"][0]
    dept_hr = [d for d, _ in departments if d.code == "HR"][0]
    dept_fin = [d for d, _ in departments if d.code == "FIN"][0]
    dept_saf = [d for d, _ in departments if d.code == "SAF"][0]
    dept_est = [d for d, _ in departments if d.code == "EST"][0]
    dept_it = [d for d, _ in departments if d.code == "IT"][0]

    ceo = make_employee("Richard", "Sterling", "Chief Executive Officer", dept_exec, "C-Suite",
                        None, "FULL_TIME", 185000, "SALARY", date(2010, 3, 15), "MALE")
    coo = make_employee("Thomas", "Mitchell", "Chief Operating Officer", dept_exec, "C-Suite",
                        None, "FULL_TIME", 165000, "SALARY", date(2012, 6, 1), "MALE", ceo.id)
    cfo = make_employee("Daniel", "Park", "Chief Financial Officer", dept_fin, "C-Suite",
                        None, "FULL_TIME", 155000, "SALARY", date(2015, 1, 10), "MALE", ceo.id)

    # Division VPs
    vp_heavy = make_employee("Robert", "Anderson", "VP Heavy Civil", dept_exec, "VP",
                             None, "FULL_TIME", 145000, "SALARY", date(2011, 8, 20), "MALE", coo.id)
    vp_building = make_employee("Jennifer", "Thompson", "VP Building Division", dept_exec, "VP",
                                None, "FULL_TIME", 140000, "SALARY", date(2013, 4, 1), "FEMALE", coo.id)
    vp_specialty = make_employee("James", "Rodriguez", "VP Specialty Division", dept_exec, "VP",
                                 None, "FULL_TIME", 135000, "SALARY", date(2014, 2, 15), "MALE", coo.id)
    vp_hr = make_employee("Sandra", "Lopez", "VP Human Resources", dept_hr, "VP",
                          None, "FULL_TIME", 130000, "SALARY", date(2015, 7, 1), "FEMALE", coo.id)

    # Corporate department heads
    dir_safety = make_employee("Frank", "Murphy", "Director of Safety", dept_saf, "Director",
                               None, "FULL_TIME", 110000, "SALARY", date(2016, 3, 1), "MALE", coo.id)
    dir_est = make_employee("Rachel", "Torres", "Director of Estimating", dept_est, "Director",
                            None, "FULL_TIME", 105000, "SALARY", date(2017, 5, 15), "FEMALE", coo.id)
    dir_it = make_employee("Brian", "Chang", "Director of IT", dept_it, "Director",
                           None, "FULL_TIME", 115000, "SALARY", date(2018, 1, 10), "MALE", coo.id)

    # Corporate staff (fill remaining corporate depts)
    corp_heads = {
        dept_hr: vp_hr, dept_fin: cfo, dept_saf: dir_safety,
        dept_est: dir_est, dept_it: dir_it
    }
    for dept, size in departments:
        if dept.code in ("EXE",):
            continue
        if dept in corp_heads:
            head = corp_heads[dept]
            target = size - 1  # Head already created
            for i in range(target):
                g = "FEMALE" if random.random() < 0.5 else "MALE"
                fn, ln = pick_name("F" if g == "FEMALE" else "M")
                titles = {
                    "HR": ["HR Specialist", "HR Coordinator", "Recruiter", "Benefits Analyst", "HR Generalist", "Payroll Specialist"],
                    "FIN": ["Accountant", "Financial Analyst", "AP Specialist", "AR Specialist", "Controller"],
                    "SAF": ["Safety Inspector", "Safety Coordinator", "Compliance Officer", "EHS Specialist"],
                    "EST": ["Senior Estimator", "Estimator", "Cost Engineer", "Bid Coordinator"],
                    "IT": ["Systems Admin", "IT Support Specialist", "Network Engineer", "Developer"],
                }
                title_list = titles.get(dept.code, ["Specialist"])
                make_employee(fn, ln, random.choice(title_list), dept, "Staff",
                             None, "FULL_TIME", random.randint(55000, 95000), "SALARY",
                             random_date(date(2016, 1, 1), date(2025, 12, 1)), g, head.id)

    # ---- Field departments (9 departments: 3 heavy, 3 building, 3 specialty) ----
    field_depts = [(d, s) for d, s in departments if d.code not in ("EXE", "HR", "FIN", "SAF", "EST", "IT")]

    field_directors = {}
    vp_map = {
        "BRG": vp_heavy, "HWY": vp_heavy, "UTL": vp_heavy,
        "COM": vp_building, "IND": vp_building, "REN": vp_building,
        "ELC": vp_specialty, "MEC": vp_specialty, "PLB": vp_specialty,
    }

    director_names = [
        ("Sarah", "Chen", "F"), ("Marcus", "Williams", "M"), ("Patricia", "Gonzalez", "F"),
        ("David", "Kim", "M"), ("Michael", "O'Brien", "M"), ("Lisa", "Patel", "F"),
        ("Carlos", "Martinez", "M"), ("Amanda", "Foster", "F"), ("Kevin", "Washington", "M"),
    ]

    dept_trades = {
        "BRG": ["Ironwork", "Concrete", "Carpentry", "Welding"],
        "HWY": ["Heavy Equipment", "Concrete", "Carpentry", "Painting"],
        "UTL": ["Pipe Fitting", "Heavy Equipment", "Welding", "Concrete"],
        "COM": ["Carpentry", "Concrete", "Drywall", "Masonry"],
        "IND": ["Welding", "Ironwork", "Concrete", "Heavy Equipment"],
        "REN": ["Carpentry", "Painting", "Drywall", "Masonry"],
        "ELC": ["Electrical"],
        "MEC": ["HVAC"],
        "PLB": ["Plumbing", "Pipe Fitting"],
    }

    for i, (dept, size) in enumerate(field_depts):
        dn = director_names[i]
        used_names.add(f"{dn[0]}_{dn[1]}")
        vp = vp_map[dept.code]
        director = make_employee(
            dn[0], dn[1], f"Director of {dept.name}", dept, "Director",
            None, "FULL_TIME", random.randint(105000, 125000), "SALARY",
            random_date(date(2013, 1, 1), date(2019, 6, 1)),
            "FEMALE" if dn[2] == "F" else "MALE", vp.id
        )
        field_directors[dept.code] = director

        # Calculate hierarchy: director=1, supts ~3, foremen ~6, rest=workers
        remaining = size - 1
        num_supts = min(3, max(1, remaining // 15))
        num_foremen = min(7, max(2, remaining // 7))
        num_workers = remaining - num_supts - num_foremen

        supts = []
        for s in range(num_supts):
            g = "FEMALE" if random.random() < 0.12 else "MALE"
            fn, ln = pick_name("F" if g == "FEMALE" else "M")
            sup = make_employee(
                fn, ln, "Superintendent", dept, "Superintendent",
                random.choice(dept_trades[dept.code]), "FULL_TIME",
                random.randint(85000, 110000), "SALARY",
                random_date(date(2014, 1, 1), date(2021, 6, 1)),
                g, director.id, random.random() < 0.4
            )
            supts.append(sup)

        foremen = []
        for f in range(num_foremen):
            g = "FEMALE" if random.random() < 0.1 else "MALE"
            fn, ln = pick_name("F" if g == "FEMALE" else "M")
            fm = make_employee(
                fn, ln, "Foreman", dept, "Foreman",
                random.choice(dept_trades[dept.code]), "FULL_TIME",
                random.randint(35, 55), "HOURLY",
                random_date(date(2015, 1, 1), date(2023, 6, 1)),
                g, random.choice(supts).id if supts else director.id,
                random.random() < 0.45
            )
            foremen.append(fm)

        for w in range(num_workers):
            g = "FEMALE" if random.random() < 0.15 else "MALE"
            fn, ln = pick_name("F" if g == "FEMALE" else "M")
            is_apprentice = random.random() < 0.25
            level = "Apprentice" if is_apprentice else "Journeyman"
            emp_type = random.choices(
                ["FULL_TIME", "PART_TIME", "CONTRACTOR"],
                weights=[70, 15, 15]
            )[0]
            make_employee(
                fn, ln,
                f"{'Apprentice' if is_apprentice else ''} {random.choice(dept_trades[dept.code])}".strip(),
                dept, level,
                random.choice(dept_trades[dept.code]), emp_type,
                random.randint(18, 32) if is_apprentice else random.randint(28, 48), "HOURLY",
                random_date(date(2018, 1, 1), date(2026, 1, 15)),
                g, random.choice(foremen).id if foremen else director.id,
                random.random() < 0.4
            )

    session.flush()

    # Set department managers (after employees exist)
    for dept, _ in departments:
        if dept.code in field_directors:
            dept.manager_id = field_directors[dept.code].id
    session.flush()

    print(f"  Created {len(all_employees)} employees")

    # ---- Demo Users ----
    demo_users_data = [
        ("admin@lumber.com", "LumberAdmin2026!", "ADMIN", None),
        ("hr@lumber.com", "LumberHR2026!", "HR_MANAGER", vp_hr.id),
        ("pm@lumber.com", "LumberPM2026!", "PROJECT_MANAGER", None),
        ("foreman@lumber.com", "LumberForeman2026!", "FOREMAN", None),
        ("worker@lumber.com", "LumberWorker2026!", "EMPLOYEE", None),
    ]
    # Find appropriate employees for PM, Foreman, Worker roles
    pm_emp = next((e for e in all_employees if e.job_level == "Superintendent"), None)
    fm_emp = next((e for e in all_employees if e.job_level == "Foreman"), None)
    wk_emp = next((e for e in all_employees if e.job_level == "Journeyman"), None)

    demo_users_data[2] = ("pm@lumber.com", "LumberPM2026!", "PROJECT_MANAGER", pm_emp.id if pm_emp else None)
    demo_users_data[3] = ("foreman@lumber.com", "LumberForeman2026!", "FOREMAN", fm_emp.id if fm_emp else None)
    demo_users_data[4] = ("worker@lumber.com", "LumberWorker2026!", "EMPLOYEE", wk_emp.id if wk_emp else None)

    for email, pwd, role, emp_id in demo_users_data:
        user = User(
            id=uid(), email=email,
            password_hash=pwd_context.hash(pwd),
            role=role, employee_id=emp_id, is_active=True,
        )
        session.add(user)

    # Also create user accounts for key employees (admin, director level)
    for emp in all_employees:
        if emp.job_level in ("C-Suite", "VP", "Director"):
            u = User(
                id=uid(), email=emp.email,
                password_hash=pwd_context.hash("Lumber2026!"),
                role="ADMIN" if emp.job_level == "C-Suite" else "HR_MANAGER",
                employee_id=emp.id, is_active=True,
            )
            session.add(u)

    session.flush()
    print("  Created demo users")

    # ---- Projects ----
    project_data = [
        ("Downtown Office Tower", "DOT-2026", "ACTIVE", 2, date(2025, 3, 1), date(2027, 6, 30)),
        ("I-95 Bridge Rehabilitation", "I95-2025", "ACTIVE", 3, date(2025, 1, 15), date(2026, 12, 31)),
        ("Municipal Water Treatment", "MWT-2026", "ACTIVE", 4, date(2025, 6, 1), date(2027, 3, 31)),
        ("Amazon Distribution Center", "ADC-2026", "ACTIVE", 5, date(2025, 9, 1), date(2027, 1, 31)),
        ("Hospital Wing Addition", "HWA-2026", "ACTIVE", 6, date(2025, 11, 1), date(2026, 11, 30)),
        ("Highway 301 Widening", "H301-2025", "ACTIVE", 7, date(2025, 4, 1), date(2027, 4, 30)),
        ("Solar Farm Electrical", "SFE-2026", "ACTIVE", 8, date(2026, 1, 5), date(2026, 8, 31)),
        ("Residential Complex HVAC", "RCH-2026", "PLANNED", 9 if len(locations) > 9 else 0, date(2026, 3, 1), date(2026, 10, 31)),
    ]

    projects = []
    for name, code, status, loc_idx, start, end in project_data:
        pm_candidates = [e for e in all_employees if e.job_level in ("Superintendent", "Director")]
        pm = random.choice(pm_candidates) if pm_candidates else ceo
        proj = Project(
            id=uid(), name=name, code=code, status=status,
            location_id=locations[min(loc_idx, len(locations)-1)].id,
            start_date=start, end_date=end,
            project_manager_id=pm.id,
        )
        projects.append(proj)
        session.add(proj)

    # Assign workers to projects with crew names
    crew_names_by_trade = {
        "Concrete": ["Alpha Concrete", "Bravo Concrete"],
        "Electrical": ["Spark Team A", "Spark Team B"],
        "HVAC": ["Climate Crew A", "Climate Crew B"],
        "Ironwork": ["Iron Eagles", "Steel Hawks"],
        "Carpentry": ["Frame Squad A", "Frame Squad B"],
        "Welding": ["Torch Team"],
        "Heavy Equipment": ["Earth Movers"],
        "Plumbing": ["Flow Team"],
        "Pipe Fitting": ["Pipe Crew"],
    }

    field_employees = [e for e in all_employees if e.job_level in ("Journeyman", "Apprentice", "Foreman")]
    assigned = set()
    for proj in projects:
        num_workers = random.randint(18, 45)
        available = [e for e in field_employees if e.id not in assigned]
        selected = random.sample(available, min(num_workers, len(available)))
        for emp in selected:
            crew = random.choice(crew_names_by_trade.get(emp.trade, ["General Crew"]))
            pa = ProjectAssignment(
                id=uid(), project_id=proj.id, employee_id=emp.id,
                role=emp.job_level or "Worker", crew_name=crew,
                start_date=proj.start_date,
            )
            session.add(pa)
            assigned.add(emp.id)

    session.flush()
    print(f"  Created {len(projects)} projects with crew assignments")

    # ---- Courses (35) ----
    course_data = [
        # (title, category, format, hours, required, trade, provider)
        ("OSHA 10-Hour Construction", "OSHA Safety", "INSTRUCTOR_LED", 10, True, None, "OSHA Training Institute"),
        ("OSHA 30-Hour Construction", "OSHA Safety", "INSTRUCTOR_LED", 30, True, None, "OSHA Training Institute"),
        ("Fall Protection Training", "OSHA Safety", "INSTRUCTOR_LED", 4, True, None, "Summit Safety Dept"),
        ("Confined Spaces Entry", "OSHA Safety", "INSTRUCTOR_LED", 8, True, None, "Summit Safety Dept"),
        ("Excavation Safety", "OSHA Safety", "INSTRUCTOR_LED", 4, True, None, "Summit Safety Dept"),
        ("Scaffolding Safety", "OSHA Safety", "INSTRUCTOR_LED", 4, True, None, "Summit Safety Dept"),
        ("Hazard Communication (HazCom)", "OSHA Safety", "E_LEARNING", 2, True, None, "SafetySkills Online"),
        ("First Aid / CPR / AED", "Compliance", "INSTRUCTOR_LED", 8, True, None, "American Red Cross"),
        ("Hazmat Awareness", "Compliance", "E_LEARNING", 4, True, None, "SafetySkills Online"),
        ("Silica Awareness", "Compliance", "E_LEARNING", 2, True, None, "Summit Safety Dept"),
        ("Lead Abatement Awareness", "Compliance", "E_LEARNING", 3, False, None, "EPA Training"),
        ("AWS D1.1 Structural Welding", "Trade Certifications", "INSTRUCTOR_LED", 40, True, "Welding", "AWS"),
        ("NCCCO Crane Operator", "Trade Certifications", "INSTRUCTOR_LED", 80, True, "Heavy Equipment", "NCCCO"),
        ("Rigging & Signaling", "Trade Certifications", "INSTRUCTOR_LED", 16, True, None, "NCCCO"),
        ("Forklift Operation", "Equipment Operation", "INSTRUCTOR_LED", 8, True, None, "Summit Training"),
        ("Aerial Lift Certification", "Equipment Operation", "INSTRUCTOR_LED", 4, True, None, "Summit Training"),
        ("Excavator Operation", "Equipment Operation", "INSTRUCTOR_LED", 16, False, "Heavy Equipment", "CAT Training"),
        ("Boom Truck Operation", "Equipment Operation", "INSTRUCTOR_LED", 8, False, "Heavy Equipment", "Summit Training"),
        ("Supervision Skills for Foremen", "Professional Development", "INSTRUCTOR_LED", 16, False, None, "Summit HR"),
        ("Blueprint Reading", "Professional Development", "INSTRUCTOR_LED", 24, False, None, "Summit Training"),
        ("Estimating Basics", "Professional Development", "E_LEARNING", 8, False, None, "ProEst Academy"),
        ("Project Management Fundamentals", "Professional Development", "E_LEARNING", 12, False, None, "LinkedIn Learning"),
        ("Drug & Alcohol Policy", "Company Policies", "E_LEARNING", 1, True, None, "Summit HR"),
        ("Harassment Prevention", "Company Policies", "E_LEARNING", 2, True, None, "Summit HR"),
        ("Code of Conduct", "Company Policies", "E_LEARNING", 1, True, None, "Summit HR"),
        ("Diversity & Inclusion", "Company Policies", "E_LEARNING", 1.5, False, None, "Summit HR"),
        ("Electrical Code (NEC) Updates", "Trade Certifications", "INSTRUCTOR_LED", 8, True, "Electrical", "NFPA"),
        ("HVAC Refrigerant Handling (EPA 608)", "Trade Certifications", "INSTRUCTOR_LED", 8, True, "HVAC", "EPA"),
        ("Plumbing Code Updates", "Trade Certifications", "INSTRUCTOR_LED", 8, True, "Plumbing", "IAPMO"),
        ("Concrete Finishing Techniques", "Trade Certifications", "TOOLBOX_TALK", 2, False, "Concrete", "Summit Training"),
        ("Heavy Equipment Maintenance", "Equipment Operation", "TOOLBOX_TALK", 2, False, "Heavy Equipment", "Summit Training"),
        ("Personal Protective Equipment (PPE)", "OSHA Safety", "TOOLBOX_TALK", 1, True, None, "Summit Safety Dept"),
        ("Fire Prevention & Extinguisher Use", "Compliance", "TOOLBOX_TALK", 1, True, None, "Summit Safety Dept"),
        ("Lockout/Tagout (LOTO)", "Compliance", "INSTRUCTOR_LED", 4, True, None, "Summit Safety Dept"),
        ("Environmental Compliance", "Compliance", "E_LEARNING", 3, False, None, "Summit Safety Dept"),
    ]

    courses = []
    for title, cat, fmt, hours, req, trade, provider in course_data:
        course = Course(
            id=uid(), title=title, description=f"Training course: {title}",
            category=cat, format=fmt, duration_hours=hours,
            is_required=req, trade_specific=trade, provider=provider,
        )
        courses.append(course)
        session.add(course)

    session.flush()
    print(f"  Created {len(courses)} courses")

    # ---- Certifications (450+) ----
    cert_count = 0
    required_courses = [c for c in courses if c.is_required]

    for emp in all_employees:
        # All field workers get OSHA 10
        if emp.job_level in ("Journeyman", "Apprentice", "Foreman", "Superintendent"):
            osha10 = next((c for c in courses if "OSHA 10" in c.title), None)
            if osha10:
                issue = random_date(emp.hire_date, min(emp.hire_date + timedelta(days=90), TODAY))
                exp = issue + timedelta(days=365 * 5)
                status = "VALID"
                if exp < TODAY:
                    status = "EXPIRED"
                elif exp < TODAY + timedelta(days=30):
                    status = "EXPIRING_SOON"
                elif exp < TODAY + timedelta(days=90):
                    status = "EXPIRING_SOON"
                cert = Certification(
                    id=uid(), employee_id=emp.id, name=osha10.title,
                    issuing_body="OSHA Training Institute",
                    cert_number=f"OSHA10-{random.randint(100000, 999999)}",
                    issue_date=issue, expiration_date=exp, status=status,
                    course_id=osha10.id,
                )
                session.add(cert)
                cert_count += 1

        # Supervisors get OSHA 30
        if emp.job_level in ("Foreman", "Superintendent"):
            osha30 = next((c for c in courses if "OSHA 30" in c.title), None)
            if osha30:
                issue = random_date(emp.hire_date, min(emp.hire_date + timedelta(days=180), TODAY))
                exp = issue + timedelta(days=365 * 5)
                status = "VALID" if exp > TODAY + timedelta(days=90) else ("EXPIRING_SOON" if exp > TODAY else "EXPIRED")
                cert = Certification(
                    id=uid(), employee_id=emp.id, name=osha30.title,
                    issuing_body="OSHA Training Institute",
                    cert_number=f"OSHA30-{random.randint(100000, 999999)}",
                    issue_date=issue, expiration_date=exp, status=status,
                    course_id=osha30.id,
                )
                session.add(cert)
                cert_count += 1

        # First Aid/CPR for all
        if emp.job_level in ("Journeyman", "Apprentice", "Foreman", "Superintendent", "Director"):
            fa = next((c for c in courses if "First Aid" in c.title), None)
            if fa and random.random() < 0.8:
                issue = random_date(date(2023, 1, 1), TODAY)
                exp = issue + timedelta(days=365 * 2)
                status = "VALID" if exp > TODAY + timedelta(days=90) else ("EXPIRING_SOON" if exp > TODAY else "EXPIRED")
                cert = Certification(
                    id=uid(), employee_id=emp.id, name=fa.title,
                    issuing_body="American Red Cross",
                    cert_number=f"FA-{random.randint(100000, 999999)}",
                    issue_date=issue, expiration_date=exp, status=status,
                    course_id=fa.id,
                )
                session.add(cert)
                cert_count += 1

        # Trade-specific certs
        if emp.trade:
            trade_courses = [c for c in courses if c.trade_specific == emp.trade]
            for tc in trade_courses:
                if random.random() < 0.7:
                    issue = random_date(date(2021, 1, 1), TODAY)
                    exp = issue + timedelta(days=365 * 3)
                    status = "VALID" if exp > TODAY + timedelta(days=90) else ("EXPIRING_SOON" if exp > TODAY else "EXPIRED")
                    cert = Certification(
                        id=uid(), employee_id=emp.id, name=tc.certification_granted or tc.title,
                        issuing_body=tc.provider or "Summit Training",
                        cert_number=f"TC-{random.randint(100000, 999999)}",
                        issue_date=issue, expiration_date=exp, status=status,
                        course_id=tc.id,
                    )
                    session.add(cert)
                    cert_count += 1

    session.flush()
    print(f"  Created {cert_count} certifications")

    # ---- Training Assignments (600+) ----
    assign_count = 0
    for emp in all_employees:
        # Assign 1-4 training courses
        num = random.randint(1, 4)
        selected_courses = random.sample(courses, min(num, len(courses)))
        for c in selected_courses:
            status = random.choices(
                ["COMPLETED", "IN_PROGRESS", "ASSIGNED", "OVERDUE"],
                weights=[70, 15, 5, 10]
            )[0]
            due = random_date(date(2025, 6, 1), date(2026, 6, 30))
            completed = random_date(due - timedelta(days=30), due) if status == "COMPLETED" else None
            ta = TrainingAssignment(
                id=uid(), employee_id=emp.id, course_id=c.id,
                status=status, due_date=due, completed_date=completed,
                score=round(random.uniform(70, 100), 1) if status == "COMPLETED" else None,
            )
            session.add(ta)
            assign_count += 1

    session.flush()
    print(f"  Created {assign_count} training assignments")

    # ---- Review Cycles ----
    cycle_q4 = ReviewCycle(
        id=uid(), name="Q4 2025 Annual Review", type="Annual",
        period_start=date(2025, 10, 1), period_end=date(2025, 12, 31),
        status="COMPLETED",
    )
    cycle_q2 = ReviewCycle(
        id=uid(), name="Q2 2026 Mid-Year Check-in", type="Mid-Year",
        period_start=date(2026, 4, 1), period_end=date(2026, 6, 30),
        status="IN_PROGRESS",
    )
    session.add(cycle_q4)
    session.add(cycle_q2)
    session.flush()

    # ---- Performance Reviews (~300 for Q4, ~50 in progress for Q2) ----
    review_count = 0
    field_and_staff = [e for e in all_employees if e.job_level not in ("C-Suite",)]
    competencies = [
        ("Safety Compliance", "Core", 0.25),
        ("Quality of Work", "Core", 0.25),
        ("Productivity & Efficiency", "Core", 0.20),
        ("Teamwork & Communication", "Core", 0.15),
        ("Reliability & Attendance", "Core", 0.15),
    ]

    # Q4 2025 completed reviews
    for emp in random.sample(field_and_staff, min(300, len(field_and_staff))):
        reviewer = next(
            (e for e in all_employees if e.id == emp.reports_to_id),
            random.choice([e for e in all_employees if e.job_level in ("Director", "Superintendent", "VP")])
        )
        # Bell curve ratings: 5%=1, 15%=2, 50%=3, 25%=4, 5%=5
        rating_dist = random.choices([1, 2, 3, 4, 5], weights=[5, 15, 50, 25, 5])[0]
        review = PerformanceReview(
            id=uid(), employee_id=emp.id, reviewer_id=reviewer.id,
            review_cycle_id=cycle_q4.id, type="ANNUAL",
            status="COMPLETED",
            period_start=date(2025, 10, 1), period_end=date(2025, 12, 31),
            due_date=date(2026, 1, 15),
            overall_rating=float(rating_dist),
            manager_comments=f"Reviewed for Q4 2025. Performance level: {'Exceptional' if rating_dist == 5 else 'Exceeds' if rating_dist == 4 else 'Meets' if rating_dist == 3 else 'Needs Improvement' if rating_dist == 2 else 'Unsatisfactory'}.",
            completed_at=datetime(2026, 1, random.randint(5, 20)),
        )
        session.add(review)
        session.flush()
        # Add criteria
        for cname, ccat, cweight in competencies:
            rc = ReviewCriteria(
                id=uid(), review_id=review.id, name=cname, category=ccat,
                weight=cweight,
                rating=max(1, min(5, rating_dist + random.randint(-1, 1))),
                comments=None,
            )
            session.add(rc)
        review_count += 1

    # Q2 2026 in-progress reviews
    for emp in random.sample(field_and_staff, min(50, len(field_and_staff))):
        reviewer = next(
            (e for e in all_employees if e.id == emp.reports_to_id),
            random.choice([e for e in all_employees if e.job_level in ("Director", "Superintendent")])
        )
        status = random.choice(["DRAFT", "SELF_REVIEW", "MANAGER_REVIEW", "PENDING_SIGN_OFF"])
        review = PerformanceReview(
            id=uid(), employee_id=emp.id, reviewer_id=reviewer.id,
            review_cycle_id=cycle_q2.id, type="MID_YEAR",
            status=status,
            period_start=date(2026, 4, 1), period_end=date(2026, 6, 30),
            due_date=date(2026, 7, 15),
        )
        session.add(review)
        session.flush()
        for cname, ccat, cweight in competencies:
            rc = ReviewCriteria(
                id=uid(), review_id=review.id, name=cname, category=ccat,
                weight=cweight,
            )
            session.add(rc)
        review_count += 1

    session.flush()
    print(f"  Created {review_count} performance reviews")

    # ---- Goals (45) ----
    goal_count = 0
    goal_employees = random.sample(field_and_staff, min(30, len(field_and_staff)))
    for emp in goal_employees:
        num_goals = random.randint(1, 3)
        for _ in range(num_goals):
            cat = random.choice(["SAFETY", "QUALITY", "PRODUCTIVITY", "DEVELOPMENT", "LEADERSHIP"])
            status = random.choice(["NOT_STARTED", "IN_PROGRESS", "IN_PROGRESS", "AT_RISK", "COMPLETED"])
            goal = Goal(
                id=uid(), employee_id=emp.id,
                title=f"{cat.title()} Goal - {emp.first_name}",
                description=f"Improvement target in {cat.lower()} area.",
                category=cat,
                target_date=random_date(date(2026, 3, 1), date(2026, 12, 31)),
                weight=round(random.uniform(0.5, 2.0), 1),
                percent_complete=random.randint(0, 100) if status != "NOT_STARTED" else 0,
                status=status,
            )
            session.add(goal)
            goal_count += 1

    session.flush()
    print(f"  Created {goal_count} goals")

    # ---- Incidents (12) ----
    incident_types = [
        ("SAFETY", "MAJOR", "Worker fell from scaffolding due to missing harness clip."),
        ("SAFETY", "MODERATE", "Near-miss incident with overhead crane load."),
        ("SAFETY", "MINOR", "Employee observed without hard hat in active zone."),
        ("ATTENDANCE", "MODERATE", "Three consecutive no-call no-shows."),
        ("ATTENDANCE", "MINOR", "Late arrival (>30 min) four times in two weeks."),
        ("ATTENDANCE", "MINOR", "Left jobsite early without supervisor approval."),
        ("ATTENDANCE", "MODERATE", "Failed to report for scheduled overtime shift."),
        ("QUALITY", "MAJOR", "Concrete pour failed inspection — incorrect mix ratio."),
        ("QUALITY", "MODERATE", "Weld rejected on structural beam — undercut detected."),
        ("QUALITY", "MINOR", "Electrical conduit run deviated from blueprint by 6 inches."),
        ("CONDUCT", "MODERATE", "Verbal altercation with coworker on site."),
        ("CONDUCT", "MINOR", "Unauthorized use of company vehicle for personal errands."),
    ]
    for itype, sev, desc in incident_types:
        emp = random.choice(field_employees)
        reporter = random.choice([e for e in all_employees if e.job_level in ("Foreman", "Superintendent", "Director")])
        status = random.choice(["OPEN", "INVESTIGATING", "RESOLVED", "CLOSED"])
        inc = Incident(
            id=uid(), employee_id=emp.id, reported_by_id=reporter.id,
            type=itype, severity=sev, description=desc,
            incident_date=random_date(date(2025, 10, 1), TODAY),
            location=random.choice(["Downtown Office Tower Site", "I-95 Bridge Site", "Highway 301 Site"]),
            status=status,
            resolution="Investigated and resolved." if status in ("RESOLVED", "CLOSED") else None,
        )
        session.add(inc)

    # ---- Commendations (25) ----
    comm_data = [
        ("SAFETY", 5, "Identified and reported critical scaffolding deficiency before crew arrival."),
        ("SAFETY", 4, "Completed 365 days without a safety incident."),
        ("SAFETY", 4, "Led toolbox talk that prevented a confined space hazard."),
        ("SAFETY", 5, "Quick response during medical emergency — administered CPR."),
        ("SAFETY", 3, "Consistently wears and promotes proper PPE usage."),
        ("SAFETY", 4, "Reported near-miss that led to improved fall protection protocol."),
        ("SAFETY", 5, "Evacuated crew from unstable excavation ahead of collapse."),
        ("SAFETY", 4, "Zero safety incidents for entire crew in Q4 2025."),
        ("QUALITY", 5, "Welding passed all inspections — zero rejects for entire project."),
        ("QUALITY", 4, "Concrete finish quality rated excellent by architect."),
        ("QUALITY", 4, "Blueprint interpretation prevented costly rework."),
        ("QUALITY", 5, "Electrical work completed ahead of schedule with zero defects."),
        ("QUALITY", 3, "Consistently maintains clean and organized work area."),
        ("QUALITY", 4, "Identified material defect in steel delivery before installation."),
        ("QUALITY", 5, "HVAC system commissioning achieved 100% first-pass rate."),
        ("TEAMWORK", 4, "Mentored three apprentices through first month on site."),
        ("TEAMWORK", 5, "Coordinated three trades to resolve scheduling conflict."),
        ("TEAMWORK", 4, "Volunteered for night shift to help meet project deadline."),
        ("TEAMWORK", 3, "Helped new hires integrate into crew quickly."),
        ("TEAMWORK", 4, "Translated safety briefings into Spanish for crew members."),
        ("TEAMWORK", 5, "Led cross-department collaboration on complex structural pour."),
        ("ABOVE_AND_BEYOND", 5, "Worked 14 consecutive weekends to meet critical milestone."),
        ("ABOVE_AND_BEYOND", 4, "Developed training materials for new crane signaling protocol."),
        ("ABOVE_AND_BEYOND", 5, "Saved $50K by suggesting alternative material sourcing."),
        ("ABOVE_AND_BEYOND", 4, "Organized crew appreciation event, improving morale metrics."),
    ]
    for cat, stars, desc in comm_data:
        emp = random.choice(field_employees)
        awarder = random.choice([e for e in all_employees if e.job_level in ("Foreman", "Superintendent", "Director", "VP")])
        comm = Commendation(
            id=uid(), employee_id=emp.id, awarded_by_id=awarder.id,
            category=cat, stars=stars, description=desc, is_public=True,
        )
        session.add(comm)

    # ---- PIPs (3) ----
    pip_employees = random.sample(field_employees, 3)
    for emp in pip_employees:
        pip = PIP(
            id=uid(), employee_id=emp.id,
            issue_description=random.choice([
                "Repeated safety violations including failure to wear required PPE.",
                "Consistent tardiness and unauthorized absences affecting crew productivity.",
                "Quality of work below standards — multiple rework instances in last quarter.",
            ]),
            improvement_targets_json='["Meet attendance policy", "Complete safety retraining", "Weekly check-ins with supervisor"]',
            start_date=random_date(date(2026, 1, 1), date(2026, 2, 1)),
            end_date=random_date(date(2026, 4, 1), date(2026, 5, 31)),
            status="ACTIVE",
        )
        session.add(pip)
        session.flush()
        # Add milestones
        for j, (title, dd) in enumerate([
            ("Initial meeting and plan acknowledgment", pip.start_date + timedelta(days=7)),
            ("First progress check-in", pip.start_date + timedelta(days=30)),
            ("Mid-point review", pip.start_date + timedelta(days=45)),
            ("Final evaluation", pip.end_date),
        ]):
            ms = PIPMilestone(
                id=uid(), pip_id=pip.id, title=title,
                due_date=dd,
                status="COMPLETED" if j == 0 else "PENDING",
                completed_date=dd if j == 0 else None,
            )
            session.add(ms)

    # ---- Training Rules (5) ----
    rules = [
        ("New Hire Safety Orientation", "NEW_HIRE", '{"departments": "all"}',
         str([c.id for c in courses if c.title in ("OSHA 10-Hour Construction", "Drug & Alcohol Policy", "Code of Conduct", "Harassment Prevention")])),
        ("OSHA 10 Renewal", "CERT_EXPIRING", '{"cert_name": "OSHA 10-Hour Construction", "days_before": 90}',
         str([c.id for c in courses if "OSHA 10" in c.title])),
        ("First Aid Renewal", "CERT_EXPIRING", '{"cert_name": "First Aid / CPR / AED", "days_before": 60}',
         str([c.id for c in courses if "First Aid" in c.title])),
        ("Safety Retraining on Low Score", "LOW_REVIEW_SCORE", '{"threshold": 2, "competency": "Safety Compliance"}',
         str([c.id for c in courses if c.category == "OSHA Safety"][:3])),
        ("New Hire Company Policies", "NEW_HIRE", '{"departments": "all"}',
         str([c.id for c in courses if c.category == "Company Policies"])),
    ]
    for name, trigger, config, course_ids in rules:
        tr = TrainingRule(
            id=uid(), name=name, trigger_type=trigger,
            trigger_config_json=config, action_course_ids_json=course_ids,
            is_active=True,
        )
        session.add(tr)

    session.commit()
    print(f"\n✅ Seed complete! Total employees: {len(all_employees)}")
    print(f"   Projects: {len(projects)}, Courses: {len(courses)}")
    print(f"   Certifications: {cert_count}, Training Assignments: {assign_count}")
    print(f"   Reviews: {review_count}, Goals: {goal_count}")
    print(f"   Incidents: 12, Commendations: 25, PIPs: 3")


# ============================================================
# CLI entry point
# ============================================================
if __name__ == "__main__":
    import sys
    sys.path.insert(0, "/home/node/.openclaw/workspace/lumber-hris")
    from backend.models.database import SessionLocal, create_tables
    print("Creating tables...")
    create_tables()
    print("Seeding database...")
    db = SessionLocal()
    try:
        seed_database(db)
    except Exception as e:
        db.rollback()
        print(f"❌ Seed failed: {e}")
        raise
    finally:
        db.close()
