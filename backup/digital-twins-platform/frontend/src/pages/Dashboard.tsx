import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  Activity, 
  AlertTriangle, 
  TrendingUp, 
  TrendingDown, 
  Minus,
  Box,
  Thermometer,
  Zap,
  Clock,
  ChevronRight,
  ArrowRight
} from 'lucide-react';
import { 
  LineChart, 
  Line, 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import { mockTwins, mockKPIs, generateTimeSeriesData } from '../data/mockData';
import { DigitalTwin, KPIData } from '../types';
import { StatusBadge } from '../components/StatusBadge';
import { TwinCard } from '../components/TwinCard';
import { realtimeService } from '../services/api';

export function Dashboard() {
  const [twins, setTwins] = useState<DigitalTwin[]>(mockTwins);
  const [kpis] = useState<KPIData[]>(mockKPIs);
  const [chartData, setChartData] = useState(generateTimeSeriesData(24, 75, 15));
  const [efficiencyData] = useState(() => {
    return generateTimeSeriesData(12, 85, 8).map((d, i) => ({
      ...d,
      oee: d.value,
      availability: d.value - Math.random() * 5,
      performance: d.value - Math.random() * 8,
    }));
  });

  useEffect(() => {
    // Subscribe to real-time updates
    const unsubscribe = realtimeService.subscribe('sensor_update', () => {
      setChartData(prev => {
        const newPoint = {
          timestamp: new Date(),
          value: 75 + (Math.random() - 0.5) * 30,
        };
        return [...prev.slice(1), newPoint];
      });
    });

    realtimeService.connect();
    return unsubscribe;
  }, []);

  // Status distribution for pie chart
  const statusDistribution = [
    { name: 'Healthy', value: twins.filter(t => t.status === 'healthy').length, color: '#00ff88' },
    { name: 'Warning', value: twins.filter(t => t.status === 'warning').length, color: '#ff9500' },
    { name: 'Critical', value: twins.filter(t => t.status === 'critical').length, color: '#ff3b5c' },
    { name: 'Offline', value: twins.filter(t => t.status === 'offline').length, color: '#64748b' },
  ];

  const recentTwins = twins.slice(0, 4);

  return (
    <div className="space-y-6 fade-in">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        <div>
          <h1 className="text-2xl lg:text-3xl font-bold text-white">Dashboard</h1>
          <p className="text-gray-400 mt-1">Monitor your digital twins in real-time</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 px-4 py-2 bg-surface-800/50 rounded-lg border border-surface-700/50">
            <Clock size={16} className="text-gray-500" />
            <span className="text-sm text-gray-400">Last updated: </span>
            <span className="text-sm font-mono text-accent-cyan">
              {new Date().toLocaleTimeString()}
            </span>
          </div>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
        {kpis.map((kpi, index) => (
          <KPICard key={index} kpi={kpi} />
        ))}
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Chart - System Performance */}
        <div className="lg:col-span-2 card card-hover">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-lg font-semibold text-white">System Performance</h3>
              <p className="text-sm text-gray-500">Real-time sensor data aggregate</p>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-accent-cyan animate-pulse"></span>
              <span className="text-sm text-accent-cyan">Live</span>
            </div>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData}>
                <defs>
                  <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#00d4ff" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#00d4ff" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis 
                  dataKey="timestamp" 
                  tick={{ fill: '#64748b', fontSize: 11 }}
                  tickFormatter={(value) => new Date(value).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                />
                <YAxis tick={{ fill: '#64748b', fontSize: 11 }} />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#1e2228', 
                    border: '1px solid #334155',
                    borderRadius: '8px',
                    boxShadow: '0 10px 40px rgba(0,0,0,0.3)'
                  }}
                  labelFormatter={(value) => new Date(value).toLocaleTimeString()}
                />
                <Area 
                  type="monotone" 
                  dataKey="value" 
                  stroke="#00d4ff" 
                  strokeWidth={2}
                  fillOpacity={1} 
                  fill="url(#colorValue)" 
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Status Distribution */}
        <div className="card card-hover">
          <div className="mb-4">
            <h3 className="text-lg font-semibold text-white">Status Distribution</h3>
            <p className="text-sm text-gray-500">Twin health overview</p>
          </div>
          <div className="h-48 flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={statusDistribution}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {statusDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#1e2228', 
                    border: '1px solid #334155',
                    borderRadius: '8px'
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="grid grid-cols-2 gap-2 mt-4">
            {statusDistribution.map((item) => (
              <div key={item.name} className="flex items-center gap-2">
                <span 
                  className="w-3 h-3 rounded-full" 
                  style={{ backgroundColor: item.color }}
                />
                <span className="text-sm text-gray-400">{item.name}</span>
                <span className="text-sm font-semibold text-white ml-auto">{item.value}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* OEE Chart and Recent Twins */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* OEE Metrics */}
        <div className="card card-hover">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-lg font-semibold text-white">Overall Equipment Effectiveness</h3>
              <p className="text-sm text-gray-500">Last 12 hours</p>
            </div>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={efficiencyData}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis 
                  dataKey="timestamp" 
                  tick={{ fill: '#64748b', fontSize: 11 }}
                  tickFormatter={(value) => new Date(value).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                />
                <YAxis domain={[70, 100]} tick={{ fill: '#64748b', fontSize: 11 }} />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#1e2228', 
                    border: '1px solid #334155',
                    borderRadius: '8px'
                  }}
                  labelFormatter={(value) => new Date(value).toLocaleTimeString()}
                />
                <Line type="monotone" dataKey="oee" stroke="#00d4ff" strokeWidth={2} dot={false} name="OEE" />
                <Line type="monotone" dataKey="availability" stroke="#00ff88" strokeWidth={2} dot={false} name="Availability" />
                <Line type="monotone" dataKey="performance" stroke="#a855f7" strokeWidth={2} dot={false} name="Performance" />
              </LineChart>
            </ResponsiveContainer>
          </div>
          <div className="flex justify-center gap-6 mt-4">
            <div className="flex items-center gap-2">
              <span className="w-3 h-0.5 bg-accent-cyan" />
              <span className="text-xs text-gray-400">OEE</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-3 h-0.5 bg-accent-green" />
              <span className="text-xs text-gray-400">Availability</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-3 h-0.5 bg-accent-purple" />
              <span className="text-xs text-gray-400">Performance</span>
            </div>
          </div>
        </div>

        {/* Recent Twins */}
        <div className="card card-hover">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-lg font-semibold text-white">Recent Digital Twins</h3>
              <p className="text-sm text-gray-500">Latest activity</p>
            </div>
            <Link 
              to="/twins" 
              className="flex items-center gap-1 text-sm text-primary-400 hover:text-primary-300 transition-colors"
            >
              View all <ChevronRight size={16} />
            </Link>
          </div>
          <div className="space-y-3">
            {recentTwins.map((twin) => (
              <Link
                key={twin.id}
                to={`/twins/${twin.id}`}
                className="flex items-center gap-4 p-3 rounded-lg bg-surface-800/30 hover:bg-surface-700/50 transition-colors group"
              >
                <div className={`
                  w-10 h-10 rounded-lg flex items-center justify-center
                  ${twin.status === 'healthy' ? 'bg-accent-green/10 text-accent-green' : ''}
                  ${twin.status === 'warning' ? 'bg-accent-orange/10 text-accent-orange' : ''}
                  ${twin.status === 'critical' ? 'bg-accent-red/10 text-accent-red' : ''}
                  ${twin.status === 'offline' ? 'bg-gray-500/10 text-gray-400' : ''}
                `}>
                  <Box size={20} />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-white truncate group-hover:text-accent-cyan transition-colors">
                    {twin.name}
                  </p>
                  <p className="text-sm text-gray-500 truncate">{twin.location}</p>
                </div>
                <StatusBadge status={twin.status} />
                <ArrowRight size={16} className="text-gray-600 group-hover:text-gray-400 transition-colors" />
              </Link>
            ))}
          </div>
        </div>
      </div>

      {/* Sensor Overview */}
      <div className="card card-hover">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-lg font-semibold text-white">Sensor Overview</h3>
            <p className="text-sm text-gray-500">Current readings across all twins</p>
          </div>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
          {[
            { icon: Thermometer, label: 'Avg Temperature', value: '67.3°C', trend: 'up', color: 'text-accent-orange' },
            { icon: Activity, label: 'Avg Vibration', value: '42.1 mm/s', trend: 'stable', color: 'text-accent-cyan' },
            { icon: Zap, label: 'Power Usage', value: '2.4 MW', trend: 'down', color: 'text-accent-purple' },
            { icon: Activity, label: 'Flow Rate', value: '78.5 L/min', trend: 'up', color: 'text-accent-green' },
            { icon: Thermometer, label: 'Humidity', value: '54%', trend: 'stable', color: 'text-primary-400' },
            { icon: Zap, label: 'Pressure', value: '5.2 bar', trend: 'down', color: 'text-accent-red' },
          ].map((sensor, index) => (
            <div 
              key={index} 
              className="p-4 bg-surface-800/30 rounded-lg border border-surface-700/30 hover:border-surface-600/50 transition-colors"
            >
              <div className="flex items-center gap-2 mb-2">
                <sensor.icon size={16} className={sensor.color} />
                <span className="text-xs text-gray-500">{sensor.label}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className={`text-lg font-bold font-mono ${sensor.color}`}>{sensor.value}</span>
                {sensor.trend === 'up' && <TrendingUp size={14} className="text-accent-green" />}
                {sensor.trend === 'down' && <TrendingDown size={14} className="text-accent-red" />}
                {sensor.trend === 'stable' && <Minus size={14} className="text-gray-500" />}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// KPI Card Component
function KPICard({ kpi }: { kpi: KPIData }) {
  return (
    <div className="card card-hover p-4">
      <div className="flex items-start justify-between">
        <span className="text-sm text-gray-500">{kpi.label}</span>
        {kpi.trend && (
          <span className={`
            p-1 rounded
            ${kpi.trend === 'up' ? 'text-accent-green bg-accent-green/10' : ''}
            ${kpi.trend === 'down' ? (kpi.label.includes('Alert') ? 'text-accent-green bg-accent-green/10' : 'text-accent-red bg-accent-red/10') : ''}
            ${kpi.trend === 'stable' ? 'text-gray-400 bg-gray-500/10' : ''}
          `}>
            {kpi.trend === 'up' && <TrendingUp size={14} />}
            {kpi.trend === 'down' && <TrendingDown size={14} />}
            {kpi.trend === 'stable' && <Minus size={14} />}
          </span>
        )}
      </div>
      <div className="mt-2">
        <span className="text-2xl font-bold text-white">{kpi.value}</span>
      </div>
      {kpi.change !== undefined && (
        <div className="mt-2 flex items-center gap-1">
          <span className={`
            text-xs font-medium
            ${kpi.change > 0 ? 'text-accent-green' : kpi.change < 0 ? 'text-accent-red' : 'text-gray-400'}
          `}>
            {kpi.change > 0 ? '+' : ''}{kpi.change}%
          </span>
          <span className="text-xs text-gray-500">{kpi.changeLabel}</span>
        </div>
      )}
    </div>
  );
}
