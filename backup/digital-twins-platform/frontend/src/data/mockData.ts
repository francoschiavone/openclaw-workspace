import { DigitalTwin, SensorData, Alert, KPIData, AnalyticsInsight, MaintenanceSchedule } from '../types';

// Helper to generate random sensor values
const randomValue = (min: number, max: number) => Math.random() * (max - min) + min;
const randomStatus = (): 'healthy' | 'warning' | 'critical' => {
  const rand = Math.random();
  if (rand > 0.85) return 'critical';
  if (rand > 0.7) return 'warning';
  return 'healthy';
};

// Generate sensor data for a twin
export const generateSensors = (twinType: string): SensorData[] => {
  const baseSensors: SensorData[] = [
    {
      id: 'temp-1',
      name: 'Temperature',
      type: 'temperature',
      value: randomValue(20, 120),
      unit: '°C',
      min: 0,
      max: 150,
      timestamp: new Date(),
      status: 'healthy',
    },
    {
      id: 'pressure-1',
      name: 'Pressure',
      type: 'pressure',
      value: randomValue(1, 10),
      unit: 'bar',
      min: 0,
      max: 15,
      timestamp: new Date(),
      status: 'healthy',
    },
    {
      id: 'vibration-1',
      name: 'Vibration',
      type: 'vibration',
      value: randomValue(0, 100),
      unit: 'mm/s',
      min: 0,
      max: 120,
      timestamp: new Date(),
      status: 'healthy',
    },
    {
      id: 'power-1',
      name: 'Power Consumption',
      type: 'power',
      value: randomValue(100, 500),
      unit: 'kW',
      min: 0,
      max: 600,
      timestamp: new Date(),
      status: 'healthy',
    },
    {
      id: 'flow-1',
      name: 'Flow Rate',
      type: 'flow',
      value: randomValue(10, 100),
      unit: 'L/min',
      min: 0,
      max: 120,
      timestamp: new Date(),
      status: 'healthy',
    },
    {
      id: 'humidity-1',
      name: 'Humidity',
      type: 'humidity',
      value: randomValue(30, 80),
      unit: '%',
      min: 0,
      max: 100,
      timestamp: new Date(),
      status: 'healthy',
    },
  ];

  // Update status based on value
  return baseSensors.map(sensor => {
    const range = sensor.max - sensor.min;
    const warningThreshold = sensor.min + range * 0.75;
    const criticalThreshold = sensor.min + range * 0.9;
    
    let status: 'healthy' | 'warning' | 'critical' = 'healthy';
    if (sensor.value >= criticalThreshold) {
      status = 'critical';
    } else if (sensor.value >= warningThreshold) {
      status = 'warning';
    }
    
    return { ...sensor, status };
  });
};

