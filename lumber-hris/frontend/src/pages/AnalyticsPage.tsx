import { useState, useEffect } from 'react'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend, LineChart, Line,
} from 'recharts'
import { Users, TrendingUp, Clock, BarChart3 } from 'lucide-react'
import api from '@/lib/api'

type Tab = 'workforce' | 'performance' | 'training' | 'organization'
const COLORS = ['#7aecb4', '#2563eb', '#d97706', '#dc2626', '#7c3aed', '#0891b2', '#ea580c', '#6366f1']

export default function AnalyticsPage() {
  const [tab, setTab] = useState<Tab>('workforce')
  const [workforce, setWorkforce] = useState<any>(null)
  const [performance, setPerformance] = useState<any>(null)
  const [training, setTraining] = useState<any>(null)
  const [organization, setOrganization] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      api.get('/analytics/workforce'),
      api.get('/analytics/performance'),
      api.get('/analytics/training'),
      api.get('/analytics/organization'),
    ]).then(([wR, pR, tR, oR]) => {
      setWorkforce(wR.data)
      setPerformance(pR.data)
      setTraining(tR.data)
      setOrganization(oR.data)
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [])

  const tabs: { key: Tab; label: string }[] = [
    { key: 'workforce', label: 'Workforce' },
    { key: 'performance', label: 'Performance' },
    { key: 'training', label: 'Training' },
    { key: 'organization', label: 'Organization' },
  ]

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2" style={{ borderColor: 'var(--mint)' }}></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold" style={{ color: 'var(--t1)' }}>Analytics & Reporting</h1>
        <p className="text-sm mt-1" style={{ color: 'var(--t3)' }}>Workforce insights · performance metrics · training compliance</p>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-1 pb-3 border-b" style={{ borderColor: 'var(--border)' }}>
        {tabs.map(t => (
          <button key={t.key} onClick={() => setTab(t.key)}
            className="px-4 py-2 rounded-lg text-sm font-medium transition-colors"
            style={{
              backgroundColor: tab === t.key ? 'rgba(37,99,235,.08)' : 'transparent',
              color: tab === t.key ? 'var(--blue)' : 'var(--t3)',
              border: tab === t.key ? '1px solid rgba(37,99,235,.2)' : '1px solid transparent',
            }}>
            {t.label}
          </button>
        ))}
      </div>

      {/* Workforce */}
      {tab === 'workforce' && workforce && (
        <div className="space-y-6">
          <div className="grid grid-cols-4 gap-4">
            {[
              { label: 'Total Employees', value: workforce.total_employees, icon: Users, color: 'var(--t1)' },
              { label: 'Turnover Rate', value: `${workforce.turnover_rate || 0}%`, icon: TrendingUp, color: '#d97706' },
              { label: 'Avg Tenure', value: `${Math.round(workforce.avg_tenure || 0)}mo`, icon: Clock, color: 'var(--blue)' },
              { label: 'Departments', value: workforce.by_department?.length || 0, icon: BarChart3, color: '#15803d' },
            ].map((s, i) => (
              <div key={i} className="bg-white rounded-xl border p-5" style={{ borderColor: 'var(--border)' }}>
                <div className="flex items-center gap-3">
                  <s.icon size={20} style={{ color: s.color }} />
                  <div>
                    <div className="text-2xl font-bold" style={{ color: s.color }}>{s.value}</div>
                    <div className="text-xs" style={{ color: 'var(--t3)' }}>{s.label}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="grid grid-cols-2 gap-4">
            {/* By Department */}
            <div className="bg-white rounded-xl border p-5" style={{ borderColor: 'var(--border)' }}>
              <h3 className="font-semibold mb-4" style={{ color: 'var(--t1)' }}>Headcount by Department</h3>
              {workforce.by_department && (
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={workforce.by_department} layout="vertical" margin={{ left: 80 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                    <XAxis type="number" tick={{ fontSize: 11, fill: 'var(--t3)' }} />
                    <YAxis type="category" dataKey="name" tick={{ fontSize: 11, fill: 'var(--t2)' }} width={80} />
                    <Tooltip contentStyle={{ fontSize: '12px', borderRadius: '8px', border: '1px solid var(--border)' }} />
                    <Bar dataKey="count" fill="#7aecb4" radius={[0, 4, 4, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              )}
            </div>

            {/* By Type */}
            <div className="bg-white rounded-xl border p-5" style={{ borderColor: 'var(--border)' }}>
              <h3 className="font-semibold mb-4" style={{ color: 'var(--t1)' }}>Employee Type Distribution</h3>
              {workforce.by_type && (
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie data={workforce.by_type.map((t: any) => ({ name: t.type?.replace(/_/g, ' '), value: t.count }))}
                      cx="50%" cy="50%" innerRadius={60} outerRadius={100} paddingAngle={2} dataKey="value"
                      label={({ name, percent }: any) => `${name} ${(percent * 100).toFixed(0)}%`} labelLine={false}>
                      {workforce.by_type.map((_: any, i: number) => (
                        <Cell key={i} fill={COLORS[i % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                    <Legend wrapperStyle={{ fontSize: '12px' }} />
                  </PieChart>
                </ResponsiveContainer>
              )}
            </div>

            {/* By Gender */}
            <div className="bg-white rounded-xl border p-5" style={{ borderColor: 'var(--border)' }}>
              <h3 className="font-semibold mb-4" style={{ color: 'var(--t1)' }}>Gender Distribution</h3>
              {workforce.by_gender && (
                <ResponsiveContainer width="100%" height={250}>
                  <PieChart>
                    <Pie data={workforce.by_gender.map((g: any) => ({ name: g.gender, value: g.count }))}
                      cx="50%" cy="50%" innerRadius={50} outerRadius={85} paddingAngle={2} dataKey="value"
                      label={({ name, percent }: any) => `${name} ${(percent * 100).toFixed(0)}%`} labelLine={false}>
                      {workforce.by_gender.map((_: any, i: number) => (
                        <Cell key={i} fill={['#2563eb', '#7aecb4', '#d97706', '#6b7280'][i]} />
                      ))}
                    </Pie>
                    <Tooltip />
                    <Legend wrapperStyle={{ fontSize: '12px' }} />
                  </PieChart>
                </ResponsiveContainer>
              )}
            </div>

            {/* By Status */}
            <div className="bg-white rounded-xl border p-5" style={{ borderColor: 'var(--border)' }}>
              <h3 className="font-semibold mb-4" style={{ color: 'var(--t1)' }}>By Status</h3>
              {workforce.by_status && (
                <div className="space-y-3 mt-4">
                  {workforce.by_status.map((s: any, i: number) => {
                    const total = workforce.total_employees || 1
                    const pct = Math.round((s.count / total) * 100)
                    const colors = ['#15803d', '#d97706', '#ea580c', '#dc2626']
                    return (
                      <div key={i}>
                        <div className="flex justify-between text-sm mb-1">
                          <span style={{ color: 'var(--t2)' }}>{s.status?.replace(/_/g, ' ')}</span>
                          <span className="font-semibold" style={{ color: 'var(--t1)' }}>{s.count} ({pct}%)</span>
                        </div>
                        <div className="h-2 rounded-full" style={{ backgroundColor: '#e5e7eb' }}>
                          <div className="h-2 rounded-full transition-all" style={{
                            width: `${pct}%`, backgroundColor: colors[i % colors.length]
                          }}></div>
                        </div>
                      </div>
                    )
                  })}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Performance */}
      {tab === 'performance' && performance && (
        <div className="space-y-6">
          <div className="grid grid-cols-3 gap-4">
            <div className="bg-white rounded-xl border p-5" style={{ borderColor: 'var(--border)' }}>
              <div className="text-xs uppercase tracking-wider mb-1" style={{ color: 'var(--t3)' }}>Avg Rating</div>
              <div className="text-3xl font-bold" style={{ color: 'var(--t1)' }}>{performance.avg_rating?.toFixed(1) || '—'}</div>
              <div className="text-xs mt-1" style={{ color: 'var(--t3)' }}>out of 5.0</div>
            </div>
            <div className="bg-white rounded-xl border p-5" style={{ borderColor: 'var(--border)' }}>
              <div className="text-xs uppercase tracking-wider mb-1" style={{ color: 'var(--t3)' }}>Review Completion</div>
              <div className="text-3xl font-bold" style={{ color: '#15803d' }}>{performance.review_completion_rate || 0}%</div>
            </div>
            <div className="bg-white rounded-xl border p-5" style={{ borderColor: 'var(--border)' }}>
              <div className="text-xs uppercase tracking-wider mb-1" style={{ color: 'var(--t3)' }}>Total Reviews</div>
              <div className="text-3xl font-bold" style={{ color: 'var(--blue)' }}>
                {performance.rating_distribution?.reduce((a: number, b: any) => a + b.count, 0) || 0}
              </div>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="bg-white rounded-xl border p-5" style={{ borderColor: 'var(--border)' }}>
              <h3 className="font-semibold mb-4" style={{ color: 'var(--t1)' }}>Rating Distribution</h3>
              {performance.rating_distribution && (
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={performance.rating_distribution}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                    <XAxis dataKey="rating" tick={{ fontSize: 12, fill: 'var(--t3)' }} />
                    <YAxis tick={{ fontSize: 12, fill: 'var(--t3)' }} />
                    <Tooltip contentStyle={{ fontSize: '12px', borderRadius: '8px' }} />
                    <Bar dataKey="count" fill="#2563eb" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              )}
            </div>
            <div className="bg-white rounded-xl border p-5" style={{ borderColor: 'var(--border)' }}>
              <h3 className="font-semibold mb-4" style={{ color: 'var(--t1)' }}>By Department</h3>
              {performance.by_department && (
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={performance.by_department} layout="vertical" margin={{ left: 80 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                    <XAxis type="number" domain={[0, 5]} tick={{ fontSize: 11, fill: 'var(--t3)' }} />
                    <YAxis type="category" dataKey="dept" tick={{ fontSize: 11, fill: 'var(--t2)' }} width={80} />
                    <Tooltip contentStyle={{ fontSize: '12px', borderRadius: '8px' }} />
                    <Bar dataKey="avg" fill="#7aecb4" radius={[0, 4, 4, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Training */}
      {tab === 'training' && training && (
        <div className="space-y-6">
          <div className="grid grid-cols-3 gap-4">
            <div className="bg-white rounded-xl border p-5" style={{ borderColor: 'var(--border)' }}>
              <div className="text-xs uppercase tracking-wider mb-1" style={{ color: 'var(--t3)' }}>Total Courses</div>
              <div className="text-3xl font-bold" style={{ color: 'var(--t1)' }}>{training.total_courses || 0}</div>
            </div>
            <div className="bg-white rounded-xl border p-5" style={{ borderColor: 'var(--border)' }}>
              <div className="text-xs uppercase tracking-wider mb-1" style={{ color: 'var(--t3)' }}>Compliance Rate</div>
              <div className="text-3xl font-bold" style={{ color: '#15803d' }}>{training.compliance_rate || 0}%</div>
            </div>
            <div className="bg-white rounded-xl border p-5" style={{ borderColor: 'var(--border)' }}>
              <div className="text-xs uppercase tracking-wider mb-1" style={{ color: 'var(--t3)' }}>Categories</div>
              <div className="text-3xl font-bold" style={{ color: 'var(--blue)' }}>{training.by_category?.length || 0}</div>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="bg-white rounded-xl border p-5" style={{ borderColor: 'var(--border)' }}>
              <h3 className="font-semibold mb-4" style={{ color: 'var(--t1)' }}>Courses by Category</h3>
              {training.by_category && (
                <ResponsiveContainer width="100%" height={250}>
                  <PieChart>
                    <Pie data={training.by_category.map((c: any) => ({ name: c.category, value: c.count }))}
                      cx="50%" cy="50%" innerRadius={55} outerRadius={90} paddingAngle={2} dataKey="value"
                      label={({ name, value }: any) => `${name} (${value})`} labelLine={false}>
                      {training.by_category.map((_: any, i: number) => (
                        <Cell key={i} fill={COLORS[i % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              )}
            </div>
            <div className="bg-white rounded-xl border p-5" style={{ borderColor: 'var(--border)' }}>
              <h3 className="font-semibold mb-4" style={{ color: 'var(--t1)' }}>Monthly Completions</h3>
              {training.completion_trend && (
                <ResponsiveContainer width="100%" height={250}>
                  <LineChart data={training.completion_trend}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                    <XAxis dataKey="month" tick={{ fontSize: 11, fill: 'var(--t3)' }} />
                    <YAxis tick={{ fontSize: 11, fill: 'var(--t3)' }} />
                    <Tooltip contentStyle={{ fontSize: '12px', borderRadius: '8px' }} />
                    <Line type="monotone" dataKey="completed" stroke="#7aecb4" strokeWidth={2} dot={{ r: 4 }} />
                  </LineChart>
                </ResponsiveContainer>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Organization */}
      {tab === 'organization' && organization && (
        <div className="space-y-6">
          <div className="grid grid-cols-4 gap-4">
            {[
              { label: 'Departments', value: organization.department_count || 0 },
              { label: 'Avg Span of Control', value: organization.avg_span?.toFixed(1) || '—' },
              { label: 'Hierarchy Depth', value: organization.hierarchy_depth || '—' },
              { label: 'Divisions', value: organization.by_division?.length || 0 },
            ].map((s, i) => (
              <div key={i} className="bg-white rounded-xl border p-5" style={{ borderColor: 'var(--border)' }}>
                <div className="text-2xl font-bold" style={{ color: 'var(--t1)' }}>{s.value}</div>
                <div className="text-xs mt-1" style={{ color: 'var(--t3)' }}>{s.label}</div>
              </div>
            ))}
          </div>

          {organization.by_division && (
            <div className="bg-white rounded-xl border p-5" style={{ borderColor: 'var(--border)' }}>
              <h3 className="font-semibold mb-4" style={{ color: 'var(--t1)' }}>Division Breakdown</h3>
              <div className="grid grid-cols-3 gap-4">
                {organization.by_division.map((d: any, i: number) => (
                  <div key={i} className="rounded-xl p-5" style={{ backgroundColor: COLORS[i % COLORS.length] + '12', border: `1px solid ${COLORS[i % COLORS.length]}30` }}>
                    <div className="font-semibold" style={{ color: 'var(--t1)' }}>{d.division}</div>
                    <div className="text-2xl font-bold mt-2" style={{ color: COLORS[i % COLORS.length] }}>
                      {d.employee_count}
                    </div>
                    <div className="text-xs mt-1" style={{ color: 'var(--t3)' }}>
                      {d.dept_count} departments
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
