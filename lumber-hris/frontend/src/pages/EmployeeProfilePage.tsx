import { useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import {
  Mail, Phone, MapPin, Calendar, Briefcase, Building, Users,
  Award, Clock, FileText, ChevronLeft, Shield, AlertTriangle,
  Star, GraduationCap, FolderOpen,
} from 'lucide-react'
import api from '@/lib/api'
import type { Employee } from '@/types'

const statusColors: Record<string, string> = {
  ACTIVE: 'bg-green-100 text-green-700',
  ON_LEAVE: 'bg-yellow-100 text-yellow-700',
  SUSPENDED: 'bg-orange-100 text-orange-700',
  TERMINATED: 'bg-red-100 text-red-700',
}

const certStatusColors: Record<string, string> = {
  VALID: 'bg-green-100 text-green-700',
  EXPIRING_SOON: 'bg-yellow-100 text-yellow-700',
  EXPIRED: 'bg-red-100 text-red-700',
}

const tabs = [
  { id: 'overview', label: 'Overview', icon: FileText },
  { id: 'certs', label: 'Certifications', icon: Shield },
  { id: 'training', label: 'Training', icon: GraduationCap },
  { id: 'performance', label: 'Performance', icon: Star },
  { id: 'projects', label: 'Projects', icon: FolderOpen },
]

export default function EmployeeProfilePage() {
  const { id } = useParams<{ id: string }>()
  const [activeTab, setActiveTab] = useState('overview')

  const { data: emp, isLoading } = useQuery<Employee>({
    queryKey: ['employee', id],
    queryFn: async () => (await api.get(`/employees/${id}`)).data,
    enabled: !!id,
  })

  const { data: summary } = useQuery({
    queryKey: ['employee-summary', id],
    queryFn: async () => (await api.get(`/employees/${id}/summary`)).data,
    enabled: !!id,
  })

  const { data: history = [] } = useQuery({
    queryKey: ['employee-history', id],
    queryFn: async () => (await api.get(`/employees/${id}/history`)).data,
    enabled: !!id,
  })

  if (isLoading || !emp) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2" style={{ borderColor: 'var(--mint)' }} />
      </div>
    )
  }

  const initials = `${emp.first_name[0]}${emp.last_name[0]}`
  const tenureYears = ((Date.now() - new Date(emp.hire_date).getTime()) / (365.25 * 24 * 60 * 60 * 1000)).toFixed(1)

  return (
    <div className="space-y-4">
      <Link to="/employees" className="inline-flex items-center gap-1 text-sm hover:underline" style={{ color: 'var(--blue)' }}>
        <ChevronLeft size={16} /> Back to employees
      </Link>

      {/* Header Card */}
      <div className="bg-white rounded-xl border p-6" style={{ borderColor: 'var(--border)' }}>
        <div className="flex items-start gap-6">
          <div className="w-20 h-20 rounded-full flex items-center justify-center text-white text-2xl font-bold flex-shrink-0" style={{ backgroundColor: 'var(--blue)' }}>
            {initials}
          </div>
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-1">
              <h1 className="text-2xl font-bold" style={{ color: 'var(--t1)' }}>{emp.first_name} {emp.last_name}</h1>
              <span className={`px-2 py-0.5 rounded text-xs font-medium ${statusColors[emp.status] || ''}`}>{emp.status.replace('_', ' ')}</span>
            </div>
            <p className="text-lg mb-2" style={{ color: 'var(--t2)' }}>{emp.job_title}</p>
            <div className="flex flex-wrap items-center gap-4 text-sm" style={{ color: 'var(--t3)' }}>
              <span className="flex items-center gap-1"><Building size={14} /> {emp.department_name}</span>
              {emp.trade && <span className="flex items-center gap-1"><Briefcase size={14} /> {emp.trade}</span>}
              <span className="flex items-center gap-1"><Clock size={14} /> {tenureYears}y tenure</span>
              <span className="flex items-center gap-1"><Users size={14} /> {((emp as any).direct_reports_count || 0)} reports</span>
            </div>
            {/* Cert summary badges */}
            {summary?.cert_summary && (
              <div className="flex gap-2 mt-2">
                {summary.cert_summary.valid > 0 && <span className="px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-700">✅ {summary.cert_summary.valid} valid certs</span>}
                {summary.cert_summary.expiring > 0 && <span className="px-2 py-0.5 rounded text-xs font-medium bg-yellow-100 text-yellow-700">⚠️ {summary.cert_summary.expiring} expiring</span>}
                {summary.cert_summary.expired > 0 && <span className="px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-700">❌ {summary.cert_summary.expired} expired</span>}
              </div>
            )}
          </div>
          <div className="text-right">
            <div className="text-sm" style={{ color: 'var(--t3)' }}>Employee ID</div>
            <div className="font-mono font-medium" style={{ color: 'var(--t1)' }}>{emp.employee_number}</div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-xl border p-1 flex gap-1" style={{ borderColor: 'var(--border)' }}>
        {tabs.map((tab) => {
          const Icon = tab.icon
          return (
            <button key={tab.id} onClick={() => setActiveTab(tab.id)}
              className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors"
              style={{
                backgroundColor: activeTab === tab.id ? 'var(--mint-bg)' : 'transparent',
                color: activeTab === tab.id ? 'var(--mint2)' : 'var(--t3)',
              }}
            >
              <Icon size={16} /> {tab.label}
            </button>
          )
        })}
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <div className="space-y-4">
            {/* Contact */}
            <div className="bg-white rounded-xl border p-4" style={{ borderColor: 'var(--border)' }}>
              <h3 className="font-semibold mb-3" style={{ color: 'var(--t1)' }}>Contact</h3>
              <div className="space-y-2 text-sm">
                <div className="flex items-center gap-2"><Mail size={14} style={{ color: 'var(--t4)' }} /><a href={`mailto:${emp.email}`} style={{ color: 'var(--blue)' }}>{emp.email}</a></div>
                {emp.phone && <div className="flex items-center gap-2"><Phone size={14} style={{ color: 'var(--t4)' }} /><span style={{ color: 'var(--t2)' }}>{emp.phone}</span></div>}
                {emp.city && <div className="flex items-center gap-2"><MapPin size={14} style={{ color: 'var(--t4)' }} /><span style={{ color: 'var(--t2)' }}>{emp.city}, {emp.state}</span></div>}
              </div>
            </div>
            {/* Employment */}
            <div className="bg-white rounded-xl border p-4" style={{ borderColor: 'var(--border)' }}>
              <h3 className="font-semibold mb-3" style={{ color: 'var(--t1)' }}>Employment</h3>
              <div className="space-y-2 text-sm">
                {[
                  ['Hire Date', emp.hire_date],
                  ['Type', emp.employee_type.replace('_', ' ')],
                  ['Division', emp.division_name],
                  ['Location', emp.location_name || 'N/A'],
                  ['Reports To', emp.reports_to_name || 'N/A'],
                  ['Cost Center', emp.cost_center || 'N/A'],
                ].map(([k, v]) => (
                  <div key={k} className="flex justify-between">
                    <span style={{ color: 'var(--t3)' }}>{k}</span>
                    <span style={{ color: 'var(--t1)' }}>{v}</span>
                  </div>
                ))}
                {emp.union_name && (
                  <div className="flex justify-between">
                    <span style={{ color: 'var(--t3)' }}>Union</span>
                    <span style={{ color: 'var(--t1)' }}>{emp.union_local}</span>
                  </div>
                )}
              </div>
            </div>
          </div>
          <div className="lg:col-span-2 space-y-4">
            {/* Compensation */}
            <div className="bg-white rounded-xl border p-4" style={{ borderColor: 'var(--border)' }}>
              <h3 className="font-semibold mb-3" style={{ color: 'var(--t1)' }}>Compensation</h3>
              <div className="grid grid-cols-4 gap-4 text-sm">
                <div><div className="text-xs mb-1" style={{ color: 'var(--t3)' }}>Pay Rate</div><div className="font-medium" style={{ color: 'var(--t1)' }}>${emp.pay_rate.toLocaleString()}/{emp.pay_type === 'HOURLY' ? 'hr' : 'yr'}</div></div>
                <div><div className="text-xs mb-1" style={{ color: 'var(--t3)' }}>Pay Type</div><div style={{ color: 'var(--t1)' }}>{emp.pay_type}</div></div>
                <div><div className="text-xs mb-1" style={{ color: 'var(--t3)' }}>Bonus</div><div style={{ color: emp.bonus_eligible ? 'var(--mint2)' : 'var(--t4)' }}>{emp.bonus_eligible ? 'Yes' : 'No'}</div></div>
                <div><div className="text-xs mb-1" style={{ color: 'var(--t3)' }}>Per Diem</div><div style={{ color: (emp as any).per_diem_eligible ? 'var(--mint2)' : 'var(--t4)' }}>{(emp as any).per_diem_eligible ? 'Yes' : 'No'}</div></div>
              </div>
            </div>
            {/* Job History */}
            <div className="bg-white rounded-xl border p-4" style={{ borderColor: 'var(--border)' }}>
              <h3 className="font-semibold mb-3" style={{ color: 'var(--t1)' }}>Job History</h3>
              {history.length === 0 ? <p className="text-sm" style={{ color: 'var(--t4)' }}>No job history recorded</p> : (
                <div className="space-y-3">{history.map((h: any) => (
                  <div key={h.id} className="flex items-start gap-3 pb-3 border-b last:border-0" style={{ borderColor: 'var(--border)' }}>
                    <div className="w-2 h-2 rounded-full mt-1.5 flex-shrink-0" style={{ backgroundColor: 'var(--mint)' }} />
                    <div><div className="font-medium text-sm" style={{ color: 'var(--t1)' }}>{h.job_title}</div><div className="text-xs" style={{ color: 'var(--t3)' }}>{h.department_name} • {h.start_date} - {h.end_date || 'Present'}</div></div>
                  </div>
                ))}</div>
              )}
            </div>
          </div>
        </div>
      )}

      {activeTab === 'certs' && (
        <div className="bg-white rounded-xl border" style={{ borderColor: 'var(--border)' }}>
          <table className="w-full">
            <thead className="bg-gray-50 border-b" style={{ borderColor: 'var(--border)' }}>
              <tr>
                <th className="text-left px-4 py-3 text-sm font-medium" style={{ color: 'var(--t3)' }}>Certification</th>
                <th className="text-left px-4 py-3 text-sm font-medium" style={{ color: 'var(--t3)' }}>Expiration</th>
                <th className="text-left px-4 py-3 text-sm font-medium" style={{ color: 'var(--t3)' }}>Status</th>
              </tr>
            </thead>
            <tbody>
              {(summary?.certifications || []).map((c: any) => (
                <tr key={c.id} className="border-b" style={{ borderColor: 'var(--border)' }}>
                  <td className="px-4 py-3 text-sm font-medium" style={{ color: 'var(--t1)' }}>{c.name}</td>
                  <td className="px-4 py-3 text-sm" style={{ color: 'var(--t2)' }}>{c.expiration_date || 'N/A'}</td>
                  <td className="px-4 py-3"><span className={`px-2 py-0.5 rounded text-xs font-medium ${certStatusColors[c.status] || 'bg-gray-100'}`}>{c.status.replace('_', ' ')}</span></td>
                </tr>
              ))}
              {(!summary?.certifications?.length) && <tr><td colSpan={3} className="px-4 py-8 text-center text-sm" style={{ color: 'var(--t4)' }}>No certifications</td></tr>}
            </tbody>
          </table>
        </div>
      )}

      {activeTab === 'training' && (
        <div className="bg-white rounded-xl border" style={{ borderColor: 'var(--border)' }}>
          <table className="w-full">
            <thead className="bg-gray-50 border-b" style={{ borderColor: 'var(--border)' }}>
              <tr>
                <th className="text-left px-4 py-3 text-sm font-medium" style={{ color: 'var(--t3)' }}>Course</th>
                <th className="text-left px-4 py-3 text-sm font-medium" style={{ color: 'var(--t3)' }}>Due Date</th>
                <th className="text-left px-4 py-3 text-sm font-medium" style={{ color: 'var(--t3)' }}>Status</th>
              </tr>
            </thead>
            <tbody>
              {(summary?.training || []).map((t: any, i: number) => (
                <tr key={i} className="border-b" style={{ borderColor: 'var(--border)' }}>
                  <td className="px-4 py-3 text-sm" style={{ color: 'var(--t1)' }}>{t.course}</td>
                  <td className="px-4 py-3 text-sm" style={{ color: 'var(--t2)' }}>{t.due_date || '-'}</td>
                  <td className="px-4 py-3"><span className={`px-2 py-0.5 rounded text-xs font-medium ${t.status === 'COMPLETED' ? 'bg-green-100 text-green-700' : t.status === 'OVERDUE' ? 'bg-red-100 text-red-700' : 'bg-blue-100 text-blue-700'}`}>{t.status}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {activeTab === 'performance' && (
        <div className="space-y-4">
          {/* Reviews */}
          <div className="bg-white rounded-xl border p-4" style={{ borderColor: 'var(--border)' }}>
            <h3 className="font-semibold mb-3" style={{ color: 'var(--t1)' }}>Performance Reviews</h3>
            {(summary?.reviews || []).length === 0 ? <p className="text-sm" style={{ color: 'var(--t4)' }}>No reviews</p> : (
              <div className="space-y-2">
                {summary.reviews.map((r: any) => (
                  <div key={r.id} className="flex items-center justify-between py-2 border-b last:border-0" style={{ borderColor: 'var(--border)' }}>
                    <div><span className="font-medium text-sm" style={{ color: 'var(--t1)' }}>{r.type}</span><span className="text-xs ml-2" style={{ color: 'var(--t4)' }}>{r.period}</span></div>
                    <div className="flex items-center gap-3">
                      {r.rating && <span className="font-medium" style={{ color: 'var(--t1)' }}>{r.rating.toFixed(1)} ⭐</span>}
                      <span className={`px-2 py-0.5 rounded text-xs ${r.status === 'COMPLETED' ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'}`}>{r.status}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
          {/* Incidents & Commendations */}
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-white rounded-xl border p-4" style={{ borderColor: 'var(--border)' }}>
              <h3 className="font-semibold mb-3 flex items-center gap-2" style={{ color: 'var(--t1)' }}><AlertTriangle size={16} style={{ color: 'var(--yellow)' }} /> Incidents ({(summary?.incidents || []).length})</h3>
              {(summary?.incidents || []).map((i: any, idx: number) => (
                <div key={idx} className="text-sm py-1" style={{ color: 'var(--t2)' }}>{i.type} ({i.severity}) — {i.date}</div>
              ))}
              {!(summary?.incidents?.length) && <p className="text-sm" style={{ color: 'var(--t4)' }}>None</p>}
            </div>
            <div className="bg-white rounded-xl border p-4" style={{ borderColor: 'var(--border)' }}>
              <h3 className="font-semibold mb-3 flex items-center gap-2" style={{ color: 'var(--t1)' }}><Award size={16} style={{ color: 'var(--mint)' }} /> Commendations ({(summary?.commendations || []).length})</h3>
              {(summary?.commendations || []).map((c: any, idx: number) => (
                <div key={idx} className="text-sm py-1" style={{ color: 'var(--t2)' }}>{'⭐'.repeat(c.stars)} {c.category} — {c.description}</div>
              ))}
              {!(summary?.commendations?.length) && <p className="text-sm" style={{ color: 'var(--t4)' }}>None</p>}
            </div>
          </div>
        </div>
      )}

      {activeTab === 'projects' && (
        <div className="bg-white rounded-xl border" style={{ borderColor: 'var(--border)' }}>
          <table className="w-full">
            <thead className="bg-gray-50 border-b" style={{ borderColor: 'var(--border)' }}>
              <tr>
                <th className="text-left px-4 py-3 text-sm font-medium" style={{ color: 'var(--t3)' }}>Project</th>
                <th className="text-left px-4 py-3 text-sm font-medium" style={{ color: 'var(--t3)' }}>Role</th>
                <th className="text-left px-4 py-3 text-sm font-medium" style={{ color: 'var(--t3)' }}>Crew</th>
              </tr>
            </thead>
            <tbody>
              {(summary?.projects || []).map((p: any, i: number) => (
                <tr key={i} className="border-b" style={{ borderColor: 'var(--border)' }}>
                  <td className="px-4 py-3 text-sm font-medium" style={{ color: 'var(--t1)' }}>{p.name}</td>
                  <td className="px-4 py-3 text-sm" style={{ color: 'var(--t2)' }}>{p.role}</td>
                  <td className="px-4 py-3 text-sm" style={{ color: 'var(--t2)' }}>{p.crew || '-'}</td>
                </tr>
              ))}
              {!(summary?.projects?.length) && <tr><td colSpan={3} className="px-4 py-8 text-center text-sm" style={{ color: 'var(--t4)' }}>No project assignments</td></tr>}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
