import { useState, useEffect } from 'react'
import { BookOpen, Users, CheckCircle, Clock, Search, Shield, Settings } from 'lucide-react'
import api from '@/lib/api'

type Tab = 'manager' | 'catalog' | 'learning' | 'rules'

const statusColors: Record<string, { bg: string; color: string; label: string }> = {
  COMPLETED: { bg: 'rgba(122,236,180,.1)', color: '#15803d', label: 'Completed' },
  IN_PROGRESS: { bg: 'rgba(37,99,235,.08)', color: '#2563eb', label: 'In Progress' },
  ASSIGNED: { bg: '#f5f6f8', color: '#6b7280', label: 'Not Started' },
  OVERDUE: { bg: 'rgba(220,38,38,.07)', color: '#dc2626', label: 'Overdue' },
}

const formatBadge: Record<string, string> = {
  E_LEARNING: '💻 Online',
  INSTRUCTOR_LED: '👨‍🏫 In-Person',
  TOOLBOX_TALK: '🔧 Toolbox Talk',
}

const categoryIcons: Record<string, string> = {
  'Safety': '🦺',
  'Technical': '⚙️',
  'Compliance': '📋',
  'Leadership': '🎯',
  'Equipment': '🔧',
}

const triggerLabels: Record<string, string> = {
  NEW_HIRE: 'Triggered on new hire',
  CERT_EXPIRING: 'Triggered on certification expiry',
  LOW_REVIEW_SCORE: 'Triggered on low review score',
}

