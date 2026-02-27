import { useEffect, useState } from 'react'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend,
} from 'recharts'
import { Users, AlertTriangle, Clock, CheckCircle, TrendingUp } from 'lucide-react'
import api from '@/lib/api'

const COLORS = ['#2563eb', '#7aecb4', '#d97706', '#dc2626', '#8b5cf6', '#06b6d4']

export default function DashboardPage() {
  const [kpis, setKpis] = useState<any>(null)
  const [projects, setProjects] = useState<any[]>([])
  const [expiring, setExpiring] = useState<any[]>([])
  const [charts, setCharts] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      api.get('/dashboard/kpis'),
      api.get('/org-chart/projects'),
      api.get('/lms/expiring?days=30'),
      api.get('/dashboard/charts'),
    ]).then(([kRes, pRes, eRes, cRes]) => {
      setKpis(kRes.data)
      setProjects(pRes.data || [])
      setExpiring(eRes.data || [])
      setCharts(cRes.data)
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [])

  const currentDate = new Date().toLocaleDateString('en-US', {
    weekday: 'long', year: 'numeric', month: 'long', day: 'numeric',
  })

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2" style={{ borderColor: 'var(--mint)' }}></div>
      </div>
    )
  }

  const statCards = [
    { label: 'Total Workforce', value: kpis?.total_headcount || 0, icon: Users, color: 'var(--t1)', iconBg: '#eff6ff', iconColor: '#2563eb', delta: '+12 this month', deltaColor: '#2563eb' },
    { label: 'Cert Issues', value: kpis?.expiring_certs || 0, icon: AlertTriangle, color: '#dc2626', iconBg: '#fef2f2', iconColor: '#dc2626', delta: 'Requires attention', deltaColor: '#dc2626' },
    { label: 'Pending Reviews', value: kpis?.pending_reviews || 0, icon: Clock, color: '#d97706', iconBg: '#fffbeb', iconColor: '#d97706', delta: `${kpis?.active_projects || 0} active projects`, deltaColor: 'var(--t3)' },
    { label: 'Training Compliance', value: `${kpis?.training_compliance_pct || 0}%`, icon: CheckCircle, color: '#15803d', iconBg: 'rgba(122,236,180,0.1)', iconColor: '#15803d', delta: `Avg tenure: ${kpis?.avg_tenure_months || 0}mo`, deltaColor: 'var(--t3)' },
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-xl font-bold" style={{ color: 'var(--t1)' }}>HRIS Dashboard</h1>
        <p className="text-sm mt-1" style={{ color: 'var(--t3)' }}>
          Summit Construction Group · All Projects · {currentDate}
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-4 gap-4">
        {statCards.map((s, i) => (
          <div key={i} className="bg-white rounded-xl border p-5 shadow-sm" style={{ borderColor: 'var(--border)' }}>
            <div className="w-10 h-10 rounded-lg flex items-center justify-center mb-3"
              style={{ backgroundColor: s.iconBg }}>
              <s.icon size={20} style={{ color: s.iconColor }} />
            </div>
            <div className="text-3xl font-bold" style={{ color: s.color }}>{s.value}</div>
            <div className="text-sm mt-1" style={{ color: 'var(--t3)' }}>{s.label}</div>
            <div className="flex items-center gap-1 mt-2 text-xs" style={{ color: s.deltaColor }}>
              <TrendingUp size={12} />
              <span>{s.delta}</span>
            </div>
          </div>
        ))}
      </div>

      {/* Two columns: Projects + Renewals */}
      <div className="grid grid-cols-2 gap-4">
        {/* Projects Overview */}
        <div className="bg-white rounded-xl border shadow-sm" style={{ borderColor: 'var(--border)' }}>
          <div className="px-5 py-4 border-b flex items-center justify-between" style={{ borderColor: 'var(--border)' }}>
            <span className="font-semibold" style={{ color: 'var(--t1)' }}>Projects Overview</span>
            <span className="text-xs px-2 py-1 rounded" style={{ backgroundColor: 'var(--mint-bg)', color: '#15803d' }}>
              {projects.length} active
            </span>
          </div>
          <div className="divide-y" style={{ borderColor: 'var(--border)' }}>
            {projects.slice(0, 6).map((p: any) => {
              const crewCount = p.crews?.length || 0
              const workerCount = p.total_workers || 0
              const initials = p.name.split(' ').map((w: string) => w[0]).join('').slice(0, 2)
              return (
                <div key={p.id} className="px-5 py-3 flex items-center gap-3">
                  <div className="w-9 h-9 rounded-full flex items-center justify-center text-white text-xs font-semibold"
                    style={{ background: 'linear-gradient(135deg, #7aecb4, #34d399)' }}>
                    {initials}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="font-medium text-sm truncate" style={{ color: 'var(--t1)' }}>{p.name}</div>
                    <div className="text-xs" style={{ color: 'var(--t3)' }}>
                      {workerCount} workers · {crewCount} crews · {p.status}
                    </div>
                  </div>
                  <span className="px-2 py-1 rounded-full text-xs font-medium"
                    style={{ backgroundColor: 'rgba(122,236,180,.1)', color: '#15803d', border: '1px solid rgba(122,236,180,.25)' }}>
                    {p.status === 'ACTIVE' ? 'Active' : p.status}
                  </span>
                </div>
              )
            })}
            {projects.length === 0 && (
              <div className="px-5 py-8 text-center text-sm" style={{ color: 'var(--t3)' }}>No active projects</div>
            )}
          </div>
        </div>

        {/* Upcoming Renewals */}
        <div className="bg-white rounded-xl border shadow-sm" style={{ borderColor: 'var(--border)' }}>
          <div className="px-5 py-4 border-b flex items-center justify-between" style={{ borderColor: 'var(--border)' }}>
            <span className="font-semibold" style={{ color: 'var(--t1)' }}>Upcoming Renewals</span>
            <span className="text-xs px-2 py-1 rounded" 
              style={{ backgroundColor: 'rgba(217,119,6,.07)', color: '#d97706' }}>
              {expiring.length} expiring
            </span>
          </div>
          <div className="divide-y" style={{ borderColor: 'var(--border)' }}>
            {expiring.slice(0, 6).map((c: any, i: number) => (
              <div key={i} className="px-5 py-3 flex items-center gap-3">
                <div className="flex-1 min-w-0">
                  <div className="font-medium text-sm" style={{ color: 'var(--t1)' }}>
                    {c.employee_name} — {c.name || c.certification_name}
                  </div>
                  <div className="text-xs" style={{ color: 'var(--t3)' }}>
                    Expires: {c.expiration_date}
                  </div>
                </div>
                <span className="px-2.5 py-1 rounded-full text-xs font-semibold"
                  style={{ 
                    backgroundColor: 'rgba(217,119,6,.07)', 
                    color: '#d97706',
                    border: '1px solid rgba(217,119,6,.2)',
                  }}>
                  {c.days_until_expiry || c.days_remaining} days
                </span>
              </div>
            ))}
            {expiring.length === 0 && (
              <div className="px-5 py-8 text-center text-sm" style={{ color: 'var(--t3)' }}>
                No certifications expiring in the next 30 days
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-2 gap-4">
        {/* Headcount by Department */}
        <div className="bg-white rounded-xl border shadow-sm" style={{ borderColor: 'var(--border)' }}>
          <div className="px-5 py-4 border-b" style={{ borderColor: 'var(--border)' }}>
            <span className="font-semibold" style={{ color: 'var(--t1)' }}>Headcount by Department</span>
          </div>
          <div className="p-5">
            {charts?.by_department ? (
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={charts.by_department} layout="vertical" margin={{ left: 80 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                  <XAxis type="number" tick={{ fontSize: 11, fill: 'var(--t3)' }} />
                  <YAxis type="category" dataKey="name" tick={{ fontSize: 11, fill: 'var(--t2)' }} width={80} />
                  <Tooltip contentStyle={{ backgroundColor: '#fff', border: '1px solid var(--border)', borderRadius: '8px', fontSize: '12px' }} />
                  <Bar dataKey="count" fill="#7aecb4" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-[250px] flex items-center justify-center text-sm" style={{ color: 'var(--t3)' }}>
                No chart data
              </div>
            )}
          </div>
        </div>

        {/* Employee Type */}
        <div className="bg-white rounded-xl border shadow-sm" style={{ borderColor: 'var(--border)' }}>
          <div className="px-5 py-4 border-b" style={{ borderColor: 'var(--border)' }}>
            <span className="font-semibold" style={{ color: 'var(--t1)' }}>Employee Type Distribution</span>
          </div>
          <div className="p-5">
            {charts?.by_type ? (
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie data={charts.by_type} cx="50%" cy="50%" innerRadius={55} outerRadius={90}
                    paddingAngle={2} dataKey="value" nameKey="name"
                    label={({ name, percent }: any) => `${name} ${(percent * 100).toFixed(0)}%`}
                    labelLine={false}>
                    {charts.by_type.map((_: any, i: number) => (
                      <Cell key={i} fill={COLORS[i % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={{ backgroundColor: '#fff', border: '1px solid var(--border)', borderRadius: '8px', fontSize: '12px' }} />
                  <Legend wrapperStyle={{ fontSize: '12px' }} />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-[250px] flex items-center justify-center text-sm" style={{ color: 'var(--t3)' }}>
                No chart data
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
