// ============================================
// Lumber HRIS — TypeScript Type Definitions
// ============================================

// Enums
export type Role = 'ADMIN' | 'HR_MANAGER' | 'PROJECT_MANAGER' | 'FOREMAN' | 'EMPLOYEE'
export type EmployeeType = 'FULL_TIME' | 'PART_TIME' | 'CONTRACTOR' | 'CASUAL'
export type EmployeeStatus = 'ACTIVE' | 'ON_LEAVE' | 'SUSPENDED' | 'TERMINATED'
export type Gender = 'MALE' | 'FEMALE' | 'OTHER' | 'PREFER_NOT_TO_SAY'
export type PayType = 'HOURLY' | 'SALARY'
export type ProjectStatus = 'ACTIVE' | 'COMPLETED' | 'PLANNED'
export type ReviewType = 'ANNUAL' | 'MID_YEAR' | 'THIRTY_SIXTY_NINETY' | 'PROJECT_CLOSEOUT' | 'PIP'
export type ReviewStatus = 'DRAFT' | 'SELF_REVIEW' | 'MANAGER_REVIEW' | 'PENDING_SIGN_OFF' | 'COMPLETED' | 'CANCELLED'
export type GoalCategory = 'SAFETY' | 'QUALITY' | 'PRODUCTIVITY' | 'DEVELOPMENT' | 'LEADERSHIP'
export type GoalStatus = 'NOT_STARTED' | 'IN_PROGRESS' | 'AT_RISK' | 'COMPLETED' | 'DEFERRED'
export type IncidentType = 'SAFETY' | 'ATTENDANCE' | 'QUALITY' | 'CONDUCT'
export type Severity = 'MINOR' | 'MODERATE' | 'MAJOR' | 'CRITICAL'
export type IncidentStatus = 'OPEN' | 'INVESTIGATING' | 'RESOLVED' | 'CLOSED'
export type CommendationCategory = 'SAFETY' | 'QUALITY' | 'TEAMWORK' | 'ABOVE_AND_BEYOND'
export type CourseFormat = 'E_LEARNING' | 'INSTRUCTOR_LED' | 'TOOLBOX_TALK'
export type TrainingStatus = 'ASSIGNED' | 'IN_PROGRESS' | 'COMPLETED' | 'OVERDUE'
export type CertStatus = 'VALID' | 'EXPIRING_SOON' | 'EXPIRED' | 'REVOKED'
export type PIPStatus = 'ACTIVE' | 'COMPLETED' | 'EXTENDED' | 'FAILED'

// Auth
export interface User {
  id: string
  email: string
  role: Role
  employee_id: string | null
  is_active: boolean
}

export interface LoginRequest {
  email: string
  password: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
  user: User
}

// Employee
export interface EmployeeBrief {
  id: string
  employee_number: string
  first_name: string
  last_name: string
  job_title: string
  department_name: string
  photo_url: string | null
}

export interface Employee {
  id: string
  employee_number: string
  first_name: string
  last_name: string
  email: string
  phone: string | null
  address: string | null
  city: string | null
  state: string | null
  zip: string | null
  date_of_birth: string | null
  gender: Gender | null
  ethnicity: string | null
  veteran_status: boolean
  photo_url: string | null
  employee_type: EmployeeType
  status: EmployeeStatus
  hire_date: string
  original_hire_date: string | null
  termination_date: string | null
  job_title: string
  job_level: string | null
  trade: string | null
  pay_rate: number
  pay_type: PayType
  department_id: string
  department_name: string
  division_name: string
  location_name: string | null
  reports_to_id: string | null
  reports_to_name: string | null
  union_name: string | null
  union_local: string | null
  cost_center: string | null
  bonus_eligible: boolean
  notes: string | null
  created_at: string
  updated_at: string
}

export interface EmployeeListResponse {
  items: Employee[]
  total: number
  page: number
  per_page: number
}

// Department / Division / Location
export interface Department {
  id: string
  name: string
  code: string
  division_id: string
  cost_center: string | null
  manager_id: string | null
}

export interface Division {
  id: string
  name: string
  code: string
}

export interface Location {
  id: string
  name: string
  address: string
  city: string
  state: string
  type: 'OFFICE' | 'FIELD' | 'WAREHOUSE'
}

// Project
export interface Project {
  id: string
  name: string
  code: string
  status: ProjectStatus
  start_date: string
  end_date: string | null
  project_manager: EmployeeBrief
}

// Performance
export interface ReviewCriteria {
  id: string
  name: string
  category: string
  weight: number
  rating: number | null
  comments: string | null
}

export interface PerformanceReview {
  id: string
  employee: EmployeeBrief
  reviewer: EmployeeBrief
  type: ReviewType
  status: ReviewStatus
  period_start: string
  period_end: string
  due_date: string
  overall_rating: number | null
  manager_comments: string | null
  employee_comments: string | null
  development_plan: string | null
  criteria: ReviewCriteria[]
  created_at: string
}

export interface Goal {
  id: string
  employee: EmployeeBrief
  title: string
  description: string | null
  category: GoalCategory
  target_date: string
  weight: number
  percent_complete: number
  status: GoalStatus
  parent_goal_id: string | null
}

export interface Incident {
  id: string
  employee: EmployeeBrief
  reported_by: EmployeeBrief
  type: IncidentType
  severity: Severity
  description: string
  incident_date: string
  location: string | null
  status: IncidentStatus
  resolution: string | null
  created_at: string
}

export interface Commendation {
  id: string
  employee: EmployeeBrief
  awarded_by: EmployeeBrief
  category: CommendationCategory
  stars: number
  description: string
  is_public: boolean
  created_at: string
}

// LMS
export interface Course {
  id: string
  title: string
  description: string | null
  category: string
  format: CourseFormat
  duration_hours: number
  is_required: boolean
  trade_specific: string | null
  provider: string | null
}

export interface Certification {
  id: string
  employee: EmployeeBrief
  name: string
  issuing_body: string
  cert_number: string | null
  issue_date: string
  expiration_date: string | null
  status: CertStatus
  course_title: string | null
}

export interface TrainingAssignment {
  id: string
  employee: EmployeeBrief
  course_title: string
  status: TrainingStatus
  due_date: string
  completed_date: string | null
  score: number | null
}

// Dashboard
export interface DashboardKPIs {
  total_headcount: number
  open_positions: number
  pending_reviews: number
  expiring_certs: number
  turnover_rate: number
  avg_tenure_months: number
  training_compliance_pct: number
  active_projects: number
}

export interface ChartDataPoint {
  label: string
  value: number
  category?: string
}

// Audit
export interface AuditLogEntry {
  id: string
  entity_type: string
  entity_id: string
  action: 'CREATE' | 'UPDATE' | 'DELETE'
  field: string | null
  old_value: string | null
  new_value: string | null
  user_email: string
  timestamp: string
}
