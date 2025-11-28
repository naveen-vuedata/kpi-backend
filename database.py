"""
Full SQLAlchemy ORM script including:
- Companies
- CompanyRevenue
- Clients
- ProjectCategory
- Projects
- ProjectDetails
- Employees
- TeamMembers
- ProjectGoals
- KPI Catalog (new)
- Milestone, Defect, Issue, TimeEntry, ProjectCost, EmployeeExit, HiringPipeline, TrainingAttendance

Generates full sample data + KPI catalog entries.

Run:
    python database_setup.py
"""

from sqlalchemy import (
    create_engine, Column, Integer, String, Date, DateTime, Text, DECIMAL,
    ForeignKey, Float, text
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime, timedelta, date
from faker import Faker
import random

Base = declarative_base()
fake = Faker()

# ---------------------------------------------------------
# ORM MODELS
# ---------------------------------------------------------

class Company(Base):
    __tablename__ = "companies"

    company_id = Column(Integer, primary_key=True, autoincrement=True)
    company_name = Column(String(200), nullable=False)
    industry = Column(String(100))
    hq_location = Column(String(100))
    website = Column(String(250))
    created_at = Column(DateTime, default=datetime.utcnow)

    revenues = relationship("CompanyRevenue", back_populates="company")
    clients = relationship("Client", back_populates="company")
    employees = relationship("Employee", back_populates="company")
    projects = relationship("Project", back_populates="company")


class CompanyRevenue(Base):
    __tablename__ = "company_revenue"
    revenue_id = Column(Integer, primary_key=True, autoincrement=True)

    company_id = Column(Integer, ForeignKey("companies.company_id"), nullable=False)
    revenue_amount = Column(DECIMAL(14,2), nullable=False)
    revenue_date = Column(Date, nullable=False)

    company = relationship("Company", back_populates="revenues")


class Client(Base):
    __tablename__ = "clients"

    client_id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey("companies.company_id"), nullable=False)
    name = Column(String(200), nullable=False)
    industry = Column(String(100))
    country = Column(String(100))
    contact_email = Column(String(200))

    company = relationship("Company", back_populates="clients")
    projects = relationship("Project", back_populates="client")


class ProjectCategory(Base):
    __tablename__ = "project_categories"

    category_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)

    projects = relationship("Project", back_populates="category")


class Project(Base):
    __tablename__ = "projects"

    project_id = Column(Integer, primary_key=True, autoincrement=True)
    project_code = Column(String(50), unique=True)
    name = Column(String(200))
    client_id = Column(Integer, ForeignKey("clients.client_id"))
    company_id = Column(Integer, ForeignKey("companies.company_id"))
    category_id = Column(Integer, ForeignKey("project_categories.category_id"))

    start_date = Column(Date)
    planned_end_date = Column(Date)
    actual_end_date = Column(Date)
    status = Column(String(50))
    budget = Column(DECIMAL(14,2))

    client = relationship("Client", back_populates="projects")
    company = relationship("Company", back_populates="projects")
    category = relationship("ProjectCategory", back_populates="projects")
    details = relationship("ProjectDetail", back_populates="project", uselist=False)
    goals = relationship("ProjectGoal", back_populates="project")
    team_members = relationship("TeamMember", back_populates="project")

    # NEW relationships for added tables
    milestones = relationship("Milestone", back_populates="project")
    defects = relationship("Defect", back_populates="project")
    issues = relationship("Issue", back_populates="project")
    time_entries = relationship("TimeEntry", back_populates="project")
    project_costs = relationship("ProjectCost", back_populates="project")


class ProjectDetail(Base):
    __tablename__ = "project_details"

    detail_id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.project_id"))
    technology_stack = Column(String(200))
    methodology = Column(String(100))

    project = relationship("Project", back_populates="details")


class Employee(Base):
    __tablename__ = "employees"

    employee_id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey("companies.company_id"))
    first_name = Column(String(150))
    last_name = Column(String(150))
    role = Column(String(100))
    department = Column(String(100))

    company = relationship("Company", back_populates="employees")
    team_memberships = relationship("TeamMember", back_populates="employee")

    # NEW relationships
    time_entries = relationship("TimeEntry", back_populates="employee")
    exit_records = relationship("EmployeeExit", back_populates="employee")
    training_records = relationship("TrainingAttendance", back_populates="employee")