// Mock Digital Twins
export const mockTwins: DigitalTwin[] = [
  {
    id: 'twin-001',
    name: 'Assembly Line A',
    type: 'factory',
    status: 'healthy',
    description: 'Main assembly line for product manufacturing with robotic arms and conveyor systems.',
    location: 'Building 1, Floor 2',
    createdAt: new Date('2024-01-15'),
    lastUpdated: new Date(),
    sensors: generateSensors('factory'),
    metadata: { manufacturer: 'Siemens', model: 'AL-2000', firmware: 'v2.4.1' },
  },
  {
    id: 'twin-002',
    name: 'CNC Machine #12',
    type: 'machine',
    status: 'warning',
    description: 'High-precision CNC milling machine for metal components.',
    location: 'Building 1, Floor 1',
    createdAt: new Date('2024-02-20'),
    lastUpdated: new Date(),
    sensors: generateSensors('machine'),
    metadata: { manufacturer: 'Haas', model: 'VF-4SS', firmware: 'v3.1.0' },
  },
  {
    id: 'twin-003',
    name: 'AGV Robot Fleet',
    type: 'robot',
    status: 'healthy',
    description: 'Autonomous guided vehicles for material transport across the facility.',
    location: 'All Buildings',
    createdAt: new Date('2024-03-10'),
    lastUpdated: new Date(),
    sensors: generateSensors('robot'),
    metadata: { count: 12, manufacturer: 'KUKA', model: 'MP-500' },
  },
  {
    id: 'twin-004',
    name: 'HVAC System',
    type: 'sensor',
    status: 'critical',
    description: 'Central heating, ventilation, and air conditioning system.',
    location: 'Building 2, Basement',
    createdAt: new Date('2023-11-05'),
    lastUpdated: new Date(),
    sensors: generateSensors('sensor'),
    metadata: { manufacturer: 'Carrier', model: 'XPower-5000', zones: 8 },
  },
  {
    id: 'twin-005',
    name: 'Injection Molder B',
    type: 'machine',
    status: 'healthy',
    description: 'Plastic injection molding machine for component production.',
    location: 'Building 1, Floor 3',
    createdAt: new Date('2024-01-28'),
    lastUpdated: new Date(),
    sensors: generateSensors('machine'),
    metadata: { manufacturer: 'Engel', model: 'victory-3300', firmware: 'v5.2.0' },
  },
  {
    id: 'twin-006',
    name: 'Delivery Drone Unit',
    type: 'vehicle',
    status: 'offline',
    description: 'Autonomous delivery drone for inter-facility logistics.',
    location: 'Hangar Bay 1',
    createdAt: new Date('2024-04-01'),
    lastUpdated: new Date(Date.now() - 3600000),
    sensors: generateSensors('vehicle'),
    metadata: { manufacturer: 'DJI', model: 'FlyCart-30', range: '28km' },
  },
  {
    id: 'twin-007',
    name: 'Packaging Line C',
    type: 'factory',
    status: 'healthy',
    description: 'Automated packaging and labeling system.',
    location: 'Building 2, Floor 1',
    createdAt: new Date('2024-02-14'),
    lastUpdated: new Date(),
    sensors: generateSensors('factory'),
    metadata: { manufacturer: 'Bosch', model: 'Pack-400', throughput: '120/min' },
  },
  {
    id: 'twin-008',
    name: 'Industrial Arm R7',
    type: 'robot',
    status: 'warning',
    description: '6-axis industrial robotic arm for precision welding.',
    location: 'Building 1, Floor 2',
    createdAt: new Date('2024-03-22'),
    lastUpdated: new Date(),
    sensors: generateSensors('robot'),
    metadata: { manufacturer: 'ABB', model: 'IRB 6700', payload: '235kg' },
  },
];

// Mock Alerts
export const mockAlerts: Alert[] = [
  {
    id: 'alert-001',
    twinId: 'twin-004',
    twinName: 'HVAC System',
    type: 'error',
    message: 'Compressor temperature exceeding safe limits. Immediate attention required.',
    timestamp: new Date(Date.now() - 300000),
    acknowledged: false,
  },
  {
    id: 'alert-002',
    twinId: 'twin-002',
    twinName: 'CNC Machine #12',
    type: 'warning',
    message: 'Spindle vibration levels above normal. Schedule maintenance recommended.',
    timestamp: new Date(Date.now() - 1800000),
    acknowledged: false,
  },
  {
    id: 'alert-003',
    twinId: 'twin-008',
    twinName: 'Industrial Arm R7',
    type: 'warning',
    message: 'Joint 4 motor showing signs of wear. Predictive maintenance suggested.',
    timestamp: new Date(Date.now() - 3600000),
    acknowledged: true,
  },
  {
    id: 'alert-004',
    twinId: 'twin-006',
    twinName: 'Delivery Drone Unit',
    type: 'info',
    message: 'Scheduled maintenance window started. Unit offline.',
    timestamp: new Date(Date.now() - 7200000),
    acknowledged: true,
  },
  {
    id: 'alert-005',
    twinId: 'twin-001',
    twinName: 'Assembly Line A',
    type: 'info',
    message: 'Firmware update available v2.5.0 with performance improvements.',
    timestamp: new Date(Date.now() - 86400000),
    acknowledged: false,
  },
];

// Mock KPIs
export const mockKPIs: KPIData[] = [
  {
    label: 'Active Twins',
    value: 8,
    change: 2,
    changeLabel: 'vs last month',
    trend: 'up',
    status: 'healthy',
  },
  {
    label: 'Overall Efficiency',
    value: '94.2%',
    change: 3.1,
    changeLabel: 'vs last week',
    trend: 'up',
    unit: '%',
  },
  {
    label: 'Active Alerts',
    value: 5,
    change: -2,
    changeLabel: 'vs yesterday',
    trend: 'down',
    status: 'warning',
  },
  {
    label: 'Avg. Response Time',
    value: '23ms',
    change: -5,
    changeLabel: 'vs baseline',
    trend: 'down',
  },
  {
    label: 'Uptime',
    value: '99.7%',
    trend: 'stable',
  },
  {
    label: 'Energy Consumption',
    value: '2.4MW',
    change: -8,
    changeLabel: 'vs last week',
    trend: 'down',
    unit: 'MW',
  },
];

