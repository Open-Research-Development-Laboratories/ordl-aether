import React, { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { 
  Activity, 
  Image, 
  FileText, 
  AlertTriangle, 
  Database, 
  Settings,
  Menu,
  X,
  Cpu,
  Zap
} from 'lucide-react'

const navItems = [
  { path: '/', icon: Activity, label: 'Dashboard', description: 'System overview' },
  { path: '/image', icon: Image, label: 'Image Analysis', description: 'Computer vision' },
  { path: '/text', icon: FileText, label: 'Text Intelligence', description: 'NLP processing' },
  { path: '/anomalies', icon: AlertTriangle, label: 'Anomaly Detection', description: 'Pattern analysis' },
  { path: '/knowledge', icon: Database, label: 'Knowledge Base', description: 'Data storage' },
  { path: '/status', icon: Settings, label: 'System Status', description: 'Health monitor' },
]

function Layout({ children, systemStatus }) {
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const location = useLocation()

  const isActive = (path) => location.pathname === path

  return (
    <div className="min-h-screen bg-bg-dark flex">
      {/* Sidebar */}
      <aside 
        className={`${sidebarOpen ? 'w-72' : 'w-20'} transition-all duration-300 bg-bg-card border-r border-border flex flex-col`}
      >
        {/* Logo */}
        <div className="p-6 border-b border-border">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-accent to-purple-600 flex items-center justify-center">
              <Cpu className="w-6 h-6 text-white" />
            </div>
            {sidebarOpen && (
              <div>
                <h1 className="text-xl font-bold text-white">AETHER</h1>
                <p className="text-xs text-text-secondary">v1.0.0</p>
              </div>
            )}
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-2">
          {navItems.map((item) => {
            const Icon = item.icon
            const active = isActive(item.path)
            
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
                  active 
                    ? 'bg-primary/20 text-accent border border-accent/30' 
                    : 'text-text-secondary hover:text-white hover:bg-white/5'
                }`}
              >
                <Icon className={`w-5 h-5 ${active ? 'text-accent' : ''}`} />
                {sidebarOpen && (
                  <div className="flex-1">
                    <p className="font-medium">{item.label}</p>
                    <p className="text-xs text-text-secondary">{item.description}</p>
                  </div>
                )}
              </Link>
            )
          })}
        </nav>

        {/* System Status */}
        {sidebarOpen && (
          <div className="p-4 border-t border-border">
            <div className="glass rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <div className={`status-dot ${systemStatus?.status === 'healthy' ? 'status-active' : 'status-error'}`}></div>
                <span className="text-sm font-medium">System {systemStatus?.status}</span>
              </div>
              <p className="text-xs text-text-secondary">
                {systemStatus?.modules?.length || 0} modules active
              </p>
            </div>
          </div>
        )}

        {/* Toggle */}
        <button
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="p-4 border-t border-border text-text-secondary hover:text-white transition-colors"
        >
          {sidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
        </button>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto bg-grid">
        <div className="p-8">
          {children}
        </div>
      </main>
    </div>
  )
}

export default Layout