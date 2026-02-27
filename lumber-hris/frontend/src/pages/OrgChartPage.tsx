import { useState, useEffect, useRef, useCallback } from 'react'
import { X, ZoomIn, ZoomOut, RotateCcw, Plus, Users, MapPin, Calendar, Briefcase, ChevronRight } from 'lucide-react'
import api from '@/lib/api'

interface FlatEmployee {
  id: string
  first_name: string
  last_name: string
  job_title: string
  department_name: string
  manager_id: string | null
  status: string
  hire_date: string
}

interface ProjectData {
  id: string
  name: string
  code: string
  status: string
  project_manager: string
  total_workers: number
  crews: { name: string; members: { id: string; name: string; job_title: string; trade: string; role: string }[] }[]
}

type ViewMode = 'corporate' | 'project'

interface TreeNode {
  emp: FlatEmployee
  children: TreeNode[]
  x: number
  y: number
}

const NODE_W = 220
const NODE_H = 90
const H_GAP = 30
const V_GAP = 60

function buildTree(employees: FlatEmployee[]): TreeNode[] {
  const byId = new Map<string, FlatEmployee>()
  const childrenMap = new Map<string, FlatEmployee[]>()
  
  employees.forEach(e => {
    byId.set(e.id, e)
    if (!childrenMap.has(e.id)) childrenMap.set(e.id, [])
  })
  
  employees.forEach(e => {
    if (e.manager_id && childrenMap.has(e.manager_id)) {
      childrenMap.get(e.manager_id)!.push(e)
    }
  })
  
  // Find roots (no manager or manager not in dataset)
  const roots = employees.filter(e => !e.manager_id || !byId.has(e.manager_id))
  
  function makeNode(emp: FlatEmployee, depth: number): TreeNode {
    const kids = childrenMap.get(emp.id) || []
    // Limit depth to avoid infinite recursion
    const childNodes = depth < 5 ? kids.slice(0, 12).map(k => makeNode(k, depth + 1)) : []
    return { emp, children: childNodes, x: 0, y: 0 }
  }
  
  return roots.slice(0, 6).map(r => makeNode(r, 0))
}

function layoutTree(node: TreeNode, x: number, y: number, level: number): number {
  node.y = level * (NODE_H + V_GAP)
  
  if (node.children.length === 0) {
    node.x = x
    return NODE_W + H_GAP
  }
  
  let childX = x
  let totalWidth = 0
  
  node.children.forEach(child => {
    const w = layoutTree(child, childX, 0, level + 1)
    childX += w
    totalWidth += w
  })
  
  // Center parent over children
  const firstChild = node.children[0]
  const lastChild = node.children[node.children.length - 1]
  node.x = (firstChild.x + lastChild.x) / 2
  
  return totalWidth
}

function flattenTree(node: TreeNode): TreeNode[] {
  return [node, ...node.children.flatMap(c => flattenTree(c))]
}

const statusDot = (status: string) => {
  const colors: Record<string, string> = {
    ACTIVE: '#22c55e',
    ON_LEAVE: '#eab308',
    TERMINATED: '#ef4444',
    SUSPENDED: '#f97316',
  }
  return colors[status] || '#9ca3af'
}

