import { ReactNode, useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Box, 
  BarChart3, 
  Bell, 
  Search,
  Menu,
  X,
  Settings,
  ChevronRight
} from 'lucide-react';
import { alertsApi } from '../services/api';

interface LayoutProps {
  children: ReactNode;
}

const navItems = [
  { path: '/', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/twins', label: 'Digital Twins', icon: Box },
  { path: '/analytics', label: 'Analytics', icon: BarChart3 },
];

export function Layout({ children }: LayoutProps) {
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [alertCount, setAlertCount] = useState(0);
  const [showNotifications, setShowNotifications] = useState(false);

  useEffect(() => {
    // Fetch alert count
    alertsApi.getUnacknowledgedCount().then(setAlertCount).catch(console.error);
    
    // Update periodically
    const interval = setInterval(() => {
      alertsApi.getUnacknowledgedCount().then(setAlertCount).catch(console.error);
    }, 30000);
    
    return () => clearInterval(interval);
  }, []);

  const isActive = (path: string) => {
    if (path === '/') return location.pathname === '/';
    return location.pathname.startsWith(path);
  };

  return (
    <div className="min-h-screen bg-industrial-darker grid-bg">
      {/* Mobile header */}
      <header className="lg:hidden fixed top-0 left-0 right-0 h-16 bg-industrial-dark/95 backdrop-blur-md border-b border-surface-700/50 z-50 flex items-center justify-between px-4">
        <button
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="p-2 hover:bg-surface-700/50 rounded-lg transition-colors"
        >
          {sidebarOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
        
        <Link to="/" className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-accent-cyan to-primary-500 flex items-center justify-center">
            <Box size={18} className="text-white" />
          </div>
          <span className="font-semibold text-lg gradient-text">Digital Twins</span>
        </Link>
        
        <button
          onClick={() => setShowNotifications(!showNotifications)}
          className="p-2 hover:bg-surface-700/50 rounded-lg transition-colors relative"
        >
          <Bell size={20} />
          {alertCount > 0 && (
            <span className="notification-badge">{alertCount}</span>
          )}
        </button>
      </header>

      {/* Sidebar */}
      <aside
        className={`
          fixed top-0 left-0 h-full w-64 bg-industrial-dark/95 backdrop-blur-md border-r border-surface-700/50 z-40
          transform transition-transform duration-300 ease-out
          lg:translate-x-0
          ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
        `}
      >
        {/* Logo */}
        <div className="h-16 lg:h-20 flex items-center gap-3 px-6 border-b border-surface-700/50">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-accent-cyan to-primary-500 flex items-center justify-center shadow-lg shadow-primary-500/20">
            <Box size={22} className="text-white" />
          </div>
          <div>
            <h1 className="font-bold text-lg gradient-text">Digital Twins</h1>
            <p className="text-xs text-gray-500">Industrial Platform</p>
          </div>
        </div>

        {/* Search */}
        <div className="px-4 py-4">
          <div className="relative">
            <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
            <input
              type="text"
              placeholder="Search twins..."
              className="input pl-10 py-2 text-sm bg-surface-800/50"
            />
          </div>
        </div>

        {/* Navigation */}
        <nav className="px-3 py-2">
          <p className="px-3 text-xs font-medium text-gray-500 uppercase tracking-wider mb-2">
            Navigation
          </p>
          {navItems.map((item) => {
            const Icon = item.icon;
            const active = isActive(item.path);
            return (
              <Link
                key={item.path}
                to={item.path}
                onClick={() => setSidebarOpen(false)}
                className={`
                  flex items-center gap-3 px-3 py-2.5 rounded-lg mb-1 transition-all duration-200
                  ${active 
                    ? 'bg-primary-500/10 text-primary-400 border border-primary-500/20' 
                    : 'text-gray-400 hover:text-white hover:bg-surface-700/50'
                  }
                `}
              >
                <Icon size={20} className={active ? 'text-primary-400' : ''} />
                <span className="font-medium">{item.label}</span>
                {active && (
                  <ChevronRight size={16} className="ml-auto text-primary-400" />
                )}
              </Link>
            );
          })}
        </nav>

        {/* Quick Stats */}
        <div className="px-4 py-4 mt-auto">
          <div className="bg-surface-800/50 rounded-xl p-4 border border-surface-700/30">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs text-gray-500">System Status</span>
              <span className="flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-accent-green animate-pulse"></span>
                <span className="text-xs text-accent-green">Online</span>
              </span>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <p className="text-2xl font-bold text-white">8</p>
                <p className="text-xs text-gray-500">Active Twins</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-accent-cyan">99.7%</p>
                <p className="text-xs text-gray-500">Uptime</p>
              </div>
            </div>
          </div>
        </div>

        {/* Settings */}
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-surface-700/50">
          <button className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-gray-400 hover:text-white hover:bg-surface-700/50 transition-colors">
            <Settings size={20} />
            <span className="font-medium">Settings</span>
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main className="lg:ml-64 pt-16 lg:pt-0 min-h-screen">
        <div className="p-4 lg:p-6">
          {children}
        </div>
      </main>

      {/* Overlay for mobile sidebar */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-30 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}
    </div>
  );
}
