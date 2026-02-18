import { useState, useEffect } from 'react';
import { Search, Filter, Grid, List, Plus, RefreshCw } from 'lucide-react';
import { DigitalTwin, TwinFilter, TwinStatus, TwinType } from '../types';
import { twinsApi } from '../services/api';
import { mockTwins } from '../data/mockData';
import { TwinCard } from '../components/TwinCard';
import { StatusBadge } from '../components/StatusBadge';

export function TwinList() {
  const [twins, setTwins] = useState<DigitalTwin[]>([]);
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [filters, setFilters] = useState<TwinFilter>({
    search: '',
    status: 'all',
    type: 'all',
  });
  const [showFilters, setShowFilters] = useState(false);

  useEffect(() => {
    loadTwins();
  }, [filters]);

  const loadTwins = async () => {
    setLoading(true);
    try {
      const data = await twinsApi.getAll(filters);
      setTwins(data);
    } catch (error) {
      console.error('Failed to load twins:', error);
      setTwins(mockTwins);
    } finally {
      setLoading(false);
    }
  };

  const statusOptions: (TwinStatus | 'all')[] = ['all', 'healthy', 'warning', 'critical', 'offline'];
  const typeOptions: (TwinType | 'all')[] = ['all', 'machine', 'factory', 'vehicle', 'robot', 'sensor'];

  const filteredTwins = twins.filter(twin => {
    if (filters.search) {
      const search = filters.search.toLowerCase();
      if (!twin.name.toLowerCase().includes(search) &&
          !twin.description.toLowerCase().includes(search) &&
          !twin.location.toLowerCase().includes(search)) {
        return false;
      }
    }
    if (filters.status !== 'all' && twin.status !== filters.status) return false;
    if (filters.type !== 'all' && twin.type !== filters.type) return false;
    return true;
  });

  return (
    <div className="space-y-6 fade-in">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        <div>
          <h1 className="text-2xl lg:text-3xl font-bold text-white">Digital Twins</h1>
          <p className="text-gray-400 mt-1">Manage and monitor all your digital twins</p>
        </div>
        <div className="flex items-center gap-3">
          <button 
            onClick={loadTwins}
            className="btn-ghost flex items-center gap-2"
          >
            <RefreshCw size={18} />
            <span className="hidden sm:inline">Refresh</span>
          </button>
          <button className="btn-primary flex items-center gap-2">
            <Plus size={18} />
            <span className="hidden sm:inline">Add Twin</span>
          </button>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="card">
        <div className="flex flex-col sm:flex-row gap-4">
          {/* Search */}
          <div className="flex-1 relative">
            <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
            <input
              type="text"
              placeholder="Search by name, description, or location..."
              value={filters.search}
              onChange={(e) => setFilters({ ...filters, search: e.target.value })}
              className="input pl-10"
            />
          </div>

          {/* Filter Toggle */}
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`btn-secondary flex items-center gap-2 ${showFilters ? 'bg-surface-600' : ''}`}
          >
            <Filter size={18} />
            <span>Filters</span>
            {(filters.status !== 'all' || filters.type !== 'all') && (
              <span className="w-2 h-2 rounded-full bg-primary-500"></span>
            )}
          </button>

          {/* View Toggle */}
          <div className="flex items-center bg-surface-800 rounded-lg p-1">
            <button
              onClick={() => setViewMode('grid')}
              className={`p-2 rounded-md transition-colors ${viewMode === 'grid' ? 'bg-surface-600 text-white' : 'text-gray-400 hover:text-white'}`}
            >
              <Grid size={18} />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`p-2 rounded-md transition-colors ${viewMode === 'list' ? 'bg-surface-600 text-white' : 'text-gray-400 hover:text-white'}`}
            >
              <List size={18} />
            </button>
          </div>
        </div>

        {/* Expanded Filters */}
        {showFilters && (
          <div className="mt-4 pt-4 border-t border-surface-700/50 grid grid-cols-1 sm:grid-cols-2 gap-4">
            {/* Status Filter */}
            <div>
              <label className="block text-sm text-gray-400 mb-2">Status</label>
              <div className="flex flex-wrap gap-2">
                {statusOptions.map((status) => (
                  <button
                    key={status}
                    onClick={() => setFilters({ ...filters, status })}
                    className={`
                      px-3 py-1.5 rounded-lg text-sm font-medium transition-colors
                      ${filters.status === status 
                        ? 'bg-primary-500/20 text-primary-400 border border-primary-500/30' 
                        : 'bg-surface-800 text-gray-400 hover:text-white border border-surface-700'
                      }
                    `}
                  >
                    {status === 'all' ? 'All' : status.charAt(0).toUpperCase() + status.slice(1)}
                  </button>
                ))}
              </div>
            </div>

            {/* Type Filter */}
            <div>
              <label className="block text-sm text-gray-400 mb-2">Type</label>
              <div className="flex flex-wrap gap-2">
                {typeOptions.map((type) => (
                  <button
                    key={type}
                    onClick={() => setFilters({ ...filters, type })}
                    className={`
                      px-3 py-1.5 rounded-lg text-sm font-medium transition-colors
                      ${filters.type === type 
                        ? 'bg-primary-500/20 text-primary-400 border border-primary-500/30' 
                        : 'bg-surface-800 text-gray-400 hover:text-white border border-surface-700'
                      }
                    `}
                  >
                    {type === 'all' ? 'All Types' : type.charAt(0).toUpperCase() + type.slice(1)}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Results Count */}
      <div className="flex items-center justify-between text-sm text-gray-500">
        <span>Showing {filteredTwins.length} of {twins.length} twins</span>
        {filteredTwins.length !== twins.length && (
          <button 
            onClick={() => setFilters({ search: '', status: 'all', type: 'all' })}
            className="text-primary-400 hover:text-primary-300"
          >
            Clear filters
          </button>
        )}
      </div>

      {/* Twins Grid/List */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="card h-48">
              <div className="skeleton h-full w-full"></div>
            </div>
          ))}
        </div>
      ) : filteredTwins.length === 0 ? (
        <div className="card py-16 text-center">
          <div className="text-gray-500 mb-2">No digital twins found</div>
          <p className="text-sm text-gray-600">Try adjusting your search or filters</p>
        </div>
      ) : viewMode === 'grid' ? (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {filteredTwins.map((twin) => (
            <TwinCard key={twin.id} twin={twin} />
          ))}
        </div>
      ) : (
        <div className="card overflow-hidden">
          <table className="w-full">
            <thead>
              <tr className="table-header">
                <th className="text-left px-4 py-3">Name</th>
                <th className="text-left px-4 py-3 hidden md:table-cell">Type</th>
                <th className="text-left px-4 py-3 hidden lg:table-cell">Location</th>
                <th className="text-left px-4 py-3">Status</th>
                <th className="text-left px-4 py-3 hidden md:table-cell">Sensors</th>
                <th className="text-left px-4 py-3 hidden lg:table-cell">Last Updated</th>
              </tr>
            </thead>
            <tbody>
              {filteredTwins.map((twin) => (
                <tr key={twin.id} className="table-row cursor-pointer" onClick={() => window.location.href = `/twins/${twin.id}`}>
                  <td className="px-4 py-4">
                    <div className="flex items-center gap-3">
                      <div className={`
                        w-10 h-10 rounded-lg flex items-center justify-center text-lg
                        ${twin.status === 'healthy' ? 'bg-accent-green/10' : ''}
                        ${twin.status === 'warning' ? 'bg-accent-orange/10' : ''}
                        ${twin.status === 'critical' ? 'bg-accent-red/10' : ''}
                        ${twin.status === 'offline' ? 'bg-gray-500/10' : ''}
                      `}>
                        {twin.type === 'machine' && '⚙️'}
                        {twin.type === 'factory' && '🏭'}
                        {twin.type === 'vehicle' && '🚗'}
                        {twin.type === 'robot' && '🤖'}
                        {twin.type === 'sensor' && '📡'}
                      </div>
                      <div>
                        <p className="font-medium text-white">{twin.name}</p>
                        <p className="text-xs text-gray-500 md:hidden">{twin.location}</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-4 py-4 hidden md:table-cell">
                    <span className="text-gray-300 capitalize">{twin.type}</span>
                  </td>
                  <td className="px-4 py-4 hidden lg:table-cell">
                    <span className="text-gray-400">{twin.location}</span>
                  </td>
                  <td className="px-4 py-4">
                    <StatusBadge status={twin.status} size="sm" />
                  </td>
                  <td className="px-4 py-4 hidden md:table-cell">
                    <span className="text-gray-400">{twin.sensors.length} active</span>
                  </td>
                  <td className="px-4 py-4 hidden lg:table-cell">
                    <span className="text-gray-500 text-sm">
                      {new Date(twin.lastUpdated).toLocaleString()}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