export default function OrgChartPage() {
  const [viewMode, setViewMode] = useState<ViewMode>('corporate')
  const [employees, setEmployees] = useState<FlatEmployee[]>([])
  const [projects, setProjects] = useState<ProjectData[]>([])
  const [selectedProject, setSelectedProject] = useState(0)
  const [selectedEmployee, setSelectedEmployee] = useState<FlatEmployee | null>(null)
  const [zoom, setZoom] = useState(0.7)
  const [pan, setPan] = useState({ x: 50, y: 50 })
  const [dragging, setDragging] = useState(false)
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 })
  const canvasRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    Promise.all([
      api.get('/org-chart/flat'),
      api.get('/org-chart/projects'),
    ]).then(([eRes, pRes]) => {
      setEmployees(eRes.data || [])
      setProjects(pRes.data || [])
    })
  }, [])

  const trees = buildTree(employees)
  let offsetX = 0
  trees.forEach(tree => {
    const w = layoutTree(tree, offsetX, 0, 0)
    offsetX += w + 80
  })
  const allNodes = trees.flatMap(t => flattenTree(t))

  // Connector lines
  const lines: { x1: number; y1: number; x2: number; y2: number }[] = []
  function collectLines(node: TreeNode) {
    node.children.forEach(child => {
      lines.push({
        x1: node.x + NODE_W / 2,
        y1: node.y + NODE_H,
        x2: child.x + NODE_W / 2,
        y2: child.y,
      })
      collectLines(child)
    })
  }
  trees.forEach(t => collectLines(t))

  const handleWheel = useCallback((e: React.WheelEvent) => {
    e.preventDefault()
    setZoom(z => Math.min(2, Math.max(0.2, z + (e.deltaY > 0 ? -0.05 : 0.05))))
  }, [])

  const handleMouseDown = (e: React.MouseEvent) => {
    if ((e.target as HTMLElement).closest('.org-node')) return
    setDragging(true)
    setDragStart({ x: e.clientX - pan.x, y: e.clientY - pan.y })
  }
  const handleMouseMove = (e: React.MouseEvent) => {
    if (!dragging) return
    setPan({ x: e.clientX - dragStart.x, y: e.clientY - dragStart.y })
  }
  const handleMouseUp = () => setDragging(false)

  const currentProject = projects[selectedProject]

  return (
    <div className="h-full flex flex-col -m-6">
      {/* Toolbar */}
      <div className="flex items-center gap-3 px-6 py-3 bg-white border-b shrink-0" style={{ borderColor: 'var(--border)' }}>
        {/* View Toggle */}
        <div className="flex items-center bg-gray-100 rounded-lg p-1">
          {(['corporate', 'project'] as const).map(v => (
            <button key={v} onClick={() => setViewMode(v)}
              className="px-3 py-1.5 rounded-md text-xs font-semibold transition-all"
              style={{
                backgroundColor: viewMode === v ? '#ffffff' : 'transparent',
                color: viewMode === v ? 'var(--t1)' : 'var(--t3)',
                boxShadow: viewMode === v ? '0 1px 3px rgba(0,0,0,.1)' : 'none',
              }}>
              {v === 'corporate' ? 'Corporate' : 'Project / Crew'}
            </button>
          ))}
        </div>

        {/* Separator */}
        <div className="w-px h-5" style={{ backgroundColor: 'var(--border)' }}></div>

        {/* Project tabs (when in project mode) */}
        {viewMode === 'project' && (
          <div className="flex items-center gap-1 flex-1 overflow-x-auto">
            {projects.map((p, i) => (
              <button key={p.id} onClick={() => setSelectedProject(i)}
                className="px-3 py-1.5 rounded-md text-xs font-medium whitespace-nowrap transition-all shrink-0"
                style={{
                  backgroundColor: i === selectedProject ? 'rgba(122,236,180,.1)' : 'transparent',
                  color: i === selectedProject ? '#15803d' : 'var(--t3)',
                  border: i === selectedProject ? '1px solid rgba(122,236,180,.25)' : '1px solid transparent',
                }}>
                🏗 {p.name}
              </button>
            ))}
          </div>
        )}

        {viewMode === 'corporate' && <div className="flex-1" />}

        {/* Legend */}
        <div className="flex items-center gap-3 text-xs" style={{ color: 'var(--t3)' }}>
          {[
            { color: '#22c55e', label: 'Active' },
            { color: '#eab308', label: 'On Leave' },
            { color: '#ef4444', label: 'Terminated' },
          ].map(l => (
            <span key={l.label} className="flex items-center gap-1">
              <span className="w-2 h-2 rounded-full" style={{ backgroundColor: l.color }}></span>
              {l.label}
            </span>
          ))}
        </div>

        <button onClick={() => { setZoom(0.7); setPan({ x: 50, y: 50 }) }}
          className="px-2.5 py-1.5 rounded-lg text-xs font-medium"
          style={{ color: 'var(--t3)', border: '1px solid var(--border)' }}>
          <RotateCcw size={14} />
        </button>

        <button className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold"
          style={{ backgroundColor: 'var(--mint)', color: '#0a4023' }}>
          <Plus size={14} /> Add Worker
        </button>
      </div>

      {/* Canvas */}
      <div className="flex-1 relative overflow-hidden cursor-grab"
        style={{ backgroundColor: '#f8f9fa' }}
        onWheel={handleWheel}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}>

        {viewMode === 'corporate' ? (
          /* Corporate Tree */
          <div ref={canvasRef}
            style={{
              transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`,
              transformOrigin: '0 0',
              position: 'relative',
              width: `${Math.max(offsetX + 200, 2000)}px`,
              height: `${(allNodes.reduce((m, n) => Math.max(m, n.y), 0) + NODE_H + 200)}px`,
              transition: dragging ? 'none' : 'transform 0.1s ease',
            }}>
            {/* SVG Connectors */}
            <svg className="absolute inset-0 pointer-events-none" 
              width="100%" height="100%" style={{ overflow: 'visible' }}>
              {lines.map((l, i) => {
                const midY = (l.y1 + l.y2) / 2
                return (
                  <path key={i}
                    d={`M${l.x1},${l.y1} C${l.x1},${midY} ${l.x2},${midY} ${l.x2},${l.y2}`}
                    fill="none" stroke="#d0d5dd" strokeWidth="1.5" />
                )
              })}
            </svg>

            {/* Nodes */}
            {allNodes.map(node => (
              <div key={node.emp.id} className="org-node absolute cursor-pointer"
                style={{ left: node.x, top: node.y, width: NODE_W }}
                onClick={() => setSelectedEmployee(node.emp)}>
                <div className="bg-white rounded-xl border shadow-sm p-3 hover:shadow-md transition-shadow"
                  style={{ borderColor: 'var(--border)' }}>
                  <div className="flex items-start gap-2">
                    <div className="w-8 h-8 rounded-full flex items-center justify-center text-white text-xs font-semibold shrink-0"
                      style={{ backgroundColor: 'var(--blue)' }}>
                      {node.emp.first_name[0]}{node.emp.last_name[0]}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-1">
                        <span className="text-xs font-semibold truncate" style={{ color: 'var(--t1)' }}>
                          {node.emp.first_name} {node.emp.last_name}
                        </span>
                        <span className="w-2 h-2 rounded-full shrink-0" style={{ backgroundColor: statusDot(node.emp.status) }}></span>
                      </div>
                      <div className="text-[11px] truncate" style={{ color: 'var(--t3)' }}>{node.emp.job_title}</div>
                    </div>
                  </div>
                  <div className="mt-2 flex items-center justify-between">
                    <span className="text-[10px] px-1.5 py-0.5 rounded" 
                      style={{ backgroundColor: 'rgba(37,99,235,.08)', color: 'var(--blue)', fontWeight: 500 }}>
                      {node.emp.department_name}
                    </span>
                    {node.children.length > 0 && (
                      <span className="text-[10px]" style={{ color: 'var(--t4)' }}>
                        {node.children.length} reports
                      </span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          /* Project/Crew View */
          <div className="p-6 overflow-auto h-full">
            {currentProject ? (
              <div className="space-y-6">
                {/* Project header */}
                <div className="bg-white rounded-xl border p-5 shadow-sm" style={{ borderColor: 'var(--border)' }}>
                  <div className="flex items-center justify-between">
                    <div>
                      <h2 className="text-lg font-bold" style={{ color: 'var(--t1)' }}>{currentProject.name}</h2>
                      <div className="text-sm mt-1" style={{ color: 'var(--t3)' }}>
                        Code: {currentProject.code} · Manager: {currentProject.project_manager} · 
                        {currentProject.total_workers} workers · {currentProject.crews.length} crews
                      </div>
                    </div>
                    <span className="px-3 py-1 rounded-full text-xs font-semibold"
                      style={{ backgroundColor: 'rgba(122,236,180,.1)', color: '#15803d', border: '1px solid rgba(122,236,180,.25)' }}>
                      {currentProject.status}
                    </span>
                  </div>
                </div>

                {/* Crews */}
                <div className="grid grid-cols-2 gap-4">
                  {currentProject.crews.map((crew, ci) => (
                    <div key={ci} className="bg-white rounded-xl border shadow-sm" style={{ borderColor: 'var(--border)' }}>
                      <div className="px-4 py-3 border-b flex items-center justify-between" style={{ borderColor: 'var(--border)' }}>
                        <span className="font-semibold text-sm" style={{ color: 'var(--t1)' }}>
                          🔧 {crew.name}
                        </span>
                        <span className="text-xs px-2 py-0.5 rounded" style={{ backgroundColor: 'var(--mint-bg)', color: '#15803d' }}>
                          {crew.members.length} members
                        </span>
                      </div>
                      <div className="divide-y" style={{ borderColor: 'var(--border)' }}>
                        {crew.members.map((m, mi) => (
                          <div key={mi} className="px-4 py-2.5 flex items-center gap-3 hover:bg-gray-50 cursor-pointer"
                            onClick={() => {
                              const emp = employees.find(e => e.id === m.id)
                              if (emp) setSelectedEmployee(emp)
                            }}>
                            <div className="w-7 h-7 rounded-full flex items-center justify-center text-white text-[10px] font-semibold shrink-0"
                              style={{ backgroundColor: m.role === 'Foreman' ? '#d97706' : 'var(--blue)' }}>
                              {m.name.split(' ').map(w => w[0]).join('')}
                            </div>
                            <div className="flex-1 min-w-0">
                              <div className="text-xs font-medium truncate" style={{ color: 'var(--t1)' }}>{m.name}</div>
                              <div className="text-[10px]" style={{ color: 'var(--t3)' }}>{m.job_title}</div>
                            </div>
                            <span className="text-[10px] px-1.5 py-0.5 rounded"
                              style={{ 
                                backgroundColor: m.role === 'Foreman' ? 'rgba(217,119,6,.07)' : '#f5f6f8',
                                color: m.role === 'Foreman' ? '#d97706' : 'var(--t3)',
                              }}>
                              {m.trade}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="flex items-center justify-center h-64 text-sm" style={{ color: 'var(--t3)' }}>
                Select a project to view crew assignments
              </div>
            )}
          </div>
        )}

        {/* Zoom controls */}
        <div className="absolute bottom-4 right-4 flex flex-col bg-white rounded-xl border shadow-md overflow-hidden"
          style={{ borderColor: 'var(--border)' }}>
          <button onClick={() => setZoom(z => Math.min(2, z + 0.1))}
            className="w-9 h-9 flex items-center justify-center hover:bg-gray-50 transition-colors"
            style={{ color: 'var(--t2)' }}>
            <ZoomIn size={16} />
          </button>
          <div className="text-[10px] text-center py-1 font-semibold border-y" 
            style={{ color: 'var(--t3)', borderColor: 'var(--border)' }}>
            {Math.round(zoom * 100)}%
          </div>
          <button onClick={() => setZoom(z => Math.max(0.2, z - 0.1))}
            className="w-9 h-9 flex items-center justify-center hover:bg-gray-50 transition-colors"
            style={{ color: 'var(--t2)' }}>
            <ZoomOut size={16} />
          </button>
        </div>

        {/* Status bar */}
        {viewMode === 'corporate' && (
          <div className="absolute bottom-4 left-1/2 -translate-x-1/2 bg-white rounded-full border shadow-md px-5 py-2 flex items-center gap-4 text-xs"
            style={{ borderColor: 'var(--border)' }}>
            <span style={{ color: 'var(--t2)' }}>
              <strong>{employees.length}</strong> employees
            </span>
            <span className="w-px h-3" style={{ backgroundColor: 'var(--border)' }}></span>
            <span style={{ color: 'var(--t2)' }}>
              <strong>{employees.filter(e => e.status === 'ACTIVE').length}</strong> active
            </span>
            <span className="w-px h-3" style={{ backgroundColor: 'var(--border)' }}></span>
            <span style={{ color: 'var(--t2)' }}>
              <strong>{projects.length}</strong> projects
            </span>
          </div>
        )}
      </div>

      {/* Detail Panel */}
      {selectedEmployee && (
        <>
          <div className="fixed inset-0 bg-black/20 z-40" onClick={() => setSelectedEmployee(null)} />
          <div className="fixed right-0 top-0 h-full w-[420px] bg-white shadow-2xl z-50 overflow-y-auto"
            style={{ animation: 'slideIn 0.2s ease' }}>
            <style>{`@keyframes slideIn { from { transform: translateX(100%); } to { transform: translateX(0); } }`}</style>
            <div className="sticky top-0 bg-white border-b px-6 py-4 flex items-center justify-between z-10" style={{ borderColor: 'var(--border)' }}>
              <h3 className="font-bold" style={{ color: 'var(--t1)' }}>Employee Details</h3>
              <button onClick={() => setSelectedEmployee(null)}
                className="w-8 h-8 rounded-lg flex items-center justify-center hover:bg-gray-100" style={{ color: 'var(--t3)' }}>
                <X size={18} />
              </button>
            </div>
            <div className="p-6 space-y-6">
              <div className="flex items-center gap-4">
                <div className="w-14 h-14 rounded-full flex items-center justify-center text-white text-lg font-bold"
                  style={{ backgroundColor: 'var(--blue)' }}>
                  {selectedEmployee.first_name[0]}{selectedEmployee.last_name[0]}
                </div>
                <div>
                  <div className="font-bold text-lg" style={{ color: 'var(--t1)' }}>
                    {selectedEmployee.first_name} {selectedEmployee.last_name}
                  </div>
                  <div className="text-sm" style={{ color: 'var(--t3)' }}>{selectedEmployee.job_title}</div>
                  <div className="text-xs mt-0.5" style={{ color: 'var(--t4)' }}>{selectedEmployee.department_name}</div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                {[
                  { icon: Calendar, label: 'Hire Date', value: selectedEmployee.hire_date?.slice(0, 10) },
                  { icon: Briefcase, label: 'Status', value: selectedEmployee.status?.replace(/_/g, ' ') },
                  { icon: MapPin, label: 'Department', value: selectedEmployee.department_name },
                  { icon: Users, label: 'ID', value: selectedEmployee.id.slice(0, 8) + '...' },
                ].map((f, i) => (
                  <div key={i} className="p-3 rounded-lg" style={{ backgroundColor: '#f8f9fa', border: '1px solid var(--border)' }}>
                    <div className="flex items-center gap-1.5 mb-1">
                      <f.icon size={12} style={{ color: 'var(--t4)' }} />
                      <span className="text-[10px] uppercase tracking-wider" style={{ color: 'var(--t4)' }}>{f.label}</span>
                    </div>
                    <div className="text-sm font-medium" style={{ color: 'var(--t1)' }}>{f.value}</div>
                  </div>
                ))}
              </div>

              <div className="space-y-2">
                <button className="w-full flex items-center justify-between px-4 py-3 rounded-lg border hover:bg-gray-50 transition-colors"
                  style={{ borderColor: 'var(--border)' }}>
                  <span className="text-sm font-medium" style={{ color: 'var(--blue)' }}>View Full Profile</span>
                  <ChevronRight size={16} style={{ color: 'var(--t3)' }} />
                </button>
                <button className="w-full flex items-center justify-between px-4 py-3 rounded-lg border hover:bg-gray-50 transition-colors"
                  style={{ borderColor: 'var(--border)' }}>
                  <span className="text-sm font-medium" style={{ color: 'var(--t2)' }}>Reassign</span>
                  <ChevronRight size={16} style={{ color: 'var(--t3)' }} />
                </button>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
