import { useState, useEffect, useRef } from 'react';
import { Bell, X, AlertTriangle, Info, AlertCircle, CheckCircle } from 'lucide-react';
import { Alert } from '../types';
import { alertsApi } from '../services/api';
import { mockAlerts } from '../data/mockData';

interface NotificationBellProps {
  className?: string;
}

export function NotificationBell({ className = '' }: NotificationBellProps) {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  
  const unacknowledgedCount = alerts.filter(a => !a.acknowledged).length;

  useEffect(() => {
    loadAlerts();
    
    // Refresh alerts periodically
    const interval = setInterval(loadAlerts, 60000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    // Close dropdown when clicking outside
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const loadAlerts = async () => {
    try {
      const data = await alertsApi.getAll(false);
      setAlerts(data);
    } catch (error) {
      console.error('Failed to load alerts:', error);
      setAlerts(mockAlerts);
    }
  };

  const handleAcknowledge = async (alertId: string) => {
    try {
      await alertsApi.acknowledge(alertId);
      setAlerts(prev => 
        prev.map(a => a.id === alertId ? { ...a, acknowledged: true } : a)
      );
    } catch (error) {
      console.error('Failed to acknowledge alert:', error);
    }
  };

  const getAlertIcon = (type: Alert['type']) => {
    switch (type) {
      case 'error':
        return <AlertCircle size={16} className="text-accent-red" />;
      case 'warning':
        return <AlertTriangle size={16} className="text-accent-orange" />;
      case 'info':
        return <Info size={16} className="text-accent-cyan" />;
    }
  };

  const formatTime = (date: Date) => {
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const minutes = Math.floor(diff / 60000);
    
    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h ago`;
    return date.toLocaleDateString();
  };

  return (
    <div className={`relative ${className}`} ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 hover:bg-surface-700/50 rounded-lg transition-colors"
      >
        <Bell size={20} className="text-gray-400 hover:text-white" />
        {unacknowledgedCount > 0 && (
          <span className="notification-badge">{unacknowledgedCount}</span>
        )}
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-80 sm:w-96 bg-industrial-panel rounded-xl border border-surface-700/50 shadow-2xl z-50 overflow-hidden">
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-surface-700/50">
            <h3 className="font-semibold text-white">Notifications</h3>
            <button
              onClick={() => setIsOpen(false)}
              className="p-1 hover:bg-surface-700/50 rounded transition-colors"
            >
              <X size={16} className="text-gray-400" />
            </button>
          </div>

          {/* Alert List */}
          <div className="max-h-96 overflow-y-auto">
            {alerts.length === 0 ? (
              <div className="p-8 text-center text-gray-500">
                <Bell size={32} className="mx-auto mb-2 opacity-50" />
                <p>No notifications</p>
              </div>
            ) : (
              alerts.map((alert) => (
                <div
                  key={alert.id}
                  className={`
                    p-4 border-b border-surface-700/30 hover:bg-surface-700/20 transition-colors
                    ${alert.acknowledged ? 'opacity-60' : ''}
                  `}
                >
                  <div className="flex items-start gap-3">
                    <div className="mt-0.5">
                      {getAlertIcon(alert.type)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-white font-medium">
                        {alert.twinName}
                      </p>
                      <p className="text-sm text-gray-400 mt-0.5 line-clamp-2">
                        {alert.message}
                      </p>
                      <div className="flex items-center justify-between mt-2">
                        <span className="text-xs text-gray-500">
                          {formatTime(alert.timestamp)}
                        </span>
                        {!alert.acknowledged && (
                          <button
                            onClick={() => handleAcknowledge(alert.id)}
                            className="text-xs text-primary-400 hover:text-primary-300 flex items-center gap-1"
                          >
                            <CheckCircle size={12} />
                            Acknowledge
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Footer */}
          {alerts.length > 0 && (
            <div className="p-3 border-t border-surface-700/50 bg-surface-800/30">
              <button
                onClick={() => {
                  alerts.forEach(a => {
                    if (!a.acknowledged) handleAcknowledge(a.id);
                  });
                }}
                className="w-full text-center text-sm text-primary-400 hover:text-primary-300"
              >
                Mark all as read
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