export default function LMSPage() {
  const [tab, setTab] = useState<Tab>('manager')
  const [courses, setCourses] = useState<any[]>([])
  const [assignments, setAssignments] = useState<any[]>([])
  const [expiring, setExpiring] = useState<any[]>([])
  const [compliance, setCompliance] = useState<any>(null)
  const [rules, setRules] = useState<any[]>([])
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      api.get('/lms/courses'),
      api.get('/lms/assignments'),
      api.get('/lms/expiring?days=30'),
      api.get('/lms/compliance'),
      api.get('/lms/rules'),
    ]).then(([cRes, aRes, eRes, compRes, rRes]) => {
      setCourses(cRes.data || [])
      setAssignments(aRes.data || [])
      setExpiring(eRes.data || [])
      setCompliance(compRes.data)
      setRules(rRes.data || [])
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [])

  const filteredAssignments = assignments.filter((a: any) => {
    if (search && !a.employee_name?.toLowerCase().includes(search.toLowerCase()) &&
      !a.course_title?.toLowerCase().includes(search.toLowerCase())) return false
    if (statusFilter && a.status !== statusFilter) return false
    return true
  })

  const completedCount = assignments.filter((a: any) => a.status === 'COMPLETED').length
  const compRate = assignments.length ? Math.round((completedCount / assignments.length) * 100) : 0

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2" style={{ borderColor: 'var(--mint)' }}></div>
      </div>
    )
  }

  const tabs: { key: Tab; label: string; icon: any }[] = [
    { key: 'manager', label: 'Manager View', icon: Users },
    { key: 'catalog', label: 'Course Catalog', icon: BookOpen },
    { key: 'learning', label: 'My Learning', icon: CheckCircle },
    { key: 'rules', label: 'Auto-Enrollment Rules', icon: Settings },
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold" style={{ color: 'var(--t1)' }}>LMS & Training</h1>
          <p className="text-sm mt-1" style={{ color: 'var(--t3)' }}>Learning management · certifications · auto-enrollment</p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold"
          style={{ backgroundColor: 'var(--mint)', color: '#0a4023' }}>
          + Assign Course
        </button>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-1 pb-3 border-b" style={{ borderColor: 'var(--border)' }}>
        {tabs.map(t => (
          <button key={t.key} onClick={() => setTab(t.key)}
            className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors"
            style={{
              backgroundColor: tab === t.key ? 'rgba(37,99,235,.08)' : 'transparent',
              color: tab === t.key ? 'var(--blue)' : 'var(--t3)',
              border: tab === t.key ? '1px solid rgba(37,99,235,.2)' : '1px solid transparent',
            }}>
            <t.icon size={15} />
            {t.label}
          </button>
        ))}
      </div>

      {/* Manager View */}
      {tab === 'manager' && (
        <div className="space-y-6">
          {/* Stats */}
          <div className="grid grid-cols-4 gap-4">
            {[
              { label: 'Total Courses', value: courses.length, icon: BookOpen, color: 'var(--blue)' },
              { label: 'Active Assignments', value: assignments.length, icon: Users, color: 'var(--t1)' },
              { label: 'Completion Rate', value: `${compRate}%`, icon: CheckCircle, color: '#15803d' },
              { label: 'Expiring Soon', value: expiring.length, icon: Clock, color: '#d97706' },
            ].map((s, i) => (
              <div key={i} className="bg-white rounded-xl border p-5" style={{ borderColor: 'var(--border)' }}>
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg flex items-center justify-center" style={{ backgroundColor: s.color + '12' }}>
                    <s.icon size={20} style={{ color: s.color }} />
                  </div>
                  <div>
                    <div className="text-2xl font-bold" style={{ color: s.color }}>{s.value}</div>
                    <div className="text-xs" style={{ color: 'var(--t3)' }}>{s.label}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Filter */}
          <div className="bg-white rounded-xl border p-4 flex items-center gap-4" style={{ borderColor: 'var(--border)' }}>
            <div className="flex-1 flex items-center gap-2 px-3 py-2 rounded-lg bg-gray-50">
              <Search size={16} style={{ color: 'var(--t4)' }} />
              <input type="text" placeholder="Search assignments..." value={search}
                onChange={e => setSearch(e.target.value)}
                className="bg-transparent border-none outline-none flex-1 text-sm" style={{ color: 'var(--t1)' }} />
            </div>
            <select value={statusFilter} onChange={e => setStatusFilter(e.target.value)}
              className="px-3 py-2 border rounded-lg text-sm" style={{ borderColor: 'var(--border2)', color: 'var(--t1)' }}>
              <option value="">All Statuses</option>
              <option value="COMPLETED">Completed</option>
              <option value="IN_PROGRESS">In Progress</option>
              <option value="ASSIGNED">Not Started</option>
              <option value="OVERDUE">Overdue</option>
            </select>
          </div>

          {/* Assignments table */}
          <div className="bg-white rounded-xl border overflow-hidden" style={{ borderColor: 'var(--border)' }}>
            <table className="w-full">
              <thead className="bg-gray-50 border-b" style={{ borderColor: 'var(--border)' }}>
                <tr>
                  {['Employee', 'Course', 'Status', 'Progress', 'Due Date'].map(h => (
                    <th key={h} className="text-left px-4 py-3 text-xs font-semibold uppercase tracking-wider" style={{ color: 'var(--t3)' }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {filteredAssignments.slice(0, 30).map((a: any, i: number) => {
                  const sc = statusColors[a.status] || statusColors.ASSIGNED
                  const progress = a.status === 'COMPLETED' ? 100 : a.status === 'IN_PROGRESS' ? 50 : 0
                  return (
                    <tr key={i} className="border-b hover:bg-gray-50" style={{ borderColor: 'var(--border)' }}>
                      <td className="px-4 py-3 text-sm font-medium" style={{ color: 'var(--t1)' }}>{a.employee_name}</td>
                      <td className="px-4 py-3 text-sm" style={{ color: 'var(--t2)' }}>{a.course_title}</td>
                      <td className="px-4 py-3">
                        <span className="px-2 py-0.5 rounded text-xs font-semibold" style={{ backgroundColor: sc.bg, color: sc.color }}>{sc.label}</span>
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-2">
                          <div className="w-20 h-1.5 rounded-full" style={{ backgroundColor: '#e5e7eb' }}>
                            <div className="h-1.5 rounded-full" style={{ width: `${progress}%`, backgroundColor: 'var(--mint)' }}></div>
                          </div>
                          <span className="text-xs" style={{ color: 'var(--t3)' }}>{progress}%</span>
                        </div>
                      </td>
                      <td className="px-4 py-3 text-sm" style={{ color: 'var(--t3)' }}>{a.due_date?.slice(0, 10)}</td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>

          {/* Expiring certs */}
          {expiring.length > 0 && (
            <div>
              <h2 className="font-semibold mb-3" style={{ color: 'var(--t1)' }}>Expiring Certifications ({expiring.length})</h2>
              <div className="grid grid-cols-2 gap-3">
                {expiring.slice(0, 8).map((c: any, i: number) => (
                  <div key={i} className="bg-white rounded-xl border p-4 flex items-center justify-between"
                    style={{ borderColor: 'var(--border)', borderLeft: '3px solid #d97706' }}>
                    <div>
                      <div className="font-medium text-sm" style={{ color: 'var(--t1)' }}>{c.employee_name}</div>
                      <div className="text-xs" style={{ color: 'var(--t3)' }}>{c.name || c.certification_name}</div>
                    </div>
                    <span className="px-2.5 py-1 rounded-full text-xs font-bold"
                      style={{ backgroundColor: 'rgba(217,119,6,.07)', color: '#d97706' }}>
                      {c.days_until_expiry || c.days_remaining}d
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Course Catalog */}
      {tab === 'catalog' && (
        <div className="grid grid-cols-3 gap-4">
          {courses.map((c: any) => (
            <div key={c.id} className="bg-white rounded-xl border p-5 cursor-pointer hover:shadow-md transition-shadow"
              style={{ borderColor: 'var(--border)' }}>
              <div className="w-10 h-10 rounded-lg flex items-center justify-center text-xl mb-3"
                style={{ backgroundColor: 'rgba(37,99,235,.08)' }}>
                {categoryIcons[c.category] || '📚'}
              </div>
              <div className="font-semibold text-sm mb-1" style={{ color: 'var(--t1)' }}>{c.title}</div>
              <div className="text-xs mb-2" style={{ color: 'var(--t3)' }}>
                {c.duration_hours}h · {c.provider || 'Internal'}
              </div>
              <div className="flex flex-wrap gap-1.5">
                <span className="px-2 py-0.5 rounded text-xs" style={{ backgroundColor: '#f5f6f8', color: 'var(--t2)' }}>
                  {c.category}
                </span>
                <span className="px-2 py-0.5 rounded text-xs" style={{ backgroundColor: '#f5f6f8', color: 'var(--t2)' }}>
                  {formatBadge[c.format] || c.format}
                </span>
                {c.is_required && (
                  <span className="px-2 py-0.5 rounded text-xs font-semibold"
                    style={{ backgroundColor: 'rgba(220,38,38,.07)', color: '#dc2626' }}>
                    Required
                  </span>
                )}
              </div>
              {c.enrollment && (
                <div className="mt-3 flex items-center gap-2">
                  <div className="flex-1 h-1.5 rounded-full" style={{ backgroundColor: '#e5e7eb' }}>
                    <div className="h-1.5 rounded-full" style={{
                      width: `${c.enrollment.total ? (c.enrollment.completed / c.enrollment.total) * 100 : 0}%`,
                      backgroundColor: 'var(--mint)',
                    }}></div>
                  </div>
                  <span className="text-xs" style={{ color: 'var(--t3)' }}>
                    {c.enrollment.completed}/{c.enrollment.total}
                  </span>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* My Learning */}
      {tab === 'learning' && (
        <div className="space-y-6">
          <div className="bg-white rounded-xl border p-6" style={{ borderColor: 'var(--border)' }}>
            <h2 className="font-semibold mb-4" style={{ color: 'var(--t1)' }}>My Active Courses</h2>
            <div className="grid grid-cols-2 gap-4">
              {assignments.filter((a: any) => a.status !== 'COMPLETED').slice(0, 6).map((a: any, i: number) => (
                <div key={i} className="bg-gray-50 rounded-lg p-4 border" style={{ borderColor: 'var(--border)' }}>
                  <div className="font-medium text-sm" style={{ color: 'var(--t1)' }}>{a.course_title}</div>
                  <div className="text-xs mt-1" style={{ color: 'var(--t3)' }}>Due: {a.due_date?.slice(0, 10)}</div>
                  <div className="flex items-center gap-2 mt-3">
                    <div className="flex-1 h-2 rounded-full" style={{ backgroundColor: '#e5e7eb' }}>
                      <div className="h-2 rounded-full" style={{
                        width: `${a.status === 'IN_PROGRESS' ? 50 : 0}%`,
                        backgroundColor: 'var(--mint)',
                      }}></div>
                    </div>
                    <span className="text-xs font-bold" style={{ color: 'var(--t2)' }}>
                      {a.status === 'IN_PROGRESS' ? '50%' : '0%'}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Auto-Enrollment Rules */}
      {tab === 'rules' && (
        <div className="space-y-3">
          {rules.map((r: any) => (
            <div key={r.id} className="bg-white rounded-xl border p-4 flex items-center gap-4"
              style={{ borderColor: 'var(--border)' }}>
              <div className="w-10 h-10 rounded-lg flex items-center justify-center"
                style={{ backgroundColor: r.is_active ? 'rgba(122,236,180,.1)' : '#f5f6f8' }}>
                <Shield size={20} style={{ color: r.is_active ? '#15803d' : 'var(--t4)' }} />
              </div>
              <div className="flex-1">
                <div className="font-semibold text-sm" style={{ color: 'var(--t1)' }}>{r.name}</div>
                <div className="text-xs mt-0.5" style={{ color: 'var(--t3)' }}>
                  {triggerLabels[r.trigger_type] || r.trigger_type?.replace(/_/g, ' ')}
                  {r.trigger_config && ` · ${r.trigger_config}`}
                </div>
              </div>
              <div className="w-10 h-5 rounded-full cursor-pointer relative transition-colors"
                style={{ backgroundColor: r.is_active ? 'var(--mint)' : '#d1d5db' }}>
                <div className="absolute top-0.5 w-4 h-4 rounded-full bg-white shadow transition-all"
                  style={{ left: r.is_active ? '22px' : '2px' }}></div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