class TeamMember(Base):
    __tablename__ = "team_members"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.project_id"))
    employee_id = Column(Integer, ForeignKey("employees.employee_id"))
    role_in_project = Column(String(100))
    allocation_percentage = Column(Integer)

    project = relationship("Project", back_populates="team_members")
    employee = relationship("Employee", back_populates="team_memberships")


class ProjectGoal(Base):
    __tablename__ = "project_goals"

    goal_id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.project_id"))
    title = Column(String(250))
    description = Column(Text)
    status = Column(String(50))

    project = relationship("Project", back_populates="goals")


# ---------------------------------------------------------
# NEW: KPI Catalog Table
# ---------------------------------------------------------

class KPICatalog(Base):
    __tablename__ = "kpi_catalog"

    kpi_id = Column(Integer, primary_key=True, autoincrement=True)
    role = Column(String(300), nullable=False)
    kpi_name = Column(String(200), nullable=False)
    category = Column(String(100), nullable=False)
    description = Column(Text)
    sql_formula = Column(Text, nullable=False)
    data_sources = Column(String(300))
    calculation_type = Column(String(50))
    unit = Column(String(20))
    target_value = Column(DECIMAL(14,2))
    created_at = Column(DateTime, default=datetime.utcnow)


# =====================================================================
# 10. MILESTONE
# =====================================================================

class Milestone(Base):
    __tablename__ = "milestones"

    milestone_id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.project_id"), nullable=False)

    name = Column(String(255), nullable=False)
    planned_date = Column(Date, nullable=False)
    actual_date = Column(Date)
    status = Column(String(50))

    project = relationship("Project", back_populates="milestones")


# =====================================================================
# 11. DEFECT
# =====================================================================

class Defect(Base):
    __tablename__ = "defects"

    defect_id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.project_id"), nullable=False)

    severity = Column(String(50))
    reported_date = Column(Date)
    reported_by = Column(String(255))
    environment = Column(String(50))  # QA, UAT, PROD
    status = Column(String(50))
    closed_date = Column(Date)

    project = relationship("Project", back_populates="defects")


# =====================================================================
# 12. ISSUE
# =====================================================================

class Issue(Base):
    __tablename__ = "issues"

    issue_id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.project_id"), nullable=False)

    issue_type = Column(String(100))
    priority = Column(String(50))
    reported_date = Column(Date)
    resolved_date = Column(Date)
    reported_by_client = Column(String(255))
    status = Column(String(50))

    project = relationship("Project", back_populates="issues")


# =====================================================================
# 13. TIME ENTRY (UTILIZATION / BILLABLE HOURS)
# =====================================================================

class TimeEntry(Base):
    __tablename__ = "time_entry"

    time_entry_id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.project_id"), nullable=False)
    employee_id = Column(Integer, ForeignKey("employees.employee_id"), nullable=False)

    date = Column(Date, nullable=False)
    hours = Column(Float, nullable=False)
    is_billable = Column(Integer)  # 1 = billable, 0 = non-billable

    project = relationship("Project", back_populates="time_entries")
    employee = relationship("Employee", back_populates="time_entries")


# =====================================================================
# 14. PROJECT COST (BUDGET VARIANCE)
# =====================================================================

class ProjectCost(Base):
    __tablename__ = "project_cost"

    cost_id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.project_id"), nullable=False)

    cost_type = Column(String(255))  # labor, infra, misc
    planned_cost = Column(Float)
    actual_cost = Column(Float)
    recorded_date = Column(Date)

    project = relationship("Project", back_populates="project_costs")


# =====================================================================
# 15. EMPLOYEE EXIT (ATTRITION RATE)
# =====================================================================

class EmployeeExit(Base):
    __tablename__ = "employee_exit"

    exit_id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey("employees.employee_id"), nullable=False)

    exit_date = Column(Date)
    reason = Column(String(255))
    is_regretted = Column(Integer)

    employee = relationship("Employee", back_populates="exit_records")


# =====================================================================
# 16. HIRING PIPELINE (TIME-TO-HIRE)
# =====================================================================

class HiringPipeline(Base):
    __tablename__ = "hiring_pipeline"

    hiring_id = Column(Integer, primary_key=True, autoincrement=True)
    position = Column(String(255), nullable=False)
    department = Column(String(255))
    opened_date = Column(Date)
    closed_date = Column(Date)
    applicant_name = Column(String(255))
    offer_made_date = Column(Date)
    offer_accepted_date = Column(Date)

    status = Column(String(50))  # open, closed, hired


