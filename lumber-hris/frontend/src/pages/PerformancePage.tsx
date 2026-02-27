import React, { useState, useEffect } from 'react';
import { Star, Calendar, Target, AlertTriangle, Award, Grid3X3, ChevronRight } from 'lucide-react';
import api from '@/lib/api';

// Types
interface Cycle {
  id: string;
  name: string;
  review_type: 'Annual' | 'Quarterly' | '360';
  status: 'Active' | 'Completed';
  start_date: string;
  end_date: string;
}

interface Review {
  id: string;
  employee_name: string;
  reviewer_name: string;
  overall_rating: number;
  status: 'Completed' | 'In Progress' | 'Draft';
  review_date: string;
  review_type: string;
}

interface Goal {
  id: string;
  employee_name: string;
  title: string;
  description: string;
  target_date: string;
  progress: number;
  status: 'On Track' | 'At Risk' | 'Completed';
}

interface Incident {
  id: string;
  employee_name: string;
  incident_type: string;
  severity: 'Critical' | 'Major' | 'Minor';
  date: string;
  description: string;
  status: string;
}

interface Commendation {
  id: string;
  employee_name: string;
  type: string;
  date: string;
  description: string;
  awarded_by: string;
}

interface NineBoxCell {
  count: number;
  employees: { name: string; title: string }[];
}

type TabType = 'reviews' | 'goals' | 'incidents' | 'calibration';