// Mock Analytics Insights
export const mockInsights: AnalyticsInsight[] = [
  {
    id: 'insight-001',
    type: 'prediction',
    title: 'Predicted Maintenance: CNC Machine #12',
    description: 'Based on vibration patterns, spindle bearing replacement recommended within 14 days to prevent failure.',
    confidence: 87,
    impact: 'high',
    twinId: 'twin-002',
    twinName: 'CNC Machine #12',
    createdAt: new Date(),
  },
  {
    id: 'insight-002',
    type: 'anomaly',
    title: 'Unusual Power Consumption Pattern',
    description: 'Assembly Line A showing 15% higher power draw during idle periods compared to baseline.',
    confidence: 92,
    impact: 'medium',
    twinId: 'twin-001',
    twinName: 'Assembly Line A',
    createdAt: new Date(Date.now() - 3600000),
  },
  {
    id: 'insight-003',
    type: 'recommendation',
    title: 'Optimize AGV Routes',
    description: 'AI analysis suggests route optimization could reduce delivery times by 12% and battery consumption by 8%.',
    confidence: 78,
    impact: 'medium',
    twinId: 'twin-003',
    twinName: 'AGV Robot Fleet',
    createdAt: new Date(Date.now() - 7200000),
  },
  {
    id: 'insight-004',
    type: 'trend',
    title: 'Temperature Trend Analysis',
    description: 'HVAC system efficiency has decreased 5% over the past month. Consider filter replacement.',
    confidence: 95,
    impact: 'low',
    twinId: 'twin-004',
    twinName: 'HVAC System',
    createdAt: new Date(Date.now() - 86400000),
  },
];

// Mock Maintenance Schedule
export const mockMaintenanceSchedule: MaintenanceSchedule[] = [
  {
    id: 'maint-001',
    twinId: 'twin-002',
    twinName: 'CNC Machine #12',
    type: 'predictive',
    scheduledDate: new Date(Date.now() + 86400000 * 3),
    estimatedDuration: 4,
    priority: 'high',
    description: 'Spindle bearing replacement based on predictive analysis.',
  },
  {
    id: 'maint-002',
    twinId: 'twin-004',
    twinName: 'HVAC System',
    type: 'corrective',
    scheduledDate: new Date(Date.now() + 3600000 * 2),
    estimatedDuration: 2,
    priority: 'high',
    description: 'Emergency compressor inspection and repair.',
  },
  {
    id: 'maint-003',
    twinId: 'twin-008',
    twinName: 'Industrial Arm R7',
    type: 'preventive',
    scheduledDate: new Date(Date.now() + 86400000 * 7),
    estimatedDuration: 3,
    priority: 'medium',
    description: 'Scheduled joint motor inspection and calibration.',
  },
  {
    id: 'maint-004',
    twinId: 'twin-001',
    twinName: 'Assembly Line A',
    type: 'preventive',
    scheduledDate: new Date(Date.now() + 86400000 * 14),
    estimatedDuration: 8,
    priority: 'low',
    description: 'Quarterly maintenance and firmware update.',
  },
];

// Generate time-series data for charts
export const generateTimeSeriesData = (
  points: number = 24,
  baseValue: number = 50,
  variance: number = 10
): { timestamp: Date; value: number }[] => {
  const now = new Date();
  const data = [];
  
  for (let i = points - 1; i >= 0; i--) {
    const timestamp = new Date(now.getTime() - i * 3600000);
    const value = baseValue + (Math.random() - 0.5) * variance * 2 + Math.sin(i / 4) * (variance / 2);
    data.push({ timestamp, value: Math.max(0, value) });
  }
  
  return data;
};

// Update sensor values for real-time simulation
export const updateSensorValues = (sensors: SensorData[]): SensorData[] => {
  return sensors.map(sensor => {
    const change = (Math.random() - 0.5) * (sensor.max - sensor.min) * 0.05;
    let newValue = sensor.value + change;
    newValue = Math.max(sensor.min, Math.min(sensor.max, newValue));
    
    const range = sensor.max - sensor.min;
    const warningThreshold = sensor.min + range * 0.75;
    const criticalThreshold = sensor.min + range * 0.9;
    
    let status: 'healthy' | 'warning' | 'critical' = 'healthy';
    if (newValue >= criticalThreshold) {
      status = 'critical';
    } else if (newValue >= warningThreshold) {
      status = 'warning';
    }
    
    return {
      ...sensor,
      value: Number(newValue.toFixed(2)),
      status,
      timestamp: new Date(),
    };
  });
};