# =====================================================================
# 17. TRAINING ATTENDANCE (TRAINING COMPLETION)
# =====================================================================

class TrainingAttendance(Base):
    __tablename__ = "training_attendance"

    training_id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey("employees.employee_id"))
    course_name = Column(String(255))
    assigned_date = Column(Date)
    completed_date = Column(Date)

    employee = relationship("Employee", back_populates="training_records")


# ---------------------------------------------------------
# DB SETUP
# ---------------------------------------------------------

DB_USER = "root"
DB_PASS = "monisha"
DB_HOST = "localhost"
DB_NAME = "kpi_platform"

# 1) Connect to MySQL server WITHOUT database to ensure DB exists
server_engine = create_engine(
    f"mysql+mysqlconnector://{DB_USER}:{DB_PASS}@{DB_HOST}",
    echo=False,
    isolation_level="AUTOCOMMIT",
)


def ensure_database():
    with server_engine.connect() as conn:
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}"))
        print(f"Ensured database '{DB_NAME}' exists.")


# 2) Now create engine pointing to the specific database
ensure_database()

engine = create_engine(
    f"mysql+mysqlconnector://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}",
    echo=False
)

Session = sessionmaker(bind=engine)


def recreate_schema():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    print("Database Schema Created Successfully")


# ---------------------------------------------------------
# SAMPLE DATA GENERATION
# ---------------------------------------------------------

