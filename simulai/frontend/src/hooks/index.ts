import { useState, useEffect, useCallback } from 'react';
import { DigitalTwin, SensorData } from '../types';
import { updateSensorValues } from '../data/mockData';

/**
 * Hook for real-time sensor data updates
 */
export function useRealtimeSensors(
  initialSensors: SensorData[],
  isRunning: boolean = true,
  updateInterval: number = 2000
) {
  const [sensors, setSensors] = useState<SensorData[]>(initialSensors);

  useEffect(() => {
    if (!isRunning) return;

    const interval = setInterval(() => {
      setSensors(prev => updateSensorValues(prev));
    }, updateInterval);

    return () => clearInterval(interval);
  }, [isRunning, updateInterval]);

  return { sensors, setSensors };
}

/**
 * Hook for fetching a digital twin by ID
 */
export function useTwin(id: string | undefined) {
  const [twin, setTwin] = useState<DigitalTwin | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchTwin = useCallback(async () => {
    if (!id) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`/api/twins/${id}`);
      if (!response.ok) {
        if (response.status === 404) {
          setTwin(null);
        } else {
          throw new Error('Failed to fetch twin');
        }
      } else {
        const data = await response.json();
        setTwin(data);
      }
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Unknown error'));
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchTwin();
  }, [fetchTwin]);

  return { twin, loading, error, refetch: fetchTwin };
}

/**
 * Hook for WebSocket real-time updates
 */
export function useWebSocket(url: string) {
  const [connected, setConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<any>(null);
  const wsRef = useState<WebSocket | null>(null);

  useEffect(() => {
    const ws = new WebSocket(url);
    
    ws.onopen = () => {
      setConnected(true);
    };
    
    ws.onclose = () => {
      setConnected(false);
    };
    
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setLastMessage(data);
      } catch (e) {
        console.error('Failed to parse WebSocket message:', e);
      }
    };
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
    
    return () => {
      ws.close();
    };
  }, [url]);

  const sendMessage = useCallback((data: any) => {
    if (wsRef[0]?.readyState === WebSocket.OPEN) {
      wsRef[0].send(JSON.stringify(data));
    }
  }, []);

  return { connected, lastMessage, sendMessage };
}

/**
 * Hook for debounced search
 */
export function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
}

/**
 * Hook for local storage persistence
 */
export function useLocalStorage<T>(key: string, initialValue: T): [T, (value: T) => void] {
  const [storedValue, setStoredValue] = useState<T>(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.error('Error reading from localStorage:', error);
      return initialValue;
    }
  });

  const setValue = useCallback((value: T) => {
    try {
      setStoredValue(value);
      window.localStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
      console.error('Error writing to localStorage:', error);
    }
  }, [key]);

  return [storedValue, setValue];
}

/**
 * Hook for window size
 */
export function useWindowSize() {
  const [size, setSize] = useState({
    width: typeof window !== 'undefined' ? window.innerWidth : 0,
    height: typeof window !== 'undefined' ? window.innerHeight : 0,
  });

  useEffect(() => {
    const handleResize = () => {
      setSize({
        width: window.innerWidth,
        height: window.innerHeight,
      });
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return size;
}

/**
 * Hook for interval
 */
export function useInterval(callback: () => void, delay: number | null) {
  useEffect(() => {
    if (delay === null) return;
    
    const id = setInterval(callback, delay);
    return () => clearInterval(id);
  }, [callback, delay]);
}
