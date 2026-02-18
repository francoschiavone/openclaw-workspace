// Digital Twins Platform Types

export type TwinStatus = 'healthy' | 'warning' | 'critical' | 'offline';

export type TwinType = 'machine' | 'factory' | 'vehicle' | 'robot' | 'sensor';

export interface SensorData {
  id: string;
  name: string;
  type: 'temperature' | 'pressure' | 'humidity' | 'vibration' | 'speed' | 'flow' | 'power';
  value: number;
  unit: string;
  min: number;
  max: number;
  timestamp: Date;
  status: TwinStatus;
}

export interface Alert {
  id: string;
  twinId: string;
  twinName: string;
  type: 'error' | 'warning' | 'info';
  message: string;
  timestamp: Date;
  acknowledged: boolean;
}

export interface DigitalTwin {
  id: string;
  name: string;
  type: TwinType;
  status: TwinStatus;
  description: string;
  location: string;
  createdAt: Date;
  lastUpdated: Date;
  sensors: SensorData[];
  metadata: Record<string, any>;
  thumbnail?: string;
}

export interface KPIData {
  label: string;
  value: number | string;
  change?: number;
  changeLabel?: string;
  unit?: string;
  trend?: 'up' | 'down' | 'stable';
  status?: TwinStatus;
}

export interface ChartDataPoint {
  timestamp: Date;
  value: number;
  [key: string]: any;
}

export interface TwinFilter {
  search: string;
  status: TwinStatus | 'all';
  type: TwinType | 'all';
}

export interface WebSocketMessage {
  type: 'sensor_update' | 'alert' | 'status_change' | 'ping';
  payload: any;
  timestamp: Date;
}

export interface AnalyticsInsight {
  id: string;
  type: 'prediction' | 'anomaly' | 'recommendation' | 'trend';
  title: string;
  description: string;
  confidence: number;
  impact: 'high' | 'medium' | 'low';
  twinId?: string;
  twinName?: string;
  createdAt: Date;
}

export interface MaintenanceSchedule {
  id: string;
  twinId: string;
  twinName: string;
  type: 'preventive' | 'corrective' | 'predictive';
  scheduledDate: Date;
  estimatedDuration: number;
  priority: 'high' | 'medium' | 'low';
  description: string;
}
