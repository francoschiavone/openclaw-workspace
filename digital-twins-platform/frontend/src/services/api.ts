import { DigitalTwin, Alert, AnalyticsInsight, MaintenanceSchedule, TwinFilter } from '../types';
import { mockTwins, mockAlerts, mockInsights, mockMaintenanceSchedule } from '../data/mockData';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws';

// Simulate API delay
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

// Check if we should use mock data
const USE_MOCK = import.meta.env.VITE_USE_MOCK !== 'false';

// Twins API
export const twinsApi = {
  async getAll(filters?: TwinFilter): Promise<DigitalTwin[]> {
    if (USE_MOCK) {
      await delay(300);
      let results = [...mockTwins];
      
      if (filters) {
        if (filters.search) {
          const search = filters.search.toLowerCase();
          results = results.filter(t => 
            t.name.toLowerCase().includes(search) ||
            t.description.toLowerCase().includes(search) ||
            t.location.toLowerCase().includes(search)
          );
        }
        if (filters.status !== 'all') {
          results = results.filter(t => t.status === filters.status);
        }
        if (filters.type !== 'all') {
          results = results.filter(t => t.type === filters.type);
        }
      }
      
      return results;
    }
    
    const params = new URLSearchParams();
    if (filters?.search) params.append('search', filters.search);
    if (filters?.status && filters.status !== 'all') params.append('status', filters.status);
    if (filters?.type && filters.type !== 'all') params.append('type', filters.type);
    
    const response = await fetch(`${API_BASE_URL}/twins?${params}`);
    if (!response.ok) throw new Error('Failed to fetch twins');
    return response.json();
  },

  async getById(id: string): Promise<DigitalTwin | null> {
    if (USE_MOCK) {
      await delay(200);
      return mockTwins.find(t => t.id === id) || null;
    }
    
    const response = await fetch(`${API_BASE_URL}/twins/${id}`);
    if (!response.ok) {
      if (response.status === 404) return null;
      throw new Error('Failed to fetch twin');
    }
    return response.json();
  },

  async create(twin: Omit<DigitalTwin, 'id' | 'createdAt' | 'lastUpdated'>): Promise<DigitalTwin> {
    if (USE_MOCK) {
      await delay(500);
      const newTwin: DigitalTwin = {
        ...twin,
        id: `twin-${Date.now()}`,
        createdAt: new Date(),
        lastUpdated: new Date(),
      };
      return newTwin;
    }
    
    const response = await fetch(`${API_BASE_URL}/twins`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(twin),
    });
    if (!response.ok) throw new Error('Failed to create twin');
    return response.json();
  },

  async update(id: string, updates: Partial<DigitalTwin>): Promise<DigitalTwin> {
    if (USE_MOCK) {
      await delay(300);
      const twin = mockTwins.find(t => t.id === id);
      if (!twin) throw new Error('Twin not found');
      return { ...twin, ...updates, lastUpdated: new Date() };
    }
    
    const response = await fetch(`${API_BASE_URL}/twins/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updates),
    });
    if (!response.ok) throw new Error('Failed to update twin');
    return response.json();
  },

  async delete(id: string): Promise<void> {
    if (USE_MOCK) {
      await delay(300);
      return;
    }
    
    const response = await fetch(`${API_BASE_URL}/twins/${id}`, {
      method: 'DELETE',
    });
    if (!response.ok) throw new Error('Failed to delete twin');
  },
};

// Alerts API
export const alertsApi = {
  async getAll(acknowledged?: boolean): Promise<Alert[]> {
    if (USE_MOCK) {
      await delay(200);
      let results = [...mockAlerts];
      if (acknowledged !== undefined) {
        results = results.filter(a => a.acknowledged === acknowledged);
      }
      return results.sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime());
    }
    
    const params = new URLSearchParams();
    if (acknowledged !== undefined) params.append('acknowledged', String(acknowledged));
    
    const response = await fetch(`${API_BASE_URL}/alerts?${params}`);
    if (!response.ok) throw new Error('Failed to fetch alerts');
    return response.json();
  },

  async acknowledge(id: string): Promise<void> {
    if (USE_MOCK) {
      await delay(200);
      return;
    }
    
    const response = await fetch(`${API_BASE_URL}/alerts/${id}/acknowledge`, {
      method: 'POST',
    });
    if (!response.ok) throw new Error('Failed to acknowledge alert');
  },

  async getUnacknowledgedCount(): Promise<number> {
    if (USE_MOCK) {
      return mockAlerts.filter(a => !a.acknowledged).length;
    }
    
    const response = await fetch(`${API_BASE_URL}/alerts/unacknowledged-count`);
    if (!response.ok) throw new Error('Failed to fetch alert count');
    return response.json();
  },
};

// Analytics API
export const analyticsApi = {
  async getInsights(): Promise<AnalyticsInsight[]> {
    if (USE_MOCK) {
      await delay(400);
      return mockInsights;
    }
    
    const response = await fetch(`${API_BASE_URL}/analytics/insights`);
    if (!response.ok) throw new Error('Failed to fetch insights');
    return response.json();
  },

  async getMaintenanceSchedule(): Promise<MaintenanceSchedule[]> {
    if (USE_MOCK) {
      await delay(300);
      return mockMaintenanceSchedule.sort((a, b) => 
        a.scheduledDate.getTime() - b.scheduledDate.getTime()
      );
    }
    
    const response = await fetch(`${API_BASE_URL}/analytics/maintenance`);
    if (!response.ok) throw new Error('Failed to fetch maintenance schedule');
    return response.json();
  },

  async getEfficiencyMetrics(twinId?: string): Promise<Record<string, number[]>> {
    if (USE_MOCK) {
      await delay(300);
      // Return mock efficiency data
      return {
        oee: Array.from({ length: 24 }, () => 85 + Math.random() * 10),
        availability: Array.from({ length: 24 }, () => 95 + Math.random() * 5),
        performance: Array.from({ length: 24 }, () => 90 + Math.random() * 8),
        quality: Array.from({ length: 24 }, () => 97 + Math.random() * 3),
      };
    }
    
    const url = twinId 
      ? `${API_BASE_URL}/analytics/efficiency?twinId=${twinId}`
      : `${API_BASE_URL}/analytics/efficiency`;
    
    const response = await fetch(url);
    if (!response.ok) throw new Error('Failed to fetch efficiency metrics');
    return response.json();
  },
};

// WebSocket connection for real-time updates
export class RealtimeService {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private listeners: Map<string, Set<(data: any) => void>> = new Map();

  connect() {
    if (this.ws?.readyState === WebSocket.OPEN) return;
    
    if (USE_MOCK) {
      // Simulate real-time updates with mock data
      this.startMockUpdates();
      return;
    }

    try {
      this.ws = new WebSocket(WS_URL);
      
      this.ws.onopen = () => {
        console.log('WebSocket connected');
        this.reconnectAttempts = 0;
      };
      
      this.ws.onmessage = (event) => {
        const message = JSON.parse(event.data);
        this.notifyListeners(message.type, message.payload);
      };
      
      this.ws.onclose = () => {
        this.attemptReconnect();
      };
      
      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
    } catch (error) {
      console.error('Failed to connect WebSocket:', error);
      this.attemptReconnect();
    }
  }

  private startMockUpdates() {
    // Simulate periodic updates
    setInterval(() => {
      this.notifyListeners('sensor_update', { twinId: 'all' });
    }, 2000);

    setInterval(() => {
      this.notifyListeners('status_change', { twinId: 'all' });
    }, 5000);
  }

  private attemptReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnect attempts reached');
      return;
    }
    
    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
    
    setTimeout(() => {
      console.log(`Reconnecting... Attempt ${this.reconnectAttempts}`);
      this.connect();
    }, delay);
  }

  subscribe(event: string, callback: (data: any) => void): () => void {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
    }
    this.listeners.get(event)!.add(callback);
    
    // Return unsubscribe function
    return () => {
      this.listeners.get(event)?.delete(callback);
    };
  }

  private notifyListeners(event: string, data: any) {
    this.listeners.get(event)?.forEach(callback => callback(data));
    this.listeners.get('*')?.forEach(callback => callback({ type: event, data }));
  }

  disconnect() {
    this.ws?.close();
    this.ws = null;
  }
}

export const realtimeService = new RealtimeService();