const PerformancePage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabType>('reviews');
  const [cycles, setCycles] = useState<Cycle[]>([]);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [goals, setGoals] = useState<Goal[]>([]);
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [commendations, setCommendations] = useState<Commendation[]>([]);
  const [nineBoxGrid, setNineBoxGrid] = useState<NineBoxCell[][]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        if (activeTab === 'reviews') {
          const [cyclesRes, reviewsRes] = await Promise.all([
            api.get('/api/performance/cycles'),
            api.get('/api/performance/reviews')
          ]);
          setCycles(cyclesRes.data);
          setReviews(reviewsRes.data);
        } else if (activeTab === 'goals') {
          const res = await api.get('/api/performance/goals');
          setGoals(res.data);
        } else if (activeTab === 'incidents') {
          const [incidentsRes, commendationsRes] = await Promise.all([
            api.get('/api/performance/incidents'),
            api.get('/api/performance/commendations')
          ]);
          setIncidents(incidentsRes.data);
          setCommendations(commendationsRes.data);
        } else if (activeTab === 'calibration') {
          const res = await api.get('/api/performance/calibration/nine-box');
          setNineBoxGrid(res.data.grid);
        }
      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [activeTab]);

  const tabs = [
    { id: 'reviews' as TabType, label: 'Reviews' },
    { id: 'goals' as TabType, label: 'Goals' },
    { id: 'incidents' as TabType, label: 'Incidents & Recognition' },
    { id: 'calibration' as TabType, label: 'Calibration' }
  ];

  const renderStars = (rating: number) => {
    return (
      <div className="flex gap-0.5">
        {[1, 2, 3, 4, 5].map((star) => (
          <Star
            key={star}
            size={16}
            fill={star <= rating ? '#f59e0b' : 'transparent'}
            stroke={star <= rating ? '#f59e0b' : '#d1d5db'}
          />
        ))}
      </div>
    );
  };

  const getStatusPillClass = (status: string) => {
    switch (status) {
      case 'Completed':
        return 'bg-green-100 text-green-700';
      case 'In Progress':
      case 'Active':
        return 'bg-blue-100 text-blue-700';
      case 'Draft':
        return 'bg-gray-100 text-gray-600';
      case 'At Risk':
        return 'bg-red-100 text-red-700';
      case 'On Track':
        return 'bg-green-100 text-green-700';
      default:
        return 'bg-gray-100 text-gray-600';
    }
  };

  const getTypePillClass = (type: string) => {
    switch (type) {
      case 'Annual':
        return 'bg-purple-100 text-purple-700';
      case 'Quarterly':
        return 'bg-blue-100 text-blue-700';
      case '360':
        return 'bg-amber-100 text-amber-700';
      default:
        return 'bg-gray-100 text-gray-600';
    }
  };

  const getSeverityPillClass = (severity: string) => {
    switch (severity) {
      case 'Critical':
        return 'bg-red-100 text-red-700';
      case 'Major':
        return 'bg-yellow-100 text-yellow-700';
      case 'Minor':
        return 'bg-gray-100 text-gray-600';
      default:
        return 'bg-gray-100 text-gray-600';
    }
  };

  const getNineBoxColor = (row: number, col: number) => {
    // Top-right (high potential, high performance) = green
    if (row === 0 && col === 2) return 'bg-green-100 border-green-300';
    // Bottom-left (low potential, low performance) = red
    if (row === 2 && col === 0) return 'bg-red-100 border-red-300';
    // Diagonal = yellow
    if (row === col) return 'bg-yellow-100 border-yellow-300';
    // Gradient between
    if (row + col >= 3) return 'bg-green-50 border-green-200';
    return 'bg-red-50 border-red-200';
  };

  const renderReviewsTab = () => (
    <div className="space-y-6">
      {/* Active Review Cycles */}
      <div>
        <h2 className="text-lg font-semibold text-[var(--t1)] mb-4">Active Review Cycles</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {cycles.map((cycle) => (
            <div key={cycle.id} className="bg-white rounded-lg border border-[var(--border)] p-4 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between mb-3">
                <h3 className="font-medium text-[var(--t1)]">{cycle.name}</h3>
                <div className="flex gap-2">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getTypePillClass(cycle.review_type)}`}>
                    {cycle.review_type}
                  </span>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusPillClass(cycle.status)}`}>
                    {cycle.status}
                  </span>
                </div>
              </div>
              <div className="flex items-center gap-2 text-sm text-[var(--t3)] mb-3">
                <Calendar size={14} />
                <span>{cycle.start_date} - {cycle.end_date}</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-[var(--mint)] h-2 rounded-full" style={{ width: '65%' }}></div>
              </div>
              <p className="text-xs text-[var(--t3)] mt-1">65% completed</p>
            </div>
          ))}
        </div>
      </div>

      {/* Recent Reviews */}
      <div>
        <h2 className="text-lg font-semibold text-[var(--t1)] mb-4">Recent Reviews</h2>
        <div className="bg-white rounded-lg border border-[var(--border)] overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-[var(--border)]">
              <tr>
                <th className="text-left py-3 px-4 text-sm font-medium text-[var(--t2)]">Employee</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-[var(--t2)]">Reviewer</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-[var(--t2)]">Rating</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-[var(--t2)]">Status</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-[var(--t2)]">Date</th>
              </tr>
            </thead>
            <tbody>
              {reviews.map((review) => (
                <tr key={review.id} className="border-b border-[var(--border)] last:border-0 hover:bg-gray-50">
                  <td className="py-3 px-4 text-sm text-[var(--t1)]">{review.employee_name}</td>
                  <td className="py-3 px-4 text-sm text-[var(--t2)]">{review.reviewer_name}</td>
                  <td className="py-3 px-4">{renderStars(review.overall_rating)}</td>
                  <td className="py-3 px-4">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusPillClass(review.status)}`}>
                      {review.status}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-sm text-[var(--t3)]">{review.review_date}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );

  const renderGoalsTab = () => (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {goals.map((goal) => (
        <div key={goal.id} className="bg-white rounded-lg border border-[var(--border)] p-4 hover:shadow-md transition-shadow">
          <div className="flex items-start justify-between mb-2">
            <Target className="text-[var(--blue)]" size={20} />
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusPillClass(goal.status)}`}>
              {goal.status}
            </span>
          </div>
          <h3 className="font-medium text-[var(--t1)] mb-1">{goal.title}</h3>
          <p className="text-sm text-[var(--t3)] mb-2">{goal.employee_name}</p>
          <p className="text-xs text-[var(--t3)] mb-3 line-clamp-2">{goal.description}</p>
          <div className="flex items-center gap-2 text-xs text-[var(--t3)] mb-3">
            <Calendar size={12} />
            <span>Target: {goal.target_date}</span>
          </div>
          <div className="relative">
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-[var(--mint)] h-2 rounded-full transition-all" 
                style={{ width: `${goal.progress}%` }}
              ></div>
            </div>
            <p className="text-xs text-[var(--t2)] mt-1 font-medium">{goal.progress}% complete</p>
          </div>
        </div>
      ))}
    </div>
  );

  const renderIncidentsTab = () => (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Incidents */}
      <div>
        <h2 className="text-lg font-semibold text-[var(--t1)] mb-4 flex items-center gap-2">
          <AlertTriangle className="text-[var(--red)]" size={20} />
          Incidents
        </h2>
        <div className="space-y-3">
          {incidents.map((incident) => (
            <div 
              key={incident.id} 
              className="bg-white rounded-lg border-l-4 border-[var(--red)] border border-[var(--border)] p-4"
            >
              <div className="flex items-start justify-between mb-2">
                <h3 className="font-medium text-[var(--t1)]">{incident.incident_type}</h3>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getSeverityPillClass(incident.severity)}`}>
                  {incident.severity}
                </span>
              </div>
              <p className="text-sm text-[var(--t2)] mb-1">{incident.employee_name}</p>
              <p className="text-xs text-[var(--t3)] mb-2">{incident.description}</p>
              <div className="flex items-center gap-2 text-xs text-[var(--t3)]">
                <Calendar size={12} />
                <span>{incident.date}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Commendations */}
      <div>
        <h2 className="text-lg font-semibold text-[var(--t1)] mb-4 flex items-center gap-2">
          <Award className="text-[var(--mint)]" size={20} />
          Commendations
        </h2>
        <div className="space-y-3">
          {commendations.map((commendation) => (
            <div 
              key={commendation.id} 
              className="bg-white rounded-lg border-l-4 border-[var(--mint)] border border-[var(--border)] p-4"
            >
              <div className="flex items-start justify-between mb-2">
                <h3 className="font-medium text-[var(--t1)]">{commendation.type}</h3>
                <Award className="text-[var(--mint)]" size={16} />
              </div>
              <p className="text-sm text-[var(--t2)] mb-1">{commendation.employee_name}</p>
              <p className="text-xs text-[var(--t3)] mb-2">{commendation.description}</p>
              <div className="flex items-center justify-between text-xs text-[var(--t3)]">
                <span>Awarded by: {commendation.awarded_by}</span>
                <span>{commendation.date}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderCalibrationTab = () => (
    <div>
      <h2 className="text-lg font-semibold text-[var(--t1)] mb-4 flex items-center gap-2">
        <Grid3X3 className="text-[var(--blue)]" size={20} />
        9-Box Calibration Grid
      </h2>
      <div className="bg-white rounded-lg border border-[var(--border)] p-6">
        {/* Y-axis label */}
        <div className="flex">
          <div className="flex flex-col justify-center items-center pr-4" style={{ height: '400px' }}>
            <span className="text-sm font-medium text-[var(--t2)] transform -rotate-90 whitespace-nowrap">
              Potential →
            </span>
          </div>
          
          <div className="flex-1">
            {/* Grid */}
            <div className="grid grid-cols-3 gap-2 mb-4">
              {nineBoxGrid.map((row, rowIndex) =>
                row.map((cell, colIndex) => (
                  <div
                    key={`${rowIndex}-${colIndex}`}
                    className={`border-2 rounded-lg p-4 min-h-[120px] ${getNineBoxColor(rowIndex, colIndex)}`}
                  >
                    <div className="text-2xl font-bold text-[var(--t1)] mb-2">{cell.count}</div>
                    <div className="space-y-1">
                      {cell.employees.slice(0, 3).map((emp, idx) => (
                        <div key={idx} className="text-xs text-[var(--t2)] truncate">
                          {emp.name}
                        </div>
                      ))}
                      {cell.employees.length > 3 && (
                        <div className="text-xs text-[var(--t3)]">
                          +{cell.employees.length - 3} more
                        </div>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
            
            {/* X-axis label */}
            <div className="text-center">
              <span className="text-sm font-medium text-[var(--t2)]">Performance →</span>
            </div>
          </div>
        </div>
        
        {/* Legend */}
        <div className="flex items-center justify-center gap-6 mt-6 pt-4 border-t border-[var(--border)]">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-green-100 border border-green-300"></div>
            <span className="text-xs text-[var(--t3)]">High Potential / High Performance</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-yellow-100 border border-yellow-300"></div>
            <span className="text-xs text-[var(--t3)]">Moderate</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-red-100 border border-red-300"></div>
            <span className="text-xs text-[var(--t3)]">Low Potential / Low Performance</span>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="p-6 bg-[var(--page-bg)] min-h-screen">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-[var(--t1)]">Performance Management</h1>
        <p className="text-[var(--t3)]">Track reviews, goals, and employee development</p>
      </div>

      {/* Sub-tab bar */}
      <div className="flex gap-2 mb-6 bg-white p-1 rounded-lg w-fit border border-[var(--border)]">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${
              activeTab === tab.id
                ? 'bg-[var(--blue)] text-white'
                : 'text-[var(--t3)] hover:bg-gray-100'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Content */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[var(--blue)]"></div>
        </div>
      ) : (
        <>
          {activeTab === 'reviews' && renderReviewsTab()}
          {activeTab === 'goals' && renderGoalsTab()}
          {activeTab === 'incidents' && renderIncidentsTab()}
          {activeTab === 'calibration' && renderCalibrationTab()}
        </>
      )}
    </div>
  );
};

export default PerformancePage;
