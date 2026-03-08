import React, { useEffect, useMemo, useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import {
  Activity,
  AlertTriangle,
  ChevronLeft,
  ChevronRight,
  Command,
  Cpu,
  Database,
  FileText,
  Image,
  Link2,
  Menu,
  Search,
  Server,
  Settings,
  X,
  Zap,
} from 'lucide-react'

const navItems = [
  { path: '/', icon: Activity, label: 'Dashboard', description: 'System overview' },
  { path: '/image', icon: Image, label: 'Image Analysis', description: 'Computer vision' },
  { path: '/text', icon: FileText, label: 'Text Intelligence', description: 'NLP processing' },
  { path: '/anomalies', icon: AlertTriangle, label: 'Anomaly Detection', description: 'Pattern analysis' },
  { path: '/knowledge', icon: Database, label: 'Knowledge Base', description: 'Data storage' },
  { path: '/system-status', icon: Settings, label: 'System Status', description: 'Health monitor' },
]

function Layout({ children, systemStatus }) {
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [contextOpen, setContextOpen] = useState(true)
  const [paletteOpen, setPaletteOpen] = useState(false)
  const [paletteQuery, setPaletteQuery] = useState('')
  const [paletteIndex, setPaletteIndex] = useState(0)
  const location = useLocation()
  const navigate = useNavigate()
  const moduleCount = Array.isArray(systemStatus?.modules)
    ? systemStatus.modules.length
    : Object.keys(systemStatus?.modules || {}).length
  const statusLabel = systemStatus?.status || 'offline'
  const statusTone =
    statusLabel === 'healthy'
      ? 'active'
      : statusLabel === 'degraded'
        ? 'warning'
        : 'error'
  const moduleEntries = useMemo(() => {
    const modules = systemStatus?.modules
    if (Array.isArray(modules)) {
      return modules.slice(0, 6).map((module, index) => [
        module?.name || `module_${index + 1}`,
        module || {},
      ])
    }
    return Object.entries(modules || {}).slice(0, 6)
  }, [systemStatus?.modules])
  const currentPage = navItems.find((item) => item.path === location.pathname)

  const isActive = (path) => location.pathname === path

  const commandItems = useMemo(() => {
    const normalized = paletteQuery.trim().toLowerCase()
    const items = navItems.map((item, index) => ({
      id: item.path,
      title: item.label,
      description: item.description,
      shortcut: `Ctrl+${index + 1}`,
      action: () => navigate(item.path),
    }))

    if (!normalized) {
      return items
    }

    return items.filter((item) => {
      return (
        item.title.toLowerCase().includes(normalized)
        || item.description.toLowerCase().includes(normalized)
      )
    })
  }, [navigate, paletteQuery])

  useEffect(() => {
    setPaletteIndex(0)
  }, [paletteQuery])

  useEffect(() => {
    if (!paletteOpen) {
      setPaletteQuery('')
      setPaletteIndex(0)
    }
  }, [paletteOpen])

  useEffect(() => {
    const onKeyDown = (event) => {
      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'k') {
        event.preventDefault()
        setPaletteOpen((open) => !open)
        return
      }

      if ((event.ctrlKey || event.metaKey) && ['1', '2', '3', '4', '5', '6'].includes(event.key)) {
        event.preventDefault()
        const item = navItems[Number(event.key) - 1]
        if (item) {
          navigate(item.path)
        }
        return
      }

      if (!paletteOpen) {
        return
      }

      if (event.key === 'Escape') {
        event.preventDefault()
        setPaletteOpen(false)
        return
      }

      if (event.key === 'ArrowDown') {
        event.preventDefault()
        setPaletteIndex((index) => {
          return Math.min(index + 1, Math.max(commandItems.length - 1, 0))
        })
        return
      }

      if (event.key === 'ArrowUp') {
        event.preventDefault()
        setPaletteIndex((index) => Math.max(index - 1, 0))
        return
      }

      if (event.key === 'Enter') {
        event.preventDefault()
        const selected = commandItems[paletteIndex]
        if (selected) {
          selected.action()
          setPaletteOpen(false)
        }
      }
    }

    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [commandItems, navigate, paletteIndex, paletteOpen])

  const handleCommandSelection = (item) => {
    item.action()
    setPaletteOpen(false)
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="topbar-left">
          <button
            type="button"
            onClick={() => setSidebarOpen((open) => !open)}
            className="icon-btn"
            aria-label="Toggle navigation"
          >
            {sidebarOpen ? <X className="w-4 h-4" /> : <Menu className="w-4 h-4" />}
          </button>
          <Link to="/" className="logo-link">
            <div className="logo-mark">
              <Cpu className="w-5 h-5" />
            </div>
            <div>
              <p className="logo-title">AETHER</p>
              <p className="logo-version">v1.0.0</p>
            </div>
          </Link>

          <nav className="breadcrumbs" aria-label="Breadcrumb">
            <span className="text-text-secondary">Fleet</span>
            <ChevronRight className="w-4 h-4 text-text-secondary" />
            <span className="text-white">{currentPage?.label || 'Dashboard'}</span>
          </nav>
        </div>

        <div className="topbar-center">
          <button type="button" onClick={() => setPaletteOpen(true)} className="search-trigger">
            <Search className="w-4 h-4" />
            <span>Command Palette</span>
            <kbd>Ctrl+K</kbd>
          </button>
        </div>

        <div className="topbar-right">
          <div className={`fleet-indicator ${statusTone}`}>
            <span className={`status-dot ${statusLabel === 'healthy' ? 'status-active' : statusLabel === 'degraded' ? 'status-processing' : 'status-error'}`} />
            <span>{statusLabel.toUpperCase()}</span>
          </div>
          <button
            type="button"
            onClick={() => setContextOpen((open) => !open)}
            className="icon-btn context-toggle"
            aria-label="Toggle context panel"
          >
            {contextOpen ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
          </button>
        </div>
      </header>

      <aside className={`sidebar-frame ${sidebarOpen ? 'expanded' : 'collapsed'}`}>
        <nav className="sidebar-nav">
          {navItems.map((item) => {
            const Icon = item.icon
            const active = isActive(item.path)

            return (
              <Link
                key={item.path}
                to={item.path}
                className={`nav-link ${active ? 'active' : ''}`}
                onClick={() => {
                  if (window.innerWidth <= 900) {
                    setSidebarOpen(false)
                  }
                }}
              >
                <Icon className="w-5 h-5" />
                {sidebarOpen && (
                  <div className="nav-label">
                    <p>{item.label}</p>
                    <p>{item.description}</p>
                  </div>
                )}
              </Link>
            )
          })}
        </nav>

        {sidebarOpen ? (
          <div className="sidebar-footer">
            <div className="status-card">
              <p className="status-card-title">Core Monitor</p>
              <div className="status-card-row">
                <span className={`status-dot ${statusLabel === 'healthy' ? 'status-active' : statusLabel === 'degraded' ? 'status-processing' : 'status-error'}`} />
                <span className="status-card-value">{statusLabel}</span>
              </div>
              <p className="status-card-meta">{moduleCount} modules available</p>
              {systemStatus?.connectionError ? (
                <p className="status-card-warning">Network degraded, retrying endpoints.</p>
              ) : null}
            </div>
          </div>
        ) : null}
      </aside>

      <main className="main-canvas">
        <div className="main-scroll bg-grid">
          {children}
        </div>
      </main>

      <aside className={`context-panel ${contextOpen ? 'expanded' : 'collapsed'}`}>
        <div className="context-header">
          <h3>Operational Context</h3>
        </div>

        <div className="context-content">
          <section className="context-section">
            <h4 className="context-section-title">System Snapshot</h4>
            <div className="context-stat">
              <Server className="w-4 h-4" />
              <span>Core</span>
              <span>{systemStatus?.coreInitialized ? 'Initialized' : 'Unavailable'}</span>
            </div>
            <div className="context-stat">
              <Activity className="w-4 h-4" />
              <span>Status</span>
              <span>{statusLabel}</span>
            </div>
            <div className="context-stat">
              <Zap className="w-4 h-4" />
              <span>Modules</span>
              <span>{moduleCount}</span>
            </div>
          </section>

          <section className="context-section">
            <h4 className="context-section-title">Model Modules</h4>
            <div className="context-list">
              {moduleEntries.length ? (
                moduleEntries.map(([name, module]) => (
                  <div key={name} className="context-item">
                    <span className={`status-dot ${module.initialized ? 'status-active' : 'status-error'}`} />
                    <span>{name.replaceAll('_', ' ')}</span>
                  </div>
                ))
              ) : (
                <div className="context-empty">No module metadata received yet.</div>
              )}
            </div>
          </section>

          <section className="context-section">
            <h4 className="context-section-title">Endpoints</h4>
            <div className="context-list">
              <a href="/health" target="_blank" rel="noreferrer" className="context-link">
                <Link2 className="w-3 h-3" />
                <span>/health</span>
              </a>
              <a href="/status" target="_blank" rel="noreferrer" className="context-link">
                <Link2 className="w-3 h-3" />
                <span>/status</span>
              </a>
              <a href="/docs" target="_blank" rel="noreferrer" className="context-link">
                <Link2 className="w-3 h-3" />
                <span>/docs</span>
              </a>
            </div>
          </section>
        </div>
      </aside>

      {paletteOpen ? (
        <div className="command-palette" role="dialog" aria-label="Command palette">
          <button type="button" className="command-backdrop" onClick={() => setPaletteOpen(false)} aria-label="Close command palette" />
          <div className="command-surface">
            <div className="command-input-row">
              <Command className="w-4 h-4 text-text-secondary" />
              <input
                type="text"
                autoFocus
                value={paletteQuery}
                onChange={(event) => setPaletteQuery(event.target.value)}
                placeholder="Search routes and jump directly..."
              />
              <kbd>ESC</kbd>
            </div>
            <div className="command-results">
              {commandItems.length ? (
                commandItems.map((item, index) => (
                  <button
                    key={item.id}
                    type="button"
                    onClick={() => handleCommandSelection(item)}
                    className={`command-item ${index === paletteIndex ? 'selected' : ''}`}
                  >
                    <div>
                      <p className="command-item-title">{item.title}</p>
                      <p className="command-item-description">{item.description}</p>
                    </div>
                    <span>{item.shortcut}</span>
                  </button>
                ))
              ) : (
                <div className="command-empty">No matching command found.</div>
              )}
            </div>
          </div>
        </div>
      ) : null}
    </div>
  )
}

export default Layout