def generate_sample_data(
    session,
    num_companies=50,
    num_clients_per_company=100,
    num_projects=100,
    num_employees=1500,
    num_revenue_months=1000,
    num_time_entries=1000
):
    # ----- Companies -----
    companies = []
    for _ in range(num_companies):
        c = Company(
            company_name=fake.company(),
            industry=fake.bs(),
            hq_location=fake.city(),
            website=fake.url()
        )
        companies.append(c)
    session.add_all(companies)
    session.commit()

    # ----- Company Revenue -----
    for c in companies:
        for m in range(num_revenue_months):
            session.add(
                CompanyRevenue(
                    company_id=c.company_id,
                    revenue_amount=random.randint(50000, 400000),
                    revenue_date=date.today() - timedelta(days=m * 30)
                )
            )
    session.commit()

    # ----- Clients -----
    clients = []
    for c in companies:
        for _ in range(num_clients_per_company):
            cl = Client(
                company_id=c.company_id,
                name=fake.company(),
                industry=random.choice(["Retail", "Finance", "Healthcare"]),
                country=fake.country(),
                contact_email=fake.email()
            )
            clients.append(cl)
    session.add_all(clients)
    session.commit()

    # ----- Project Categories -----
    category_list = ["Web", "Mobile", "AI/ML", "Cloud"]
    categories = []
    for ct in category_list:
        categories.append(ProjectCategory(name=ct, description=f"{ct} projects"))
    session.add_all(categories)
    session.commit()

    # ----- Projects -----
    projects = []
    for i in range(num_projects):
        cli = random.choice(clients)
        cat = random.choice(categories)
        comp = random.choice(companies)
        start = date.today() - timedelta(days=random.randint(30, 500))
        planned_end = start + timedelta(days=random.randint(50, 150))

        p = Project(
            project_code=f"PRJ{i+1000}",
            name=f"Project_{i}",
            client_id=cli.client_id,
            company_id=comp.company_id,
            category_id=cat.category_id,
            start_date=start,
            planned_end_date=planned_end,
            actual_end_date=planned_end + timedelta(days=random.randint(-10, 40)),
            status=random.choice(["Completed", "In Progress"]),
            budget=random.randint(50000, 500000)
        )
        projects.append(p)
    session.add_all(projects)
    session.commit()

    # ----- Project Details -----
    for p in projects:
        session.add(ProjectDetail(
            project_id=p.project_id,
            technology_stack=random.choice(["Python", "Node", "Java", "Go"]),
            methodology=random.choice(["Agile", "Scrum", "Waterfall"])
        ))
    session.commit()

    # ----- Employees -----
    employees = []
    for _ in range(num_employees):
        comp = random.choice(companies)
        emp = Employee(
            company_id=comp.company_id,
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            role=random.choice(["Developer", "QA", "Manager"]),
            department=random.choice(["IT", "HR", "Finance"])
        )
        employees.append(emp)
    session.add_all(employees)
    session.commit()

    # ----- Team Members -----
    for p in projects:
        sample_team = random.sample(employees, min(5, len(employees)))
        for emp in sample_team:
            session.add(TeamMember(
                project_id=p.project_id,
                employee_id=emp.employee_id,
                role_in_project=random.choice(["Dev", "Lead", "QA"]),
                allocation_percentage=random.randint(20, 100)
            ))
    session.commit()

    # ----- Project Goals -----
    for p in projects:
        for _ in range(random.randint(2, 5)):
            session.add(ProjectGoal(
                project_id=p.project_id,
                title=fake.bs(),
                description=fake.sentence(),
                status=random.choice(["Pending", "Completed"])
            ))
    session.commit()

    # ----- Milestones -----
    for p in projects:
        for m_idx in range(2):
            planned = p.start_date + timedelta(days=20 * (m_idx + 1))
            actual_offset = random.randint(-5, 10)
            session.add(Milestone(
                project_id=p.project_id,
                name=f"{p.name} - Milestone {m_idx+1}",
                planned_date=planned,
                actual_date=planned + timedelta(days=actual_offset),
                status=random.choice(["Pending", "Completed", "Delayed"])
            ))
    session.commit()

    # ----- Defects -----
    for p in projects:
        for _ in range(random.randint(0, 3)):
            session.add(Defect(
                project_id=p.project_id,
                severity=random.choice(["Low", "Medium", "High", "Critical"]),
                reported_date=p.start_date + timedelta(days=random.randint(1, 40)),
                reported_by=fake.name(),
                environment=random.choice(["QA", "UAT", "PROD"]),
                status=random.choice(["Open", "In Progress", "Closed"]),
                closed_date=date.today() if random.random() > 0.5 else None
            ))
    session.commit()

    # ----- Issues -----
    for p in projects:
        for _ in range(random.randint(0, 2)):
            session.add(Issue(
                project_id=p.project_id,
                issue_type=random.choice(["Blocker", "Task", "Bug", "Query"]),
                priority=random.choice(["Low", "Medium", "High"]),
                reported_date=p.start_date + timedelta(days=random.randint(1, 40)),
                resolved_date=p.start_date + timedelta(days=random.randint(20, 80)) if random.random() > 0.4 else None,
                reported_by_client=fake.company(),
                status=random.choice(["Open", "Resolved", "Monitoring"])
            ))
    session.commit()

    # ----- Time Entries -----
    for i in range(num_time_entries):
        proj = projects[i % len(projects)]
        emp = employees[i % len(employees)]

        session.add(TimeEntry(
            project_id=proj.project_id,
            employee_id=emp.employee_id,
            date=proj.start_date + timedelta(days=random.randint(0, 90)),
            hours=round(random.uniform(1.0, 8.0), 2),
            is_billable=1 if random.random() > 0.2 else 0
        ))

        if i % 500 == 0 and i > 0:
            session.commit()
    session.commit()

    # ----- Project Cost -----
    for p in projects:
        for _ in range(random.randint(1, 3)):
            session.add(ProjectCost(
                project_id=p.project_id,
                cost_type=random.choice(["labor", "infra", "misc"]),
                planned_cost=round(random.uniform(1000, 50000), 2),
                actual_cost=round(random.uniform(500, 60000), 2),
                recorded_date=p.start_date + timedelta(days=random.randint(0, 120))
            ))
    session.commit()

    # ----- Employee Exits -----
    exit_count = max(1, int(num_employees * 0.05))
    exit_sample = random.sample(employees, exit_count)

    for emp in exit_sample:
        session.add(EmployeeExit(
            employee_id=emp.employee_id,
            exit_date=date.today() - timedelta(days=random.randint(1, 400)),
            reason=random.choice(["Personal", "Better Offer", "Resignation", "Termination"]),
            is_regretted=1 if random.random() > 0.6 else 0
        ))
    session.commit()

    # ----- Hiring Pipeline -----
    for _ in range(12):
        session.add(HiringPipeline(
            position=random.choice(["Software Engineer", "QA Engineer", "Project Manager", "Data Analyst"]),
            department=random.choice(["IT", "HR", "Finance", "Product"]),
            opened_date=date.today() - timedelta(days=random.randint(1, 200)),
            closed_date=date.today() - timedelta(days=random.randint(0, 100)) if random.random() > 0.5 else None,
            applicant_name=fake.name(),
            offer_made_date=date.today() - timedelta(days=random.randint(0, 60)) if random.random() > 0.6 else None,
            offer_accepted_date=date.today() - timedelta(days=random.randint(0, 30)) if random.random() > 0.7 else None,
            status=random.choice(["open", "closed", "hired"])
        ))
    session.commit()

    # ----- Training Attendance -----
    for idx, emp in enumerate(employees):
        if idx % 3 == 0:  # ~30%
            session.add(TrainingAttendance(
                employee_id=emp.employee_id,
                course_name=random.choice(["AWS Basics", "Python Advanced", "Agile Foundations", "Security Awareness"]),
                assigned_date=date.today() - timedelta(days=random.randint(10, 300)),
                completed_date=date.today() - timedelta(days=random.randint(1, 50)) if random.random() > 0.4 else None
            ))
    session.commit()


