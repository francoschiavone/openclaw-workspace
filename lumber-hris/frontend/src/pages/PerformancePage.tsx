import { useState, useEffect } from 'react'
import { Star, Target, AlertTriangle, Award, BarChart3 } from 'lucide-react'
import api from '@/lib/api'

type Tab = 'reviews' | 'goals' | 'incidents' | 'calibration'

const pill = (status: string) => {
  const m: Record<string, { bg: string; c: string }> = {
    COMPLETED: { bg: 'rgba(122,236,180,.1)', c: '#15803d' },
    IN_PROGRESS: { bg: 'rgba(37,99,235,.08)', c: '#2563eb' },
    DRAFT: { bg: '#f5f6f8', c: '#6b7280' },
    SELF_REVIEW: { bg: 'rgba(37,99,235,.08)', c: '#2563eb' },
    MANAGER_REVIEW: { bg: 'rgba(217,119,6,.07)', c: '#d97706' },
    PENDING_SIGN_OFF: { bg: 'rgba(217,119,6,.07)', c: '#d97706' },
    ACTIVE: { bg: 'rgba(37,99,235,.08)', c: '#2563eb' },
    AT_RISK: { bg: 'rgba(220,38,38,.07)', c: '#dc2626' },
    NOT_STARTED: { bg: '#f5f6f8', c: '#6b7280' },
    OPEN: { bg: 'rgba(220,38,38,.07)', c: '#dc2626' },
    INVESTIGATING: { bg: 'rgba(217,119,6,.07)', c: '#d97706' },
    RESOLVED: { bg: 'rgba(122,236,180,.1)', c: '#15803d' },
    CLOSED: { bg: '#f5f6f8', c: '#6b7280' },
  }
  const s = m[status] || { bg: '#f5f6f8', c: '#6b7280' }
  return <span className="px-2 py-0.5 rounded text-xs font-semibold" style={{ backgroundColor: s.bg, color: s.c }}>{(status || '').replace(/_/g, ' ')}</span>
}

const Stars = ({ rating }: { rating: number }) => (
  <div className="flex gap-0.5">
    {[1, 2, 3, 4, 5].map(i => (
      <Star key={i} size={14} fill={i <= rating ? '#f59e0b' : 'none'} style={{ color: i <= rating ? '#f59e0b' : '#d1d5db' }} />
    ))}
  </div>
)

const sevMap: Record<string, { bg: string; c: string }> = {
  CRITICAL: { bg: 'rgba(220,38,38,.07)', c: '#dc2626' },
  MAJOR: { bg: 'rgba(217,119,6,.07)', c: '#d97706' },
  MODERATE: { bg: 'rgba(37,99,235,.08)', c: '#2563eb' },
  MINOR: { bg: '#f5f6f8', c: '#6b7280' },
}

