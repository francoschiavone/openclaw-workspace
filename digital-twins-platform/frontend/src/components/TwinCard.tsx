import { Link } from 'react-router-dom';
import { Box, MapPin, Clock, ChevronRight } from 'lucide-react';
import { DigitalTwin } from '../types';
import { StatusBadge } from './StatusBadge';

interface TwinCardProps {
  twin: DigitalTwin;
  showDetails?: boolean;
}

export function TwinCard({ twin, showDetails = true }: TwinCardProps) {
  const typeIcons: Record<string, string> = {
    machine: '⚙️',
    factory: '🏭',
    vehicle: '🚗',
    robot: '🤖',
    sensor: '📡',
  };

  return (
    <Link
      to={`/twins/${twin.id}`}
      className="card card-hover block group"
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className={`
            w-12 h-12 rounded-xl flex items-center justify-center text-2xl
            ${twin.status === 'healthy' ? 'bg-accent-green/10' : ''}
            ${twin.status === 'warning' ? 'bg-accent-orange/10' : ''}
            ${twin.status === 'critical' ? 'bg-accent-red/10' : ''}
            ${twin.status === 'offline' ? 'bg-gray-500/10' : ''}
          `}>
            {typeIcons[twin.type] || '📦'}
          </div>
          <div>
            <h3 className="font-semibold text-white group-hover:text-accent-cyan transition-colors">
              {twin.name}
            </h3>
            <p className="text-sm text-gray-500 capitalize">{twin.type}</p>
          </div>
        </div>
        <StatusBadge status={twin.status} size="sm" />
      </div>

      {showDetails && (
        <>
          <p className="text-sm text-gray-400 mb-4 line-clamp-2">
            {twin.description}
          </p>
          
          <div className="flex items-center gap-4 text-xs text-gray-500">
            <span className="flex items-center gap-1">
              <MapPin size={12} />
              {twin.location}
            </span>
            <span className="flex items-center gap-1">
              <Clock size={12} />
              Updated {formatRelativeTime(twin.lastUpdated)}
            </span>
          </div>

          {/* Sensor preview */}
          {twin.sensors.length > 0 && (
            <div className="mt-4 pt-4 border-t border-surface-700/50">
              <div className="grid grid-cols-3 gap-2">
                {twin.sensors.slice(0, 3).map((sensor) => (
                  <div key={sensor.id} className="text-center">
                    <p className="text-xs text-gray-500">{sensor.name}</p>
                    <p className={`
                      text-sm font-mono font-semibold
                      ${sensor.status === 'critical' ? 'text-accent-red' : ''}
                      ${sensor.status === 'warning' ? 'text-accent-orange' : ''}
                      ${sensor.status === 'healthy' ? 'text-white' : ''}
                    `}>
                      {sensor.value.toFixed(1)}{sensor.unit}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}

      <div className="absolute right-4 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 transition-opacity">
        <ChevronRight size={20} className="text-gray-400" />
      </div>
    </Link>
  );
}

function formatRelativeTime(date: Date): string {
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);

  if (minutes < 1) return 'just now';
  if (minutes < 60) return `${minutes}m ago`;
  if (hours < 24) return `${hours}h ago`;
  return `${days}d ago`;
}
