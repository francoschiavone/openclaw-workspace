import { useState, useEffect } from 'react'
import { Shield, AlertTriangle, CheckCircle, Clock, Search, Filter, Download } from 'lucide-react'
import api from '@/lib/api'

interface CertSummary {
  total: number
  valid: number
  expiring: number
  expired: number
}

interface CertRecord {
  id: string
  employee_name: string
  certification_name: string
  issuing_body: string
  issue_date: string
  expiration_date: string | null
  status: string
  days_until_expiry?: number
}

const statusConfig: Record<string, { color: string; bg: string; label: string }> = {
  VALID: { color: '#15803d', bg: 'rgba(122,236,180,.1)', label: 'Current' },
  EXPIRING_SOON: { color: '#d97706', bg: 'rgba(217,119,6,.07)', label: 'Expiring' },
  EXPIRED: { color: '#dc2626', bg: 'rgba(220,38,38,.07)', label: 'Expired' },
  REVOKED: { color: '#6b7280', bg: '#f5f6f8', label: 'Revoked' },
}

export default function BuilderFaxPage() {
  const [certs, setCerts] = useState<CertRecord[]>([])
  const [expiring, setExpiring] = useState<CertRecord[]>([])
  const [summary, setSummary] = useState<CertSummary>({ total: 0, valid: 0, expiring: 0, expired: 0 })
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [loading, setLoading] = useState(true)
  const [tab, setTab] = useState<'all' | 'expiring' | 'compliance'>('all')

  useEffect(() => {
    Promise.all([
      api.get('/lms/certifications'),
      api.get('/lms/expiring?days=60'),
      api.get('/lms/compliance'),
    ]).then(([certsRes, expRes, compRes]) => {
      const allCerts = certsRes.data
      setCerts(allCerts)
      setExpiring(expRes.data)
      const valid = allCerts.filter((c: any) => c.status === 'VALID').length
      const expiring = allCerts.filter((c: any) => c.status === 'EXPIRING_SOON').length
      const expired = allCerts.filter((c: any) => c.status === 'EXPIRED').length
      setSummary({ total: allCerts.length, valid, expiring, expired })
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [])

  const filtered = certs.filter(c => {
    if (search && !c.employee_name?.toLowerCase().includes(search.toLowerCase()) && 
        !c.certification_name?.toLowerCase().includes(search.toLowerCase())) return false
    if (statusFilter && c.status !== statusFilter) return false
    return true
  }).slice(0, 100)

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2" style={{ borderColor: 'var(--mint)' }}></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold" style={{ color: 'var(--t1)' }}>BuilderFax — Credential Management</h1>
          <p className="text-sm mt-1" style={{ color: 'var(--t3)' }}>Track certifications, licenses, and safety credentials across your workforce</p>
        </div>
        <div className="flex gap-2">
          <button className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold border" 
            style={{ borderColor: 'var(--border2)', color: 'var(--t2)' }}>
            <Download size={16} /> Export
          </button>
          <button className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold"
            style={{ backgroundColor: 'var(--mint)', color: '#0a4023' }}>
            <Shield size={16} /> + Add Certification
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-4 gap-4">
        {[
          { label: 'Total Certifications', value: summary.total, icon: Shield, color: 'var(--t1)' },
          { label: 'Current / Valid', value: summary.valid, icon: CheckCircle, color: '#15803d' },
          { label: 'Expiring (60 days)', value: summary.expiring, icon: Clock, color: '#d97706' },
          { label: 'Expired', value: summary.expired, icon: AlertTriangle, color: '#dc2626' },
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

      {/* Tabs */}
      <div className="flex items-center gap-1 pb-3 border-b" style={{ borderColor: 'var(--border)' }}>
        {(['all', 'expiring', 'compliance'] as const).map(t => (
          <button key={t} onClick={() => setTab(t)}
            className="px-4 py-2 rounded-lg text-sm font-medium transition-colors"
            style={{
              backgroundColor: tab === t ? 'rgba(37,99,235,.08)' : 'transparent',
              color: tab === t ? 'var(--blue)' : 'var(--t3)',
              border: tab === t ? '1px solid rgba(37,99,235,.2)' : '1px solid transparent',
            }}>
            {t === 'all' ? 'All Certifications' : t === 'expiring' ? `Expiring Soon (${expiring.length})` : 'Compliance Overview'}
          </button>
        ))}
      </div>

      {tab === 'all' && (
        <>
          <div className="bg-white rounded-xl border p-4 flex items-center gap-4" style={{ borderColor: 'var(--border)' }}>
            <div className="flex-1 flex items-center gap-2 px-3 py-2 rounded-lg bg-gray-50">
              <Search size={16} style={{ color: 'var(--t4)' }} />
              <input type="text" placeholder="Search by employee or certification..." value={search}
                onChange={e => setSearch(e.target.value)}
                className="bg-transparent border-none outline-none flex-1 text-sm" style={{ color: 'var(--t1)' }} />
            </div>
            <select value={statusFilter} onChange={e => setStatusFilter(e.target.value)}
              className="px-3 py-2 border rounded-lg text-sm" style={{ borderColor: 'var(--border2)', color: 'var(--t1)' }}>
              <option value="">All Statuses</option>
              <option value="VALID">Current</option>
              <option value="EXPIRING_SOON">Expiring</option>
              <option value="EXPIRED">Expired</option>
            </select>
          </div>
          <div className="bg-white rounded-xl border overflow-hidden" style={{ borderColor: 'var(--border)' }}>
            <table className="w-full">
              <thead className="bg-gray-50 border-b" style={{ borderColor: 'var(--border)' }}>
                <tr>
                  {['Employee', 'Certification', 'Issuing Body', 'Issue Date', 'Expiration', 'Status'].map(h => (
                    <th key={h} className="text-left px-4 py-3 text-xs font-semibold uppercase tracking-wider" style={{ color: 'var(--t3)' }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {filtered.map((c, i) => {
                  const sc = statusConfig[c.status] || statusConfig.VALID
                  return (
                    <tr key={i} className="border-b hover:bg-gray-50 transition-colors" style={{ borderColor: 'var(--border)' }}>
                      <td className="px-4 py-3 text-sm font-medium" style={{ color: 'var(--t1)' }}>{c.employee_name}</td>
                      <td className="px-4 py-3 text-sm" style={{ color: 'var(--t2)' }}>{c.certification_name}</td>
                      <td className="px-4 py-3 text-sm" style={{ color: 'var(--t3)' }}>{c.issuing_body}</td>
                      <td className="px-4 py-3 text-sm" style={{ color: 'var(--t3)' }}>{c.issue_date?.slice(0, 10)}</td>
                      <td className="px-4 py-3 text-sm" style={{ color: 'var(--t3)' }}>{c.expiration_date?.slice(0, 10) || '—'}</td>
                      <td className="px-4 py-3">
                        <span className="px-2 py-1 rounded text-xs font-semibold" style={{ color: sc.color, backgroundColor: sc.bg }}>{sc.label}</span>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
            {filtered.length === 0 && (
              <div className="text-center py-8 text-sm" style={{ color: 'var(--t3)' }}>No certifications found</div>
            )}
          </div>
        </>
      )}

      {tab === 'expiring' && (
        <div className="space-y-3">
          {expiring.length === 0 ? (
            <div className="bg-white rounded-xl border p-8 text-center" style={{ borderColor: 'var(--border)' }}>
              <CheckCircle size={40} style={{ color: 'var(--mint)', margin: '0 auto 12px' }} />
              <p className="text-sm font-medium" style={{ color: 'var(--t1)' }}>No certifications expiring in the next 60 days</p>
            </div>
          ) : expiring.map((c, i) => (
            <div key={i} className="bg-white rounded-xl border p-4 flex items-center justify-between" 
              style={{ borderColor: 'var(--border)', borderLeft: '4px solid #d97706' }}>
              <div>
                <div className="font-semibold text-sm" style={{ color: 'var(--t1)' }}>{c.employee_name}</div>
                <div className="text-sm" style={{ color: 'var(--t2)' }}>{c.certification_name}</div>
                <div className="text-xs mt-1" style={{ color: 'var(--t3)' }}>Expires: {c.expiration_date?.slice(0, 10)}</div>
              </div>
              <span className="px-3 py-1 rounded-full text-xs font-bold" 
                style={{ backgroundColor: 'rgba(217,119,6,.07)', color: '#d97706', border: '1px solid rgba(217,119,6,.2)' }}>
                {c.days_until_expiry} days
              </span>
            </div>
          ))}
        </div>
      )}

      {tab === 'compliance' && (
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-white rounded-xl border p-6" style={{ borderColor: 'var(--border)' }}>
            <h3 className="font-semibold mb-4" style={{ color: 'var(--t1)' }}>Compliance Rate</h3>
            <div className="text-4xl font-bold" style={{ color: summary.expired > 0 ? '#d97706' : '#15803d' }}>
              {summary.total > 0 ? Math.round((summary.valid / summary.total) * 100) : 0}%
            </div>
            <p className="text-sm mt-2" style={{ color: 'var(--t3)' }}>{summary.valid} of {summary.total} certifications current</p>
            <div className="w-full h-3 rounded-full mt-4" style={{ backgroundColor: '#e5e7eb' }}>
              <div className="h-3 rounded-full transition-all" style={{ 
                width: `${summary.total > 0 ? (summary.valid / summary.total) * 100 : 0}%`,
                backgroundColor: 'var(--mint)' 
              }}></div>
            </div>
          </div>
          <div className="bg-white rounded-xl border p-6" style={{ borderColor: 'var(--border)' }}>
            <h3 className="font-semibold mb-4" style={{ color: 'var(--t1)' }}>Issues Summary</h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 rounded-lg" style={{ backgroundColor: 'rgba(220,38,38,.05)' }}>
                <span className="text-sm" style={{ color: 'var(--t2)' }}>Expired Certifications</span>
                <span className="font-bold text-sm" style={{ color: '#dc2626' }}>{summary.expired}</span>
              </div>
              <div className="flex items-center justify-between p-3 rounded-lg" style={{ backgroundColor: 'rgba(217,119,6,.05)' }}>
                <span className="text-sm" style={{ color: 'var(--t2)' }}>Expiring in 60 days</span>
                <span className="font-bold text-sm" style={{ color: '#d97706' }}>{summary.expiring}</span>
              </div>
              <div className="flex items-center justify-between p-3 rounded-lg" style={{ backgroundColor: 'rgba(122,236,180,.05)' }}>
                <span className="text-sm" style={{ color: 'var(--t2)' }}>Valid / Current</span>
                <span className="font-bold text-sm" style={{ color: '#15803d' }}>{summary.valid}</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
