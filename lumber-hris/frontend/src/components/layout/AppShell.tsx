import { NavLink, useNavigate, useLocation } from 'react-router-dom'
import { Bell, Settings, ChevronDown, LogOut } from 'lucide-react'
import { useAuth } from '@/context/AuthContext'

const roleLabels: Record<string, string> = {
  ADMIN: 'Administrator',
  HR_MANAGER: 'HR Manager',
  PROJECT_MANAGER: 'Project Manager',
  FOREMAN: 'Foreman',
  EMPLOYEE: 'Employee',
}

const topNavItems = [
  { label: 'Time' },
  { label: 'Pay' },
  { label: 'Scheduler' },
  { label: 'Resources' },
  { label: 'HR', active: true },
  { label: 'Reports' },
  { label: 'Documents' },
  { label: 'Forms' },
]

const subNavItems = [
  { label: 'Dashboard', path: '/dashboard' },
  { label: 'LMS & Training', path: '/lms', badge: 7 },
  { label: 'BuilderFax', path: '/builderfax' },
  { label: 'Performance', path: '/performance' },
  { label: 'Org Chart', path: '/org-chart' },
  { label: 'Analytics', path: '/analytics' },
  { label: 'Employees', path: '/employees' },
]

export default function AppShell({ children }: { children: React.ReactNode }) {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const userName = user?.email?.split('@')[0] || 'User'
  const userRole = user?.role ? roleLabels[user.role] || user.role : 'User'

  const isSubActive = (path: string) => {
    if (path === '/dashboard') return location.pathname === '/' || location.pathname === '/dashboard'
    return location.pathname.startsWith(path)
  }

  return (
    <div className="h-screen flex flex-col overflow-hidden" style={{ backgroundColor: 'var(--page-bg)' }}>
      {/* ── TOP NAV ── */}
      <header className="flex items-center shrink-0 px-5 gap-0" 
        style={{ height: '52px', backgroundColor: '#1e2d3b' }}>
        {/* Logo */}
        <div className="flex items-center gap-2 pr-6 mr-4 shrink-0"
          style={{ borderRight: '1px solid rgba(255,255,255,0.1)' }}>
          <span style={{ color: '#7aecb4', fontSize: '20px' }}>⬡</span>
          <span className="font-bold text-lg tracking-wide" style={{ color: '#ffffff' }}>LUMBER</span>
        </div>

        {/* Main nav links */}
        <nav className="flex items-center gap-0.5 flex-1">
          {topNavItems.map((item) => (
            <button key={item.label}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-[13px] font-medium transition-all"
              style={{
                color: item.active ? '#7aecb4' : '#c8d6e2',
                backgroundColor: item.active ? 'rgba(122,236,180,0.15)' : 'transparent',
              }}
              onMouseEnter={(e) => { if (!item.active) e.currentTarget.style.backgroundColor = 'rgba(255,255,255,0.08)' }}
              onMouseLeave={(e) => { if (!item.active) e.currentTarget.style.backgroundColor = 'transparent' }}
            >
              {item.label}
              <ChevronDown size={11} />
            </button>
          ))}
        </nav>

        {/* Right: notifications, settings, company */}
        <div className="flex items-center gap-2 shrink-0">
          <button className="relative w-8 h-8 rounded-md flex items-center justify-center transition-colors"
            style={{ color: '#c8d6e2' }}
            onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'rgba(255,255,255,0.08)'}
            onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}>
            <Bell size={18} />
            <span className="absolute -top-0.5 -right-0.5 w-3.5 h-3.5 rounded-full text-white flex items-center justify-center"
              style={{ fontSize: '9px', fontWeight: 700, backgroundColor: '#dc2626', border: '1.5px solid #1e2d3b' }}>3</span>
          </button>
          <button className="w-8 h-8 rounded-md flex items-center justify-center transition-colors"
            style={{ color: '#c8d6e2' }}
            onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'rgba(255,255,255,0.08)'}
            onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}>
            <Settings size={18} />
          </button>
          <button className="flex items-center gap-2 px-3 py-1.5 rounded-md text-xs font-medium"
            style={{ 
              color: '#ffffff', 
              backgroundColor: 'rgba(255,255,255,0.08)',
              border: '1px solid rgba(255,255,255,0.12)',
            }}>
            Summit Construction Group
            <ChevronDown size={11} />
          </button>
        </div>
      </header>

      {/* ── SUB NAV ── */}
      <nav className="flex items-center px-6 gap-0.5 shrink-0"
        style={{ 
          height: '44px', 
          backgroundColor: '#ffffff',
          borderBottom: '1px solid var(--border)',
        }}>
        <div className="flex items-center gap-0.5 flex-1">
          {subNavItems.map((item) => {
            const active = isSubActive(item.path)
            return (
              <NavLink key={item.path} to={item.path}
                className="relative flex items-center gap-2 px-3.5 py-2.5 text-[13px] font-medium transition-colors"
                style={{
                  color: active ? '#2563eb' : '#6b7280',
                }}>
                {item.label}
                {item.badge && (
                  <span className="flex items-center justify-center rounded-full text-white"
                    style={{ 
                      fontSize: '9px', fontWeight: 700, 
                      backgroundColor: '#dc2626',
                      padding: '1px 5px',
                      minWidth: '16px',
                    }}>{item.badge}</span>
                )}
                {active && (
                  <span className="absolute bottom-0 left-3.5 right-3.5 h-0.5 rounded-t"
                    style={{ backgroundColor: '#2563eb' }} />
                )}
              </NavLink>
            )
          })}
        </div>

        {/* User info */}
        <div className="flex items-center gap-3 shrink-0">
          <div className="w-8 h-8 rounded-full flex items-center justify-center text-white text-xs font-semibold"
            style={{ backgroundColor: '#2563eb' }}>
            {userName[0]?.toUpperCase() || 'U'}
          </div>
          <div className="flex flex-col">
            <span className="text-sm font-medium" style={{ color: 'var(--t1)' }}>{userName}</span>
            <span className="text-xs" style={{ color: 'var(--t4)' }}>{userRole}</span>
          </div>
          <button onClick={handleLogout}
            className="flex items-center gap-1 px-2 py-1.5 rounded-md text-xs transition-colors"
            style={{ color: 'var(--t3)' }}
            onMouseEnter={(e) => { e.currentTarget.style.color = '#dc2626'; e.currentTarget.style.backgroundColor = 'rgba(220,38,38,0.05)' }}
            onMouseLeave={(e) => { e.currentTarget.style.color = 'var(--t3)'; e.currentTarget.style.backgroundColor = 'transparent' }}>
            <LogOut size={14} />
          </button>
        </div>
      </nav>

      {/* ── CONTENT ── */}
      <main className="flex-1 overflow-auto p-6" style={{ backgroundColor: 'var(--page-bg)' }}>
        {children}
      </main>
    </div>
  )
}