export default function PerformancePage() {
  const [tab, setTab] = useState<Tab>('reviews')
  const [reviews, setReviews] = useState<any[]>([])
  const [cycles, setCycles] = useState<any[]>([])
  const [goals, setGoals] = useState<any[]>([])
  const [incidents, setIncidents] = useState<any[]>([])
  const [commendations, setCommendations] = useState<any[]>([])
  const [nineBox, setNineBox] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      api.get('/performance/reviews'),
      api.get('/performance/cycles'),
      api.get('/performance/goals'),
      api.get('/performance/incidents'),
      api.get('/performance/commendations'),
      api.get('/performance/calibration/nine-box').catch(() => ({ data: null })),
    ]).then(([rR, cR, gR, iR, coR, nbR]) => {
      setReviews(rR.data || [])
      setCycles(cR.data || [])
      setGoals(gR.data || [])
      setIncidents(iR.data || [])
      setCommendations(coR.data || [])
      setNineBox(nbR.data)
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [])

  const tabs: { key: Tab; label: string; icon: any }[] = [
    { key: 'reviews', label: 'Reviews', icon: Star },
    { key: 'goals', label: 'Goals', icon: Target },
    { key: 'incidents', label: 'Incidents & Recognition', icon: AlertTriangle },
    { key: 'calibration', label: 'Calibration', icon: BarChart3 },
  ]

  if (loading) return <div className="flex items-center justify-center h-64"><div className="animate-spin rounded-full h-8 w-8 border-b-2" style={{ borderColor: 'var(--mint)' }}></div></div>

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold" style={{ color: 'var(--t1)' }}>Performance Management</h1>
        <p className="text-sm mt-1" style={{ color: 'var(--t3)' }}>Reviews, goals, incidents, and calibration</p>
      </div>

      <div className="flex items-center gap-1 pb-3 border-b" style={{ borderColor: 'var(--border)' }}>
        {tabs.map(t => (
          <button key={t.key} onClick={() => setTab(t.key)}
            className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors"
            style={{
              backgroundColor: tab === t.key ? 'rgba(37,99,235,.08)' : 'transparent',
              color: tab === t.key ? 'var(--blue)' : 'var(--t3)',
              border: tab === t.key ? '1px solid rgba(37,99,235,.2)' : '1px solid transparent',
            }}>
            <t.icon size={15} />{t.label}
          </button>
        ))}
      </div>

      {tab === 'reviews' && (
        <div className="space-y-6">
          <div>
            <h2 className="font-semibold mb-3" style={{ color: 'var(--t1)' }}>Active Review Cycles</h2>
            <div className="grid grid-cols-2 gap-4">
              {cycles.map((c: any) => (
                <div key={c.id} className="bg-white rounded-xl border p-5" style={{ borderColor: 'var(--border)' }}>
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <div className="font-semibold" style={{ color: 'var(--t1)' }}>{c.name}</div>
                      <div className="text-xs mt-1" style={{ color: 'var(--t3)' }}>
                        {c.period_start?.slice(0, 10)} → {c.period_end?.slice(0, 10)}
                      </div>
                    </div>
                    <div className="flex gap-2">
                      {pill(c.status)}
                      <span className="px-2 py-0.5 rounded text-xs font-medium" style={{ backgroundColor: '#f5f6f8', color: 'var(--t2)' }}>
                        {c.type}
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="flex-1 h-2 rounded-full" style={{ backgroundColor: '#e5e7eb' }}>
                      <div className="h-2 rounded-full" style={{ width: `${c.progress || 0}%`, backgroundColor: 'var(--mint)' }}></div>
                    </div>
                    <span className="text-xs font-bold" style={{ color: 'var(--t2)' }}>{c.completed_reviews}/{c.total_reviews}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white rounded-xl border overflow-hidden" style={{ borderColor: 'var(--border)' }}>
            <div className="px-5 py-4 border-b" style={{ borderColor: 'var(--border)' }}>
              <span className="font-semibold" style={{ color: 'var(--t1)' }}>Recent Reviews ({reviews.length})</span>
            </div>
            <table className="w-full">
              <thead className="bg-gray-50 border-b" style={{ borderColor: 'var(--border)' }}>
                <tr>
                  {['Employee', 'Reviewer', 'Type', 'Rating', 'Status', 'Due Date'].map(h => (
                    <th key={h} className="text-left px-4 py-3 text-xs font-semibold uppercase tracking-wider" style={{ color: 'var(--t3)' }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {reviews.slice(0, 20).map((r: any) => (
                  <tr key={r.id} className="border-b hover:bg-gray-50" style={{ borderColor: 'var(--border)' }}>
                    <td className="px-4 py-3 text-sm font-medium" style={{ color: 'var(--t1)' }}>{r.employee_name}</td>
                    <td className="px-4 py-3 text-sm" style={{ color: 'var(--t2)' }}>{r.reviewer_name}</td>
                    <td className="px-4 py-3 text-sm" style={{ color: 'var(--t3)' }}>{(r.type || '').replace(/_/g, ' ')}</td>
                    <td className="px-4 py-3"><Stars rating={r.overall_rating || 0} /></td>
                    <td className="px-4 py-3">{pill(r.status)}</td>
                    <td className="px-4 py-3 text-sm" style={{ color: 'var(--t3)' }}>{(r.due_date || r.created_at || '').slice(0, 10)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {tab === 'goals' && (
        <div className="grid grid-cols-3 gap-4">
          {goals.map((g: any) => (
            <div key={g.id} className="bg-white rounded-xl border p-5" style={{ borderColor: 'var(--border)' }}>
              <div className="flex items-start justify-between mb-2">
                <div className="font-semibold text-sm" style={{ color: 'var(--t1)' }}>{g.title}</div>
                {pill(g.status)}
              </div>
              <div className="text-xs mb-3" style={{ color: 'var(--t3)' }}>{g.employee_name} · Due: {g.target_date?.slice(0, 10)}</div>
              <div className="flex items-center gap-2">
                <div className="flex-1 h-2 rounded-full" style={{ backgroundColor: '#e5e7eb' }}>
                  <div className="h-2 rounded-full" style={{ width: `${g.percent_complete || 0}%`, backgroundColor: 'var(--mint)' }}></div>
                </div>
                <span className="text-xs font-bold" style={{ color: 'var(--t2)' }}>{g.percent_complete || 0}%</span>
              </div>
            </div>
          ))}
          {goals.length === 0 && <div className="col-span-3 text-center py-8 text-sm" style={{ color: 'var(--t3)' }}>No goals found</div>}
        </div>
      )}

      {tab === 'incidents' && (
        <div className="grid grid-cols-2 gap-6">
          <div>
            <h2 className="font-semibold mb-3 flex items-center gap-2" style={{ color: 'var(--t1)' }}>
              <AlertTriangle size={16} style={{ color: '#dc2626' }} /> Incidents ({incidents.length})
            </h2>
            <div className="space-y-3">
              {incidents.map((inc: any) => {
                const sv = sevMap[inc.severity] || sevMap.MINOR
                return (
                  <div key={inc.id} className="bg-white rounded-xl border p-4" style={{ borderColor: 'var(--border)', borderLeft: '4px solid #dc2626' }}>
                    <div className="flex items-start justify-between mb-2">
                      <div className="font-semibold text-sm" style={{ color: 'var(--t1)' }}>{inc.employee_name}</div>
                      <span className="px-2 py-0.5 rounded text-xs font-semibold" style={{ backgroundColor: sv.bg, color: sv.c }}>{inc.severity}</span>
                    </div>
                    <div className="text-xs mb-1" style={{ color: 'var(--t3)' }}>{inc.type} · {inc.incident_date?.slice(0, 10)}</div>
                    <p className="text-xs line-clamp-2" style={{ color: 'var(--t2)' }}>{inc.description}</p>
                    <div className="mt-2">{pill(inc.status)}</div>
                  </div>
                )
              })}
            </div>
          </div>
          <div>
            <h2 className="font-semibold mb-3 flex items-center gap-2" style={{ color: 'var(--t1)' }}>
              <Award size={16} style={{ color: '#15803d' }} /> Commendations ({commendations.length})
            </h2>
            <div className="space-y-3">
              {commendations.map((c: any) => (
                <div key={c.id} className="bg-white rounded-xl border p-4" style={{ borderColor: 'var(--border)', borderLeft: '4px solid var(--mint)' }}>
                  <div className="font-semibold text-sm mb-1" style={{ color: 'var(--t1)' }}>{c.employee_name}</div>
                  <div className="text-xs mb-1" style={{ color: 'var(--t3)' }}>
                    {c.category?.replace(/_/g, ' ')} · By: {c.awarded_by_name || c.awarded_by} · {c.created_at?.slice(0, 10)}
                  </div>
                  <p className="text-xs line-clamp-2" style={{ color: 'var(--t2)' }}>{c.description}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {tab === 'calibration' && (
        <div>
          <h2 className="font-semibold mb-4" style={{ color: 'var(--t1)' }}>9-Box Calibration Grid</h2>
          {nineBox && nineBox.grid ? (
            <div className="bg-white rounded-xl border p-6" style={{ borderColor: 'var(--border)' }}>
              <div className="grid grid-cols-3 gap-3">
                {['High', 'Medium', 'Low'].map((pot, pi) =>
                  ['Low', 'Medium', 'High'].map((perf, pei) => {
                    const cell = nineBox.grid?.[pi]?.[pei]
                    const bg = (pi === 0 && pei === 2) ? 'rgba(122,236,180,.15)' :
                      (pi === 2 && pei === 0) ? 'rgba(220,38,38,.06)' : 'rgba(37,99,235,.04)'
                    return (
                      <div key={`${pi}-${pei}`} className="rounded-lg p-3 min-h-[90px]" style={{ backgroundColor: bg, border: '1px solid var(--border)' }}>
                        <div className="text-[10px] font-semibold mb-1" style={{ color: 'var(--t4)' }}>{pot} Pot · {perf} Perf</div>
                        <div className="text-xl font-bold" style={{ color: 'var(--t1)' }}>{cell?.count || 0}</div>
                        {cell?.employees?.slice(0, 2).map((e: any, i: number) => (
                          <div key={i} className="text-[10px] truncate" style={{ color: 'var(--t2)' }}>{e.name}</div>
                        ))}
                      </div>
                    )
                  })
                ).flat()}
              </div>
            </div>
          ) : (
            <div className="bg-white rounded-xl border p-8 text-center" style={{ borderColor: 'var(--border)' }}>
              <BarChart3 size={40} style={{ color: 'var(--t4)', margin: '0 auto 12px' }} />
              <p className="text-sm" style={{ color: 'var(--t3)' }}>Calibration data will be available after review cycles are completed</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
