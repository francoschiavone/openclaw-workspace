import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import {
  Search, Filter, ChevronLeft, ChevronRight, Eye, Edit,
} from 'lucide-react'
import api from '@/lib/api'
import type { EmployeeListResponse, Employee, Department } from '@/types'

const statusColors: Record<string, string> = {
  ACTIVE: 'bg-green-100 text-green-700',
  ON_LEAVE: 'bg-yellow-100 text-yellow-700',
  SUSPENDED: 'bg-orange-100 text-orange-700',
  TERMINATED: 'bg-red-100 text-red-700',
}

export default function EmployeesPage() {
  const navigate = useNavigate()
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [debouncedSearch, setDebouncedSearch] = useState('')
  const [filters, setFilters] = useState({
    department_id: '',
    status: '',
    employee_type: '',
  })
  const [showFilters, setShowFilters] = useState(false)

  // Debounce search
  const handleSearch = (value: string) => {
    setSearch(value)
    setTimeout(() => setDebouncedSearch(value), 300)
  }

  const { data, isLoading } = useQuery<EmployeeListResponse>({
    queryKey: ['employees', page, debouncedSearch, filters],
    queryFn: async () => {
      const params = new URLSearchParams()
      params.set('page', String(page))
      params.set('per_page', '25')
      if (debouncedSearch) params.set('search', debouncedSearch)
      if (filters.department_id) params.set('department_id', filters.department_id)
      if (filters.status) params.set('status', filters.status)
      if (filters.employee_type) params.set('employee_type', filters.employee_type)
      const { data } = await api.get(`/employees?${params}`)
      return data
    },
  })

  const { data: departments = [] } = useQuery<Department[]>({
    queryKey: ['departments'],
    queryFn: async () => {
      const { data } = await api.get('/departments')
      return data
    },
  })

  const employees = data?.items || []
  const total = data?.total || 0
  const totalPages = Math.ceil(total / 25)

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold" style={{ color: 'var(--t1)' }}>Employees</h1>
          <p className="text-sm" style={{ color: 'var(--t3)' }}>{total} total</p>
        </div>
      </div>

      {/* Search and Filter Bar */}
      <div className="bg-white rounded-xl border p-4 flex items-center gap-4" style={{ borderColor: 'var(--border)' }}>
        <div className="flex-1 flex items-center gap-2 px-3 py-2 rounded-lg bg-gray-50">
          <Search size={18} style={{ color: 'var(--t4)' }} />
          <input
            type="text"
            placeholder="Search by name, email, ID..."
            value={search}
            onChange={(e) => handleSearch(e.target.value)}
            className="bg-transparent border-none outline-none flex-1 text-sm"
            style={{ color: 'var(--t1)' }}
          />
        </div>
        <button
          onClick={() => setShowFilters(!showFilters)}
          className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
            showFilters ? 'bg-gray-100' : ''
          }`}
          style={{ color: 'var(--t2)' }}
        >
          <Filter size={16} />
          Filters
        </button>
      </div>

      {/* Filters Panel */}
      {showFilters && (
        <div className="bg-white rounded-xl border p-4 flex flex-wrap gap-4" style={{ borderColor: 'var(--border)' }}>
          <select
            value={filters.status}
            onChange={(e) => setFilters({ ...filters, status: e.target.value })}
            className="px-3 py-2 border rounded-lg text-sm"
            style={{ borderColor: 'var(--border)', color: 'var(--t1)' }}
          >
            <option value="">All Statuses</option>
            <option value="ACTIVE">Active</option>
            <option value="ON_LEAVE">On Leave</option>
            <option value="SUSPENDED">Suspended</option>
            <option value="TERMINATED">Terminated</option>
          </select>
          <select
            value={filters.department_id}
            onChange={(e) => setFilters({ ...filters, department_id: e.target.value })}
            className="px-3 py-2 border rounded-lg text-sm"
            style={{ borderColor: 'var(--border)', color: 'var(--t1)' }}
          >
            <option value="">All Departments</option>
            {departments.map((d) => (
              <option key={d.id} value={d.id}>{d.name}</option>
            ))}
          </select>
          <select
            value={filters.employee_type}
            onChange={(e) => setFilters({ ...filters, employee_type: e.target.value })}
            className="px-3 py-2 border rounded-lg text-sm"
            style={{ borderColor: 'var(--border)', color: 'var(--t1)' }}
          >
            <option value="">All Types</option>
            <option value="FULL_TIME">Full Time</option>
            <option value="PART_TIME">Part Time</option>
            <option value="CONTRACTOR">Contractor</option>
            <option value="CASUAL">Casual</option>
          </select>
          <button
            onClick={() => setFilters({ department_id: '', status: '', employee_type: '' })}
            className="text-sm"
            style={{ color: 'var(--blue)' }}
          >
            Clear filters
          </button>
        </div>
      )}

      {/* Table */}
      <div className="bg-white rounded-xl border overflow-hidden" style={{ borderColor: 'var(--border)' }}>
        <table className="w-full">
          <thead className="bg-gray-50 border-b" style={{ borderColor: 'var(--border)' }}>
            <tr>
              <th className="text-left px-4 py-3 text-sm font-medium" style={{ color: 'var(--t3)' }}>Employee</th>
              <th className="text-left px-4 py-3 text-sm font-medium" style={{ color: 'var(--t3)' }}>ID</th>
              <th className="text-left px-4 py-3 text-sm font-medium" style={{ color: 'var(--t3)' }}>Department</th>
              <th className="text-left px-4 py-3 text-sm font-medium" style={{ color: 'var(--t3)' }}>Job Title</th>
              <th className="text-left px-4 py-3 text-sm font-medium" style={{ color: 'var(--t3)' }}>Trade</th>
              <th className="text-left px-4 py-3 text-sm font-medium" style={{ color: 'var(--t3)' }}>Status</th>
              <th className="text-right px-4 py-3 text-sm font-medium" style={{ color: 'var(--t3)' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {isLoading ? (
              <tr>
                <td colSpan={7} className="text-center py-8" style={{ color: 'var(--t3)' }}>
                  Loading...
                </td>
              </tr>
            ) : employees.length === 0 ? (
              <tr>
                <td colSpan={7} className="text-center py-8" style={{ color: 'var(--t3)' }}>
                  No employees found
                </td>
              </tr>
            ) : (
              employees.map((emp) => (
                <tr
                  key={emp.id}
                  className="border-b hover:bg-gray-50 cursor-pointer transition-colors"
                  style={{ borderColor: 'var(--border)' }}
                  onClick={() => navigate(`/employees/${emp.id}`)}
                >
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-3">
                      <div
                        className="w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-medium"
                        style={{ backgroundColor: 'var(--blue)' }}
                      >
                        {emp.first_name[0]}{emp.last_name[0]}
                      </div>
                      <div>
                        <div className="font-medium text-sm" style={{ color: 'var(--t1)' }}>
                          {emp.first_name} {emp.last_name}
                        </div>
                        <div className="text-xs" style={{ color: 'var(--t4)' }}>{emp.email}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-sm" style={{ color: 'var(--t2)' }}>
                    {emp.employee_number}
                  </td>
                  <td className="px-4 py-3 text-sm" style={{ color: 'var(--t2)' }}>
                    {emp.department_name}
                  </td>
                  <td className="px-4 py-3 text-sm" style={{ color: 'var(--t2)' }}>
                    {emp.job_title}
                  </td>
                  <td className="px-4 py-3 text-sm" style={{ color: 'var(--t2)' }}>
                    {emp.trade || '-'}
                  </td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${statusColors[emp.status] || ''}`}>
                      {emp.status.replace('_', ' ')}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right">
                    <div className="flex items-center justify-end gap-2">
                      <button
                        onClick={(e) => { e.stopPropagation(); navigate(`/employees/${emp.id}`) }}
                        className="p-1.5 rounded hover:bg-gray-100"
                        title="View"
                      >
                        <Eye size={16} style={{ color: 'var(--t3)' }} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between bg-white rounded-xl border p-4" style={{ borderColor: 'var(--border)' }}>
          <span className="text-sm" style={{ color: 'var(--t3)' }}>
            Page {page} of {totalPages}
          </span>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setPage(Math.max(1, page - 1))}
              disabled={page === 1}
              className="p-2 rounded-lg disabled:opacity-50 hover:bg-gray-100"
            >
              <ChevronLeft size={18} />
            </button>
            <button
              onClick={() => setPage(Math.min(totalPages, page + 1))}
              disabled={page === totalPages}
              className="p-2 rounded-lg disabled:opacity-50 hover:bg-gray-100"
            >
              <ChevronRight size={18} />
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