# ---------------------------------------------------------
# KPI CATALOG INSERTS
# ---------------------------------------------------------

def insert_kpi_catalog(session):
# role=random.choice - "Project Manager", "Delivery Manager", "HR Manager",
    kpis = [
        # Company-Level KPIs
        ("Total Revenue", "Company",
         "Total revenue for a given year",
         "SELECT SUM(revenue_amount) FROM company_revenue WHERE YEAR(revenue_date) = :year",
         "company_revenue", "sum", "USD", None, "HR Manager"),

        ("Revenue Growth Rate", "Company",
         "Year over year revenue growth",
         """
         SELECT 
           ((this_year.total - last_year.total) / last_year.total) * 100 
         FROM
           (SELECT SUM(revenue_amount) total FROM company_revenue WHERE YEAR(revenue_date)=:year) this_year,
           (SELECT SUM(revenue_amount) total FROM company_revenue WHERE YEAR(revenue_date)=:year-1) last_year
         """,
         "company_revenue", "percentage", "%", None, "HR Manager"),

        ("Revenue per Client", "Company",
         "Revenue divided by total active clients",
         """
         SELECT SUM(r.revenue_amount) / COUNT(DISTINCT c.client_id)
         FROM company_revenue r 
         JOIN clients c ON c.company_id = r.company_id
         """,
         "company_revenue, clients", "ratio", "USD", None, "HR Manager"),

        # Project KPIs
        ("On-time Delivery Rate", "Project",
         "Percentage of projects delivered on time",
         """
         SELECT 
           (SUM(CASE WHEN actual_end_date <= planned_end_date THEN 1 ELSE 0 END) 
            / COUNT(*)) * 100 
         FROM projects
         """,
         "projects", "percentage", "%", 95, "Project Manager"),

        ("Goal Completion Rate", "Project",
         "Percentage of goals completed",
         """
         SELECT 
           (SUM(CASE WHEN status='Completed' THEN 1 END) / COUNT(*)) * 100 
         FROM project_goals
         """,
         "project_goals", "percentage", "%", None, "Project Manager"),

        # New KPIs for the added tables
        ("Average Time per Project (hrs)", "Project",
         "Average billable hours per project over period",
         """
         SELECT AVG(hours) FROM time_entry WHERE project_id = :project_id AND is_billable = 1
         """,
         "time_entry", "average", "hours", None, "Delivery Manager"),

        ("Defects per Project", "Project",
         "Average number of defects reported per project",
         """
         SELECT project_id, COUNT(*) AS defect_count FROM defects GROUP BY project_id
         """,
         "defects", "count", "count", None, "Delivery Manager"),
    ]

    for k in kpis:
        session.add(
            KPICatalog(
                kpi_name=k[0],
                category=k[1],
                description=k[2],
                sql_formula=k[3],
                data_sources=k[4],
                calculation_type=k[5],
                unit=k[6],
                target_value=k[7],
                role=k[8]
            )
        )
    session.commit()
    print("Inserted KPI Catalog entries.")


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

def main():
    recreate_schema()
    session = Session()

    generate_sample_data(session)
    insert_kpi_catalog(session)

    session.close()
    print("All data generation completed successfully!")


if __name__ == "__main__":
    main()
