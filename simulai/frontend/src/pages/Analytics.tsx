import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  Brain, 
  TrendingUp, 
  AlertTriangle, 
  Lightbulb, 
  Calendar,
  ArrowRight,
  Clock,
  Wrench,
  CheckCircle,
  AlertCircle,
  Info,
  ChevronRight,
  Filter
} from 'lucide-react';
import { 
  LineChart, 
  Line, 
  AreaChart, 
  Area, 
  BarChart, 
  Bar,
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Legend
} from 'recharts';
import { analyticsApi } from '../services/api';
import { mockInsights, mockMaintenanceSchedule, generateTimeSeriesData, mockTwins } from '../data/mockData';
import { AnalyticsInsight, MaintenanceSchedule } from '../types';
import { StatusBadge } from '../components/StatusBadge';

type InsightFilter = 'all' | 'prediction' | 'anomaly' | 'recommendation' | 'trend';

export function Analytics() {
  const [insights, setInsights] = useState<AnalyticsInsight[]>([]);
  const [maintenance, setMaintenance] = useState<MaintenanceSchedule[]>([]);
  const [loading, setLoading] = useState(true);
  const [insightFilter, setInsightFilter] = useState<InsightFilter>('all');
  
  // Chart data
  const [efficiencyData] = useState(() => 
    generateTimeSeriesData(24, 85, 8).map((d, i) => ({
      ...d,
      oee: d.value,
      availability: d.value - Math.random() * 5,
      performance: d.value - Math.random() * 8,
      quality: d.value + Math.random() * 3,
    }))
  );
  
  const [energyData] = useState(() => 
    generateTimeSeriesData(24, 2.4, 0.3).map((d, i) => ({
      ...d,
      consumption: d.value,
      predicted: d.value + (Math.random() - 0.5) * 0.2,
    }))
  );

  const [downtimeData] = useState([
    { name: 'Assembly A', value: 4 },
    { name: 'CNC #12', value: 8 },
    { name: 'HVAC', value: 12 },
    { name: 'Packaging', value: 2 },
    { name: 'AGV Fleet', value: 3 },
  ]);

  const [performanceRadar] = useState([
    { metric: 'Efficiency', value: 92 },
    { metric: 'Quality', value: 97 },
    { metric: 'Speed', value: 88 },
    { metric: 'Reliability', value: 94 },
    { metric: 'Safety', value: 99 },
    { metric: 'Maintenance', value: 85 },
  ]);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [insightsData, maintenanceData] = await Promise.all([
        analyticsApi.getInsights(),
        analyticsApi.getMaintenanceSchedule(),
      ]);
      setInsights(insightsData);
      setMaintenance(maintenanceData);
    } catch (error) {
      console.error('Failed to load analytics:', error);
      setInsights(mockInsights);
      setMaintenance(mockMaintenanceSchedule);
    } finally {
      setLoading(false);
    }
  };

  const filteredInsights = insights.filter(insight => 
    insightFilter === 'all' || insight.type === insightFilter
  );

  const insightTypeConfig = {
    prediction: { icon: Brain, color: 'text-accent-purple', bg: 'bg-accent-purple/10', border: 'border-accent-purple/20' },
    anomaly: { icon: AlertTriangle, color: 'text-accent-orange', bg: 'bg-accent-orange/10', border: 'border-accent-orange/20' },
    recommendation: { icon: Lightbulb, color: 'text-accent-cyan', bg: 'bg-accent-cyan/10', border: 'border-accent-cyan/20' },
    trend: { icon: TrendingUp, color: 'text-accent-green', bg: 'bg-accent-green/10', border: 'border-accent-green/20' },
  };

  const maintenancePriorityColors = {
    high: 'text-accent-red bg-accent-red/10',
    medium: 'text-accent-orange bg-accent-orange/10',
    low: 'text-accent-green bg-accent-green/10',
  };

  return (
    <div className="space-y-6 fade-in">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        <div>
          <h1 className="text-2xl lg:text-3xl font-bold text-white">Analytics & Insights</h1>
          <p className="text-gray-400 mt-1">AI-powered analysis and predictions for your digital twins</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 px-4 py-2 bg-surface-800/50 rounded-lg border border-surface-700/50">
            <Brain size={16} className="text-accent-purple" />
            <span className="text-sm text-gray-400">AI Analysis Active</span>
            <span className="w-2 h-2 rounded-full bg-accent-green animate-pulse"></span>
          </div>
        </div>
      </div>

      {/* AI Insights Section */}
      <div className="card">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-accent-purple/10">
              <Brain size={20} className="text-accent-purple" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-white">AI Insights</h3>
              <p className="text-sm text-gray-500">Machine learning powered predictions and recommendations</p>
            </div>
          </div>
          
          {/* Filter Pills */}
          <div className="flex flex-wrap gap-2">
            {(['all', 'prediction', 'anomaly', 'recommendation', 'trend'] as InsightFilter[]).map((filter) => (
              <button
                key={filter}
                onClick={() => setInsightFilter(filter)}
                className={`
                  px-3 py-1.5 rounded-lg text-sm font-medium transition-colors capitalize
                  ${insightFilter === filter 
                    ? 'bg-primary-500/20 text-primary-400 border border-primary-500/30' 
                    : 'bg-surface-800 text-gray-400 hover:text-white border border-surface-700'
                  }
                `}
              >
                {filter}
              </button>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {loading ? (
            [...Array(4)].map((_, i) => (
              <div key={i} className="skeleton h-32 rounded-lg"></div>
            ))
          ) : filteredInsights.length === 0 ? (
            <div className="col-span-2 text-center py-8 text-gray-500">
              No insights match the selected filter
            </div>
          ) : (
            filteredInsights.map((insight) => {
              const config = insightTypeConfig[insight.type];
              const Icon = config.icon;
              
              return (
                <div 
                  key={insight.id}
                  className={`
                    p-4 rounded-xl border transition-all hover:shadow-lg
                    ${config.bg} ${config.border}
                  `}
                >
                  <div className="flex items-start gap-3">
                    <div className={`p-2 rounded-lg ${config.bg}`}>
                      <Icon size={18} className={config.color} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between gap-2">
                        <h4 className="font-medium text-white">{insight.title}</h4>
                        <span className={`
                          text-xs font-medium px-2 py-0.5 rounded-full
                          ${insight.impact === 'high' ? 'bg-accent-red/20 text-accent-red' : ''}
                          ${insight.impact === 'medium' ? 'bg-accent-orange/20 text-accent-orange' : ''}
                          ${insight.impact === 'low' ? 'bg-accent-green/20 text-accent-green' : ''}
                        `}>
                          {insight.impact} impact
                        </span>
                      </div>
                      <p className="text-sm text-gray-400 mt-1">{insight.description}</p>
                      <div className="flex items-center gap-4 mt-3">
                        {insight.twinName && (
                          <Link 
                            to={`/twins/${insight.twinId}`}
                            className="text-sm text-primary-400 hover:text-primary-300 flex items-center gap-1"
                          >
                            {insight.twinName} <ArrowRight size={12} />
                          </Link>
                        )}
                        <span className="text-xs text-gray-500">
                          Confidence: {insight.confidence}%
                        </span>
                        <span className="text-xs text-gray-600">
                          {new Date(insight.createdAt).toLocaleString()}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* OEE Over Time */}
        <div className="card card-hover">
          <div className="mb-4">
            <h3 className="text-lg font-semibold text-white">Overall Equipment Effectiveness</h3>
            <p className="text-sm text-gray-500">Last 24 hours breakdown</p>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={efficiencyData}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis 
                  dataKey="timestamp" 
                  tick={{ fill: '#64748b', fontSize: 10 }}
                  tickFormatter={(v) => new Date(v).toLocaleTimeString([], { hour: '2-digit' })}
                />
                <YAxis domain={[70, 100]} tick={{ fill: '#64748b', fontSize: 10 }} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1e2228', border: '1px solid #334155', borderRadius: '8px' }}
                  labelFormatter={(v) => new Date(v).toLocaleTimeString()}
                />
                <Legend />
                <Line type="monotone" dataKey="oee" stroke="#00d4ff" strokeWidth={2} dot={false} name="OEE" />
                <Line type="monotone" dataKey="availability" stroke="#00ff88" strokeWidth={2} dot={false} name="Availability" />
                <Line type="monotone" dataKey="performance" stroke="#a855f7" strokeWidth={2} dot={false} name="Performance" />
                <Line type="monotone" dataKey="quality" stroke="#ff9500" strokeWidth={2} dot={false} name="Quality" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Energy Consumption */}
        <div className="card card-hover">
          <div className="mb-4">
            <h3 className="text-lg font-semibold text-white">Energy Consumption</h3>
            <p className="text-sm text-gray-500">Actual vs Predicted (AI Forecast)</p>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={energyData}>
                <defs>
                  <linearGradient id="energyGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#00d4ff" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#00d4ff" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis 
                  dataKey="timestamp" 
                  tick={{ fill: '#64748b', fontSize: 10 }}
                  tickFormatter={(v) => new Date(v).toLocaleTimeString([], { hour: '2-digit' })}
                />
                <YAxis tick={{ fill: '#64748b', fontSize: 10 }} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1e2228', border: '1px solid #334155', borderRadius: '8px' }}
                  labelFormatter={(v) => new Date(v).toLocaleTimeString()}
                />
                <Legend />
                <Area 
                  type="monotone" 
                  dataKey="consumption" 
                  stroke="#00d4ff" 
                  fill="url(#energyGradient)"
                  strokeWidth={2}
                  name="Actual"
                />
                <Line 
                  type="monotone" 
                  dataKey="predicted" 
                  stroke="#a855f7" 
                  strokeWidth={2}
                  strokeDasharray="5 5"
                  dot={false}
                  name="Predicted"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Downtime and Radar */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Downtime by Equipment */}
        <div className="card card-hover">
          <div className="mb-4">
            <h3 className="text-lg font-semibold text-white">Downtime by Equipment</h3>
            <p className="text-sm text-gray-500">Hours of unplanned downtime this week</p>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={downtimeData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis type="number" tick={{ fill: '#64748b', fontSize: 10 }} />
                <YAxis 
                  type="category" 
                  dataKey="name" 
                  tick={{ fill: '#94a3b8', fontSize: 11 }}
                  width={100}
                />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1e2228', border: '1px solid #334155', borderRadius: '8px' }}
                  formatter={(v: number) => [`${v} hours`, 'Downtime']}
                />
                <Bar 
                  dataKey="value" 
                  fill="#ff9500" 
                  radius={[0, 4, 4, 0]}
                  background={{ fill: 'rgba(255,255,255,0.02)', radius: [0, 4, 4, 0] }}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Performance Radar */}
        <div className="card card-hover">
          <div className="mb-4">
            <h3 className="text-lg font-semibold text-white">Performance Metrics</h3>
            <p className="text-sm text-gray-500">Overall system health indicators</p>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart data={performanceRadar}>
                <PolarGrid stroke="rgba(255,255,255,0.1)" />
                <PolarAngleAxis 
                  dataKey="metric" 
                  tick={{ fill: '#94a3b8', fontSize: 11 }}
                />
                <PolarRadiusAxis 
                  angle={30} 
                  domain={[0, 100]} 
                  tick={{ fill: '#64748b', fontSize: 9 }}
                />
                <Radar
                  name="Performance"
                  dataKey="value"
                  stroke="#00d4ff"
                  fill="#00d4ff"
                  fillOpacity={0.3}
                  strokeWidth={2}
                />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1e2228', border: '1px solid #334155', borderRadius: '8px' }}
                  formatter={(v: number) => [`${v}%`, 'Score']}
                />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Maintenance Schedule */}
      <div className="card">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-accent-orange/10">
              <Calendar size={20} className="text-accent-orange" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-white">Maintenance Schedule</h3>
              <p className="text-sm text-gray-500">Upcoming maintenance based on AI predictions</p>
            </div>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="table-header">
                <th className="text-left px-4 py-3">Equipment</th>
                <th className="text-left px-4 py-3">Type</th>
                <th className="text-left px-4 py-3">Scheduled Date</th>
                <th className="text-left px-4 py-3">Duration</th>
                <th className="text-left px-4 py-3">Priority</th>
                <th className="text-left px-4 py-3">Description</th>
                <th className="text-left px-4 py-3">Actions</th>
              </tr>
            </thead>
            <tbody>
              {maintenance.map((item) => (
                <tr key={item.id} className="table-row">
                  <td className="px-4 py-4">
                    <Link 
                      to={`/twins/${item.twinId}`}
                      className="text-white hover:text-accent-cyan transition-colors"
                    >
                      {item.twinName}
                    </Link>
                  </td>
                  <td className="px-4 py-4">
                    <span className={`
                      inline-flex items-center gap-1.5 text-sm
                      ${item.type === 'predictive' ? 'text-accent-purple' : ''}
                      ${item.type === 'preventive' ? 'text-accent-cyan' : ''}
                      ${item.type === 'corrective' ? 'text-accent-orange' : ''}
                    `}>
                      {item.type === 'predictive' && <Brain size={14} />}
                      {item.type === 'preventive' && <Clock size={14} />}
                      {item.type === 'corrective' && <Wrench size={14} />}
                      {item.type}
                    </span>
                  </td>
                  <td className="px-4 py-4">
                    <span className="text-gray-300">
                      {new Date(item.scheduledDate).toLocaleDateString()} at{' '}
                      {new Date(item.scheduledDate).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                  </td>
                  <td className="px-4 py-4">
                    <span className="text-gray-400">{item.estimatedDuration}h</span>
                  </td>
                  <td className="px-4 py-4">
                    <span className={`
                      inline-flex items-center gap-1.5 px-2 py-1 rounded-full text-xs font-medium
                      ${maintenancePriorityColors[item.priority]}
                    `}>
                      {item.priority}
                    </span>
                  </td>
                  <td className="px-4 py-4">
                    <span className="text-gray-400 text-sm max-w-xs truncate block">
                      {item.description}
                    </span>
                  </td>
                  <td className="px-4 py-4">
                    <button className="btn-secondary text-sm py-1.5">
                      Schedule
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="card card-hover">
          <div className="flex items-center gap-3">
            <div className="p-3 rounded-xl bg-accent-green/10">
              <CheckCircle size={24} className="text-accent-green" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">94.2%</p>
              <p className="text-sm text-gray-500">Avg. OEE</p>
            </div>
          </div>
        </div>
        
        <div className="card card-hover">
          <div className="flex items-center gap-3">
            <div className="p-3 rounded-xl bg-accent-cyan/10">
              <Brain size={24} className="text-accent-cyan" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">87%</p>
              <p className="text-sm text-gray-500">Prediction Accuracy</p>
            </div>
          </div>
        </div>
        
        <div className="card card-hover">
          <div className="flex items-center gap-3">
            <div className="p-3 rounded-xl bg-accent-orange/10">
              <AlertTriangle size={24} className="text-accent-orange" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">3</p>
              <p className="text-sm text-gray-500">Anomalies Detected</p>
            </div>
          </div>
        </div>
        
        <div className="card card-hover">
          <div className="flex items-center gap-3">
            <div className="p-3 rounded-xl bg-accent-purple/10">
              <TrendingUp size={24} className="text-accent-purple" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">+12%</p>
              <p className="text-sm text-gray-500">Efficiency Gain</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
