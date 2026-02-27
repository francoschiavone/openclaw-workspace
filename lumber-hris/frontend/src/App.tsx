import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from '@/context/AuthContext'
import AppShell from '@/components/layout/AppShell'
import LoginPage from '@/pages/LoginPage'
import DashboardPage from '@/pages/DashboardPage'
import EmployeesPage from '@/pages/EmployeesPage'
import EmployeeProfilePage from '@/pages/EmployeeProfilePage'
import OrgChartPage from '@/pages/OrgChartPage'
import PerformancePage from '@/pages/PerformancePage'
import LMSPage from '@/pages/LMSPage'
import AnalyticsPage from '@/pages/AnalyticsPage'
import BuilderFaxPage from '@/pages/BuilderFaxPage'

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth()
  
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen" style={{ backgroundColor: 'var(--page-bg)' }}>
        <div className="animate-spin rounded-full h-12 w-12 border-b-2" style={{ borderColor: 'var(--mint)' }}></div>
      </div>
    )
  }
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }
  
  return <>{children}</>
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/*"
        element={
          <ProtectedRoute>
            <AppShell>
              <Routes>
                <Route path="/" element={<Navigate to="/dashboard" replace />} />
                <Route path="/dashboard" element={<DashboardPage />} />
                <Route path="/employees" element={<EmployeesPage />} />
                <Route path="/employees/:id" element={<EmployeeProfilePage />} />
                <Route path="/org-chart" element={<OrgChartPage />} />
                <Route path="/performance" element={<PerformancePage />} />
                <Route path="/lms" element={<LMSPage />} />
                <Route path="/analytics" element={<AnalyticsPage />} />
                <Route path="/builderfax" element={<BuilderFaxPage />} />
              </Routes>
            </AppShell>
          </ProtectedRoute>
        }
      />
    </Routes>
  )
}
