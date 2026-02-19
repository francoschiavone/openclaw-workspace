import { useState, useEffect, useRef, Suspense } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Environment, Float, Text, MeshDistortMaterial, Html } from '@react-three/drei';
import * as THREE from 'three';
import { 
  ArrowLeft, 
  Settings, 
  Power, 
  Thermometer, 
  Activity, 
  Zap, 
  Droplets,
  Wind,
  Gauge,
  Play,
  Pause,
  RotateCcw,
  Download,
  AlertTriangle,
  Clock,
  MapPin,
  Info
} from 'lucide-react';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  AreaChart,
  Area
} from 'recharts';
import { DigitalTwin, SensorData } from '../types';
import { twinsApi, realtimeService } from '../services/api';
import { mockTwins, generateTimeSeriesData, updateSensorValues } from '../data/mockData';
import { StatusBadge } from '../components/StatusBadge';

export function TwinDetail() {
  const { id } = useParams<{ id: string }>();
  const [twin, setTwin] = useState<DigitalTwin | null>(null);
  const [loading, setLoading] = useState(true);
  const [sensors, setSensors] = useState<SensorData[]>([]);
  const [chartData, setChartData] = useState<Record<string, any[]>>({});
  const [isRunning, setIsRunning] = useState(true);
  const [selectedSensor, setSelectedSensor] = useState<string | null>(null);

  useEffect(() => {
    loadTwin();
    
    // Subscribe to real-time updates
    const unsubscribe = realtimeService.subscribe('sensor_update', () => {
      if (isRunning) {
        setSensors(prev => updateSensorValues(prev));
      }
    });
    
    realtimeService.connect();
    return unsubscribe;
  }, [id, isRunning]);

  useEffect(() => {
    if (twin) {
      // Generate initial chart data for each sensor
      const data: Record<string, any[]> = {};
      twin.sensors.forEach(sensor => {
        data[sensor.id] = generateTimeSeriesData(20, sensor.value, (sensor.max - sensor.min) * 0.1);
      });
      setChartData(data);
    }
  }, [twin]);

  useEffect(() => {
    // Update chart data periodically
    if (!isRunning) return;
    
    const interval = setInterval(() => {
      setChartData(prev => {
        const newData = { ...prev };
        Object.keys(newData).forEach(sensorId => {
          const sensor = sensors.find(s => s.id === sensorId);
          if (sensor) {
            newData[sensorId] = [
              ...newData[sensorId].slice(1),
              { timestamp: new Date(), value: sensor.value }
            ];
          }
        });
        return newData;
      });
    }, 2000);
    
    return () => clearInterval(interval);
  }, [isRunning, sensors]);

  const loadTwin = async () => {
    setLoading(true);
    try {
      const data = await twinsApi.getById(id!);
      if (data) {
        setTwin(data);
        setSensors(data.sensors);
      }
    } catch (error) {
      console.error('Failed to load twin:', error);
      // Use mock data
      const mockTwin = mockTwins.find(t => t.id === id);
      if (mockTwin) {
        setTwin(mockTwin);
        setSensors(mockTwin.sensors);
      }
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
      </div>
    );
  }

  if (!twin) {
    return (
      <div className="text-center py-16">
        <h2 className="text-2xl font-bold text-white mb-4">Digital Twin Not Found</h2>
        <p className="text-gray-400 mb-6">The requested twin does not exist or has been deleted.</p>
        <Link to="/twins" className="btn-primary">
          Back to Twin List
        </Link>
      </div>
    );
  }

  const sensorIcons: Record<string, any> = {
    temperature: Thermometer,
    pressure: Gauge,
    vibration: Activity,
    power: Zap,
    flow: Droplets,
    humidity: Wind,
    speed: Activity,
  };

  const criticalSensors = sensors.filter(s => s.status === 'critical');
  const warningSensors = sensors.filter(s => s.status === 'warning');

  return (
    <div className="space-y-6 fade-in">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        <div className="flex items-center gap-4">
          <Link 
            to="/twins" 
            className="p-2 hover:bg-surface-700/50 rounded-lg transition-colors text-gray-400 hover:text-white"
          >
            <ArrowLeft size={20} />
          </Link>
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-2xl lg:text-3xl font-bold text-white">{twin.name}</h1>
              <StatusBadge status={twin.status} />
            </div>
            <div className="flex items-center gap-4 mt-1 text-sm text-gray-500">
              <span className="flex items-center gap-1">
                <MapPin size={14} />
                {twin.location}
              </span>
              <span className="flex items-center gap-1">
                <Clock size={14} />
                Updated {new Date(twin.lastUpdated).toLocaleString()}
              </span>
            </div>
          </div>
        </div>
        
        <div className="flex items-center gap-3">
          <button 
            onClick={() => setIsRunning(!isRunning)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors ${
              isRunning 
                ? 'bg-accent-orange/10 text-accent-orange border border-accent-orange/20' 
                : 'bg-accent-green/10 text-accent-green border border-accent-green/20'
            }`}
          >
            {isRunning ? <Pause size={18} /> : <Play size={18} />}
            {isRunning ? 'Pause' : 'Resume'}
          </button>
          <button className="btn-ghost flex items-center gap-2">
            <RotateCcw size={18} />
            Reset
          </button>
          <button className="btn-ghost flex items-center gap-2">
            <Download size={18} />
            Export
          </button>
          <button className="btn-secondary flex items-center gap-2">
            <Settings size={18} />
            Configure
          </button>
        </div>
      </div>

      {/* Alerts */}
      {(criticalSensors.length > 0 || warningSensors.length > 0) && (
        <div className={`
          p-4 rounded-xl border flex items-start gap-3
          ${criticalSensors.length > 0 
            ? 'bg-accent-red/5 border-accent-red/20' 
            : 'bg-accent-orange/5 border-accent-orange/20'
          }
        `}>
          <AlertTriangle className={criticalSensors.length > 0 ? 'text-accent-red' : 'text-accent-orange'} size={20} />
          <div>
            <h4 className={`font-medium ${criticalSensors.length > 0 ? 'text-accent-red' : 'text-accent-orange'}`}>
              {criticalSensors.length > 0 ? 'Critical Alert' : 'Warning'}
            </h4>
            <p className="text-sm text-gray-400 mt-1">
              {criticalSensors.length > 0 
                ? `${criticalSensors.map(s => s.name).join(', ')} exceeding critical thresholds`
                : `${warningSensors.map(s => s.name).join(', ')} approaching warning levels`
              }
            </p>
          </div>
        </div>
      )}

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        {/* 3D Viewer */}
        <div className="xl:col-span-2 card overflow-hidden" style={{ minHeight: '400px' }}>
          <div className="h-full relative">
            <Canvas camera={{ position: [0, 0, 5], fov: 50 }}>
              <Suspense fallback={null}>
                <Scene twin={twin} sensors={sensors} isRunning={isRunning} />
              </Suspense>
            </Canvas>
            
            {/* 3D Viewer Controls Overlay */}
            <div className="absolute top-4 right-4 flex flex-col gap-2">
              <button className="p-2 bg-industrial-dark/80 backdrop-blur-sm rounded-lg text-gray-400 hover:text-white border border-surface-700/50">
                <RotateCcw size={16} />
              </button>
              <button className="p-2 bg-industrial-dark/80 backdrop-blur-sm rounded-lg text-gray-400 hover:text-white border border-surface-700/50">
                <Power size={16} />
              </button>
            </div>
            
            {/* Sensor Overlay */}
            <div className="absolute bottom-4 left-4 right-4">
              <div className="flex flex-wrap gap-2">
                {sensors.slice(0, 4).map((sensor) => {
                  const Icon = sensorIcons[sensor.type] || Activity;
                  return (
                    <div
                      key={sensor.id}
                      onClick={() => setSelectedSensor(sensor.id)}
                      className={`
                        px-3 py-2 rounded-lg backdrop-blur-md cursor-pointer transition-all
                        ${sensor.status === 'critical' 
                          ? 'bg-accent-red/20 border border-accent-red/30 glow-red' 
                          : sensor.status === 'warning'
                          ? 'bg-accent-orange/20 border border-accent-orange/30'
                          : 'bg-industrial-dark/80 border border-surface-700/50'
                        }
                        ${selectedSensor === sensor.id ? 'ring-2 ring-primary-500/50' : ''}
                      `}
                    >
                      <div className="flex items-center gap-2">
                        <Icon size={14} className={
                          sensor.status === 'critical' ? 'text-accent-red' :
                          sensor.status === 'warning' ? 'text-accent-orange' : 'text-gray-400'
                        } />
                        <span className="text-xs text-gray-400">{sensor.name}</span>
                      </div>
                      <div className={`text-sm font-mono font-bold ${
                        sensor.status === 'critical' ? 'text-accent-red' :
                        sensor.status === 'warning' ? 'text-accent-orange' : 'text-white'
                      }`}>
                        {sensor.value.toFixed(1)} {sensor.unit}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </div>

        {/* Info Panel */}
        <div className="space-y-6">
          {/* Twin Info */}
          <div className="card">
            <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <Info size={18} className="text-primary-400" />
              Twin Information
            </h3>
            <div className="space-y-4">
              <div>
                <label className="text-sm text-gray-500">Description</label>
                <p className="text-gray-300 mt-1">{twin.description}</p>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm text-gray-500">Type</label>
                  <p className="text-white capitalize mt-1">{twin.type}</p>
                </div>
                <div>
                  <label className="text-sm text-gray-500">Created</label>
                  <p className="text-white mt-1">{new Date(twin.createdAt).toLocaleDateString()}</p>
                </div>
              </div>
              {twin.metadata && Object.keys(twin.metadata).length > 0 && (
                <div>
                  <label className="text-sm text-gray-500">Specifications</label>
                  <div className="mt-2 space-y-1">
                    {Object.entries(twin.metadata).map(([key, value]) => (
                      <div key={key} className="flex justify-between text-sm">
                        <span className="text-gray-500 capitalize">{key}</span>
                        <span className="text-gray-300">{String(value)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Sensor List */}
          <div className="card">
            <h3 className="text-lg font-semibold text-white mb-4">Sensors</h3>
            <div className="space-y-3">
              {sensors.map((sensor) => {
                const Icon = sensorIcons[sensor.type] || Activity;
                const percentage = ((sensor.value - sensor.min) / (sensor.max - sensor.min)) * 100;
                
                return (
                  <div 
                    key={sensor.id}
                    className={`p-3 rounded-lg border transition-colors cursor-pointer ${
                      selectedSensor === sensor.id 
                        ? 'border-primary-500/50 bg-primary-500/5' 
                        : 'border-surface-700/50 bg-surface-800/30 hover:border-surface-600/50'
                    }`}
                    onClick={() => setSelectedSensor(sensor.id)}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <Icon size={16} className={
                          sensor.status === 'critical' ? 'text-accent-red' :
                          sensor.status === 'warning' ? 'text-accent-orange' : 'text-gray-400'
                        } />
                        <span className="text-sm text-gray-300">{sensor.name}</span>
                      </div>
                      <span className={`text-sm font-mono font-bold ${
                        sensor.status === 'critical' ? 'text-accent-red' :
                        sensor.status === 'warning' ? 'text-accent-orange' : 'text-white'
                      }`}>
                        {sensor.value.toFixed(1)} {sensor.unit}
                      </span>
                    </div>
                    {/* Progress bar */}
                    <div className="h-1.5 bg-surface-700 rounded-full overflow-hidden">
                      <div 
                        className={`h-full rounded-full transition-all duration-300 ${
                          sensor.status === 'critical' ? 'bg-accent-red' :
                          sensor.status === 'warning' ? 'bg-accent-orange' : 'bg-accent-cyan'
                        }`}
                        style={{ width: `${Math.min(100, percentage)}%` }}
                      />
                    </div>
                    <div className="flex justify-between mt-1 text-xs text-gray-600">
                      <span>{sensor.min}</span>
                      <span>{sensor.max}</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>

      {/* Sensor Charts */}
      {selectedSensor && chartData[selectedSensor] && (
        <div className="card">
          <h3 className="text-lg font-semibold text-white mb-4">
            {sensors.find(s => s.id === selectedSensor)?.name} History
          </h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData[selectedSensor]}>
                <defs>
                  <linearGradient id="sensorGradient" x1="0" y1="0" x2="0" y2="1">
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
                <YAxis 
                  tick={{ fill: '#64748b', fontSize: 11 }}
                  domain={['auto', 'auto']}
                />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#1e2228', 
                    border: '1px solid #334155',
                    borderRadius: '8px'
                  }}
                  labelFormatter={(value) => new Date(value).toLocaleTimeString()}
                  formatter={(value: number) => [value.toFixed(2), 'Value']}
                />
                <Area 
                  type="monotone" 
                  dataKey="value" 
                  stroke="#00d4ff" 
                  strokeWidth={2}
                  fillOpacity={1} 
                  fill="url(#sensorGradient)" 
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* All Sensors Mini Charts */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {sensors.map((sensor) => (
          <div key={sensor.id} className="card card-hover">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                {(() => {
                  const Icon = sensorIcons[sensor.type] || Activity;
                  return <Icon size={16} className="text-gray-400" />;
                })()}
                <span className="text-sm font-medium text-white">{sensor.name}</span>
              </div>
              <StatusBadge status={sensor.status} size="sm" />
            </div>
            <div className="h-20">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData[sensor.id]?.slice(-10) || []}>
                  <Line 
                    type="monotone" 
                    dataKey="value" 
                    stroke={sensor.status === 'critical' ? '#ff3b5c' : sensor.status === 'warning' ? '#ff9500' : '#00d4ff'} 
                    strokeWidth={2}
                    dot={false}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
            <div className="mt-2 flex items-center justify-between">
              <span className={`text-lg font-mono font-bold ${
                sensor.status === 'critical' ? 'text-accent-red' :
                sensor.status === 'warning' ? 'text-accent-orange' : 'text-white'
              }`}>
                {sensor.value.toFixed(1)}
              </span>
              <span className="text-sm text-gray-500">{sensor.unit}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// 3D Scene Component
function Scene({ twin, sensors, isRunning }: { twin: DigitalTwin; sensors: SensorData[]; isRunning: boolean }) {
  const groupRef = useRef<THREE.Group>(null);
  const criticalSensor = sensors.find(s => s.status === 'critical');
  
  // Rotate the model
  useFrame((state, delta) => {
    if (groupRef.current && isRunning) {
      groupRef.current.rotation.y += delta * 0.2;
    }
  });

  // Determine model type based on twin type
  const renderModel = () => {
    const tempSensor = sensors.find(s => s.type === 'temperature');
    const tempValue = tempSensor ? (tempSensor.value - tempSensor.min) / (tempSensor.max - tempSensor.min) : 0.5;
    
    switch (twin.type) {
      case 'machine':
        return <MachineModel tempValue={tempValue} isRunning={isRunning} hasAlert={!!criticalSensor} />;
      case 'factory':
        return <FactoryModel isRunning={isRunning} hasAlert={!!criticalSensor} />;
      case 'robot':
        return <RobotModel isRunning={isRunning} hasAlert={!!criticalSensor} />;
      case 'vehicle':
        return <VehicleModel isRunning={isRunning} hasAlert={!!criticalSensor} />;
      default:
        return <SensorModel isRunning={isRunning} hasAlert={!!criticalSensor} />;
    }
  };

  return (
    <>
      <ambientLight intensity={0.3} />
      <directionalLight position={[10, 10, 5]} intensity={1} />
      <pointLight position={[-10, -10, -10]} intensity={0.5} color="#00d4ff" />
      {criticalSensor && <pointLight position={[0, 0, 0]} intensity={2} color="#ff3b5c" distance={5} />}
      
      <Float speed={1} rotationIntensity={0.2} floatIntensity={0.5}>
        <group ref={groupRef}>
          {renderModel()}
        </group>
      </Float>
      
      <Environment preset="city" />
      <OrbitControls 
        enableZoom={true} 
        enablePan={true}
        minDistance={3}
        maxDistance={10}
      />
    </>
  );
}

// Machine 3D Model
function MachineModel({ tempValue, isRunning, hasAlert }: { tempValue: number; isRunning: boolean; hasAlert: boolean }) {
  const coreRef = useRef<THREE.Mesh>(null);
  const glowRef = useRef<THREE.Mesh>(null);
  
  useFrame((state) => {
    if (coreRef.current && isRunning) {
      coreRef.current.rotation.y += 0.05;
    }
    if (glowRef.current) {
      const scale = 1 + Math.sin(state.clock.elapsedTime * 3) * 0.05;
      glowRef.current.scale.set(scale, scale, scale);
    }
  });

  const coreColor = hasAlert 
    ? new THREE.Color('#ff3b5c')
    : new THREE.Color().lerpColors(
        new THREE.Color('#00d4ff'),
        new THREE.Color('#ff9500'),
        tempValue
      );

  return (
    <group>
      {/* Base */}
      <mesh position={[0, -1, 0]}>
        <boxGeometry args={[2, 0.3, 2]} />
        <meshStandardMaterial color="#2a2d35" metalness={0.8} roughness={0.2} />
      </mesh>
      
      {/* Main body */}
      <mesh position={[0, 0, 0]}>
        <cylinderGeometry args={[0.8, 1, 1.5, 32]} />
        <meshStandardMaterial color="#3a3d45" metalness={0.6} roughness={0.3} />
      </mesh>
      
      {/* Core (animated) */}
      <mesh ref={coreRef} position={[0, 0.3, 0]}>
        <cylinderGeometry args={[0.4, 0.4, 0.8, 32]} />
        <meshStandardMaterial 
          color={coreColor} 
          emissive={coreColor}
          emissiveIntensity={0.5}
          metalness={0.9} 
          roughness={0.1} 
        />
      </mesh>
      
      {/* Glow effect */}
      {hasAlert && (
        <mesh ref={glowRef} position={[0, 0.3, 0]}>
          <sphereGeometry args={[0.6, 32, 32]} />
          <MeshDistortMaterial 
            color="#ff3b5c" 
            transparent 
            opacity={0.3}
            distort={0.4}
            speed={2}
          />
        </mesh>
      )}
      
      {/* Arms */}
      {[0, 1, 2, 3].map((i) => (
        <mesh 
          key={i} 
          position={[
            Math.cos((i * Math.PI) / 2) * 1.2,
            0.5,
            Math.sin((i * Math.PI) / 2) * 1.2
          ]}
          rotation={[0, (i * Math.PI) / 2, 0]}
        >
          <boxGeometry args={[0.6, 0.2, 0.2]} />
          <meshStandardMaterial color="#4a4d55" metalness={0.7} roughness={0.3} />
        </mesh>
      ))}
      
      {/* Top dome */}
      <mesh position={[0, 1.1, 0]}>
        <sphereGeometry args={[0.5, 32, 32, 0, Math.PI * 2, 0, Math.PI / 2]} />
        <meshStandardMaterial 
          color="#00d4ff" 
          transparent 
          opacity={0.6}
          metalness={0.9} 
          roughness={0.1} 
        />
      </mesh>
    </group>
  );
}

// Factory 3D Model
function FactoryModel({ isRunning, hasAlert }: { isRunning: boolean; hasAlert: boolean }) {
  const smokeRef = useRef<THREE.Mesh>(null);
  
  useFrame((state) => {
    if (smokeRef.current && isRunning) {
      smokeRef.current.position.y = 1.8 + Math.sin(state.clock.elapsedTime * 2) * 0.1;
    }
  });

  return (
    <group>
      {/* Main building */}
      <mesh position={[0, 0, 0]}>
        <boxGeometry args={[2.5, 1.2, 1.5]} />
        <meshStandardMaterial color="#2a3040" metalness={0.5} roughness={0.5} />
      </mesh>
      
      {/* Roof */}
      <mesh position={[0, 0.8, 0]}>
        <boxGeometry args={[2.7, 0.4, 1.7]} />
        <meshStandardMaterial color="#1a2030" metalness={0.6} roughness={0.4} />
      </mesh>
      
      {/* Chimney */}
      <mesh position={[0.8, 1.3, 0]}>
        <cylinderGeometry args={[0.15, 0.2, 1, 16]} />
        <meshStandardMaterial color="#3a4050" metalness={0.7} roughness={0.3} />
      </mesh>
      
      {/* Smoke */}
      {isRunning && (
        <mesh ref={smokeRef} position={[0.8, 1.8, 0]}>
          <sphereGeometry args={[0.2, 16, 16]} />
          <MeshDistortMaterial 
            color="#666" 
            transparent 
            opacity={0.4}
            distort={0.8}
            speed={1}
          />
        </mesh>
      )}
      
      {/* Windows */}
      {[-0.6, 0, 0.6].map((x, i) => (
        <mesh key={i} position={[x, 0.2, 0.76]}>
          <boxGeometry args={[0.4, 0.4, 0.02]} />
          <meshStandardMaterial 
            color={hasAlert ? "#ff3b5c" : "#00d4ff"} 
            emissive={hasAlert ? "#ff3b5c" : "#00d4ff"}
            emissiveIntensity={0.5}
          />
        </mesh>
      ))}
      
      {/* Side building */}
      <mesh position={[-1.2, -0.2, 0]}>
        <boxGeometry args={[0.8, 0.8, 1.5]} />
        <meshStandardMaterial color="#252a35" metalness={0.5} roughness={0.5} />
      </mesh>
    </group>
  );
}

// Robot 3D Model
function RobotModel({ isRunning, hasAlert }: { isRunning: boolean; hasAlert: boolean }) {
  const armRef = useRef<THREE.Group>(null);
  
  useFrame((state) => {
    if (armRef.current && isRunning) {
      armRef.current.rotation.z = Math.sin(state.clock.elapsedTime * 2) * 0.3;
    }
  });

  return (
    <group>
      {/* Base */}
      <mesh position={[0, -0.8, 0]}>
        <cylinderGeometry args={[0.6, 0.7, 0.3, 32]} />
        <meshStandardMaterial color="#2a3040" metalness={0.8} roughness={0.2} />
      </mesh>
      
      {/* Body */}
      <mesh position={[0, -0.3, 0]}>
        <cylinderGeometry args={[0.3, 0.4, 0.8, 32]} />
        <meshStandardMaterial color="#3a4050" metalness={0.7} roughness={0.3} />
      </mesh>
      
      {/* Shoulder */}
      <mesh position={[0, 0.3, 0]}>
        <sphereGeometry args={[0.25, 32, 32]} />
        <meshStandardMaterial 
          color={hasAlert ? "#ff3b5c" : "#00d4ff"} 
          emissive={hasAlert ? "#ff3b5c" : "#00d4ff"}
          emissiveIntensity={0.3}
          metalness={0.8} 
          roughness={0.2} 
        />
      </mesh>
      
      {/* Arm group */}
      <group ref={armRef} position={[0, 0.3, 0]}>
        {/* Upper arm */}
        <mesh position={[0.4, 0, 0]}>
          <boxGeometry args={[0.6, 0.15, 0.15]} />
          <meshStandardMaterial color="#4a5060" metalness={0.7} roughness={0.3} />
        </mesh>
        
        {/* Elbow */}
        <mesh position={[0.7, 0, 0]}>
          <sphereGeometry args={[0.1, 16, 16]} />
          <meshStandardMaterial color="#00d4ff" metalness={0.8} roughness={0.2} />
        </mesh>
        
        {/* Lower arm */}
        <mesh position={[0.95, -0.15, 0]} rotation={[0, 0, -0.5]}>
          <boxGeometry args={[0.5, 0.12, 0.12]} />
          <meshStandardMaterial color="#4a5060" metalness={0.7} roughness={0.3} />
        </mesh>
        
        {/* End effector */}
        <mesh position={[1.2, -0.35, 0]}>
          <coneGeometry args={[0.1, 0.2, 16]} />
          <meshStandardMaterial color="#ff9500" metalness={0.6} roughness={0.4} />
        </mesh>
      </group>
      
      {/* Head */}
      <mesh position={[0, 0.7, 0]}>
        <boxGeometry args={[0.3, 0.25, 0.25]} />
        <meshStandardMaterial color="#3a4050" metalness={0.7} roughness={0.3} />
      </mesh>
      
      {/* Eyes */}
      {[-0.08, 0.08].map((x, i) => (
        <mesh key={i} position={[x, 0.72, 0.13]}>
          <sphereGeometry args={[0.04, 16, 16]} />
          <meshStandardMaterial 
            color={hasAlert ? "#ff3b5c" : "#00ff88"} 
            emissive={hasAlert ? "#ff3b5c" : "#00ff88"}
            emissiveIntensity={0.8}
          />
        </mesh>
      ))}
    </group>
  );
}

// Vehicle 3D Model
function VehicleModel({ isRunning, hasAlert }: { isRunning: boolean; hasAlert: boolean }) {
  const propRef = useRef<THREE.Group>(null);
  
  useFrame((state) => {
    if (propRef.current && isRunning) {
      propRef.current.rotation.y += 0.3;
    }
  });

  return (
    <group>
      {/* Body */}
      <mesh position={[0, 0, 0]}>
        <boxGeometry args={[1.5, 0.3, 1]} />
        <meshStandardMaterial color="#2a3545" metalness={0.7} roughness={0.3} />
      </mesh>
      
      {/* Cabin */}
      <mesh position={[0, 0.3, 0]}>
        <boxGeometry args={[0.8, 0.3, 0.8]} />
        <meshStandardMaterial 
          color="#1a2535" 
          transparent 
          opacity={0.8}
          metalness={0.8} 
          roughness={0.2} 
        />
      </mesh>
      
      {/* Wheels */}
      {[[-0.5, -0.15, 0.5], [-0.5, -0.15, -0.5], [0.5, -0.15, 0.5], [0.5, -0.15, -0.5]].map((pos, i) => (
        <mesh key={i} position={pos as [number, number, number]} rotation={[Math.PI / 2, 0, 0]}>
          <cylinderGeometry args={[0.15, 0.15, 0.1, 16]} />
          <meshStandardMaterial color="#1a1a1a" metalness={0.3} roughness={0.8} />
        </mesh>
      ))}
      
      {/* Sensor array */}
      <mesh position={[0, 0.55, 0]}>
        <cylinderGeometry args={[0.1, 0.15, 0.2, 16]} />
        <meshStandardMaterial 
          color={hasAlert ? "#ff3b5c" : "#00d4ff"} 
          emissive={hasAlert ? "#ff3b5c" : "#00d4ff"}
          emissiveIntensity={0.5}
          metalness={0.9} 
          roughness={0.1} 
        />
      </mesh>
      
      {/* Rotating sensor */}
      <group ref={propRef} position={[0, 0.65, 0]}>
        <mesh>
          <boxGeometry args={[0.3, 0.05, 0.05]} />
          <meshStandardMaterial color="#3a4555" metalness={0.8} roughness={0.2} />
        </mesh>
      </group>
      
      {/* Lights */}
      {[[-0.6, 0, 0.4], [-0.6, 0, -0.4]].map((pos, i) => (
        <mesh key={i} position={pos as [number, number, number]}>
          <sphereGeometry args={[0.05, 16, 16]} />
          <meshStandardMaterial 
            color="#00d4ff" 
            emissive="#00d4ff"
            emissiveIntensity={0.8}
          />
        </mesh>
      ))}
    </group>
  );
}

// Sensor 3D Model
function SensorModel({ isRunning, hasAlert }: { isRunning: boolean; hasAlert: boolean }) {
  const pulseRef = useRef<THREE.Mesh>(null);
  
  useFrame((state) => {
    if (pulseRef.current && isRunning) {
      const scale = 1 + Math.sin(state.clock.elapsedTime * 4) * 0.1;
      pulseRef.current.scale.set(scale, scale, scale);
    }
  });

  return (
    <group>
      {/* Base */}
      <mesh position={[0, -0.5, 0]}>
        <cylinderGeometry args={[0.4, 0.5, 0.3, 32]} />
        <meshStandardMaterial color="#2a3040" metalness={0.8} roughness={0.2} />
      </mesh>
      
      {/* Body */}
      <mesh position={[0, 0, 0]}>
        <cylinderGeometry args={[0.3, 0.35, 0.8, 32]} />
        <meshStandardMaterial color="#3a4050" metalness={0.7} roughness={0.3} />
      </mesh>
      
      {/* Core sensor */}
      <mesh ref={pulseRef} position={[0, 0.5, 0]}>
        <sphereGeometry args={[0.25, 32, 32]} />
        <meshStandardMaterial 
          color={hasAlert ? "#ff3b5c" : "#00d4ff"} 
          emissive={hasAlert ? "#ff3b5c" : "#00d4ff"}
          emissiveIntensity={0.6}
          metalness={0.9} 
          roughness={0.1} 
        />
      </mesh>
      
      {/* Ring */}
      <mesh position={[0, 0.5, 0]} rotation={[Math.PI / 2, 0, 0]}>
        <torusGeometry args={[0.35, 0.02, 16, 32]} />
        <meshStandardMaterial 
          color={hasAlert ? "#ff3b5c" : "#00ff88"} 
          emissive={hasAlert ? "#ff3b5c" : "#00ff88"}
          emissiveIntensity={0.4}
          metalness={0.9} 
          roughness={0.1} 
        />
      </mesh>
      
      {/* Antenna */}
      <mesh position={[0, 0.9, 0]}>
        <cylinderGeometry args={[0.02, 0.02, 0.4, 8]} />
        <meshStandardMaterial color="#4a5060" metalness={0.8} roughness={0.2} />
      </mesh>
      
      {/* Antenna tip */}
      <mesh position={[0, 1.15, 0]}>
        <sphereGeometry args={[0.05, 16, 16]} />
        <meshStandardMaterial 
          color="#ff9500" 
          emissive="#ff9500"
          emissiveIntensity={0.8}
        />
      </mesh>
    </group>
  );
}
