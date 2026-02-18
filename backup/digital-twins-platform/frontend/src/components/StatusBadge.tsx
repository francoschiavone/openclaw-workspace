import { ReactNode } from 'react';
import { TwinStatus } from '../types';

interface StatusBadgeProps {
  status: TwinStatus;
  size?: 'sm' | 'md' | 'lg';
  showDot?: boolean;
  children?: ReactNode;
}

export function StatusBadge({ status, size = 'md', showDot = true, children }: StatusBadgeProps) {
  const sizeClasses = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-2.5 py-1 text-sm',
    lg: 'px-3 py-1.5 text-base',
  };

  const statusClasses = {
    healthy: 'bg-accent-green/10 text-accent-green border-accent-green/20',
    warning: 'bg-accent-orange/10 text-accent-orange border-accent-orange/20',
    critical: 'bg-accent-red/10 text-accent-red border-accent-red/20',
    offline: 'bg-gray-500/10 text-gray-400 border-gray-500/20',
  };

  const dotColors = {
    healthy: 'bg-accent-green',
    warning: 'bg-accent-orange',
    critical: 'bg-accent-red animate-pulse',
    offline: 'bg-gray-500',
  };

  return (
    <span className={`
      inline-flex items-center gap-1.5 rounded-full border font-medium
      ${sizeClasses[size]}
      ${statusClasses[status]}
    `}>
      {showDot && (
        <span className={`w-1.5 h-1.5 rounded-full ${dotColors[status]}`} />
      )}
      {children || status.charAt(0).toUpperCase() + status.slice(1)}
    </span>
  );
}
