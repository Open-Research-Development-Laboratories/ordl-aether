import React, { useEffect, useMemo, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'

const navItems = [
  { path: '/', en: 'DASHBOARD', jp: 'ダッシュボード', description: 'SYSTEM OVERVIEW', mark: '[■]' },
  { path: '/image', en: 'IMAGE ANALYSIS', jp: '画像分析', description: 'COMPUTER VISION', mark: '[ ]' },
  { path: '/text', en: 'TEXT INTELLIGENCE', jp: 'テキスト分析', description: 'NLP PROCESSING', mark: '[ ]' },
  { path: '/anomalies', en: 'ANOMALY DETECTION', jp: '異常検出', description: 'PATTERN ANALYSIS', mark: '[ ]' },
  { path: '/knowledge', en: 'KNOWLEDGE BASE', jp: '知識ベース', description: 'DATA STORAGE', mark: '[ ]' },
  { path: '/system-status', en: 'SYSTEM STATUS', jp: 'システム状態', description: 'HEALTH MONITOR', mark: '[◐]' },
]

function formatUptime(seconds) {
  const hrs = Math.floor(seconds / 3600).toString().padStart(2, '0')
  const mins = Math.floor((seconds % 3600) / 60).toString().padStart(2, '0')
  const secs = (seconds % 60).toString().padStart(2, '0')
  return `${hrs}:${mins}:${secs}`
}

function Layout({ children, systemStatus }) {
  const location = useLocation()
  const uiRevision = 'UI REV 2026-03-08.4'
  const [uptimeSeconds, setUptimeSeconds] = useState(() => Math.floor(Math.random() * 86400))

  const moduleEntries = useMemo(() => {
    const modules = systemStatus?.modules
    if (Array.isArray(modules)) {
      return modules.slice(0, 3).map((module, index) => [
        module?.name || `module_${index + 1}`,
        module || {},
      ])
    }
    return Object.entries(modules || {}).slice(0, 3)
  }, [systemStatus?.modules])

  const moduleCount = Array.isArray(systemStatus?.modules)
    ? systemStatus.modules.length
    : Object.keys(systemStatus?.modules || {}).length

  const statusLabel = (systemStatus?.status || 'offline').toLowerCase()
  const coreInitialized = Boolean(systemStatus?.coreInitialized ?? systemStatus?.core_initialized)
  const hasConnectionError = Boolean(systemStatus?.connectionError)
  const statusTone = hasConnectionError
    ? 'inactive'
    : statusLabel === 'healthy' && coreInitialized
      ? 'active'
      : statusLabel === 'healthy' || statusLabel === 'degraded'
        ? 'warning'
        : 'inactive'
  const statusText = hasConnectionError
    ? 'SYSTEM.OFFLINE'
    : statusLabel === 'healthy' && coreInitialized
      ? 'SYSTEM.ONLINE'
      : statusLabel === 'healthy' || statusLabel === 'degraded'
        ? 'SYSTEM.WARMING'
        : 'SYSTEM.OFFLINE'

  useEffect(() => {
    const timer = window.setInterval(() => {
      setUptimeSeconds((value) => value + 1)
    }, 1000)

    return () => window.clearInterval(timer)
  }, [])

  useEffect(() => {
    const slider = document.getElementById('contrast-slider')
    if (!slider) {
      return undefined
    }

    const clampBrightness = (value) => {
      const numeric = Number(value)
      if (Number.isNaN(numeric)) {
        return 1
      }
      return Math.min(5, Math.max(0.5, numeric))
    }

    const applyBrightness = (value) => {
      const numericValue = clampBrightness(value)
      document.documentElement.style.setProperty('--text-brightness', String(numericValue))
      window.localStorage.setItem('textBrightness', String(numericValue))
      slider.value = String(numericValue)
    }

    const storedValue = window.localStorage.getItem('textBrightness')
    const initialValue = storedValue !== null ? clampBrightness(storedValue) : 1
    slider.value = String(initialValue)
    applyBrightness(slider.value)

    const onInput = (event) => applyBrightness(event.target.value)
    slider.addEventListener('input', onInput)

    return () => slider.removeEventListener('input', onInput)
  }, [])

  useEffect(() => {
    const canvas = document.getElementById('binary-canvas')
    if (!canvas) {
      return undefined
    }

    const context = canvas.getContext('2d')
    if (!context) {
      return undefined
    }

    const config = {
      fontSize: 14,
      color: 'rgba(255,255,255,0.14)',
      highlightColor: 'rgba(255,255,255,0.35)',
      chars: '01',
    }

    let columns = []
    let animationFrame = null
    let active = true

    const randomChar = () => config.chars[Math.floor(Math.random() * config.chars.length)]

    const resetColumns = () => {
      const colCount = Math.ceil(canvas.width / config.fontSize)
      columns = Array.from({ length: colCount }).map((_, index) => ({
        x: index * config.fontSize,
        y: Math.random() * canvas.height,
        speed: Math.random() * 2 + 1,
        length: Math.floor(Math.random() * 14) + 6,
        chars: [],
        enabled: Math.random() < 0.3,
      }))
    }

    const resize = () => {
      canvas.width = window.innerWidth
      canvas.height = window.innerHeight
      resetColumns()
    }

    const draw = () => {
      if (!active) {
        return
      }

      context.fillStyle = 'rgba(0, 0, 0, 0.06)'
      context.fillRect(0, 0, canvas.width, canvas.height)
      context.font = `${config.fontSize}px "JetBrains Mono", monospace`
      context.textAlign = 'center'

      columns.forEach((column) => {
        if (!column.enabled) {
          if (Math.random() < 0.02) {
            column.enabled = true
            column.y = -column.length * config.fontSize
          }
          return
        }

        if (column.chars.length < column.length) {
          column.chars.push(randomChar())
        }

        column.chars.forEach((character, index) => {
          const y = column.y - (column.length - index) * config.fontSize
          if (y < -config.fontSize || y > canvas.height + config.fontSize) {
            return
          }

          if (index === column.chars.length - 1) {
            context.fillStyle = config.highlightColor
          } else {
            const opacity = (index / column.length) * 0.16
            context.fillStyle = `rgba(255,255,255,${opacity})`
          }

          context.fillText(character, column.x + config.fontSize / 2, y)
        })

        column.y += column.speed

        if (column.y - column.length * config.fontSize > canvas.height) {
          column.enabled = Math.random() < 0.5
          column.y = -column.length * config.fontSize
          column.chars = []
          column.speed = Math.random() * 2 + 1
        }
      })

      animationFrame = window.requestAnimationFrame(draw)
    }

    const onVisibility = () => {
      if (document.hidden) {
        active = false
        if (animationFrame) {
          window.cancelAnimationFrame(animationFrame)
        }
      } else if (!active) {
        active = true
        draw()
      }
    }

    resize()
    draw()
    window.addEventListener('resize', resize)
    document.addEventListener('visibilitychange', onVisibility)

    return () => {
      active = false
      if (animationFrame) {
        window.cancelAnimationFrame(animationFrame)
      }
      window.removeEventListener('resize', resize)
      document.removeEventListener('visibilitychange', onVisibility)
    }
  }, [])

  const isActivePath = (path) => location.pathname === path

  return (
    <>
      <canvas id="binary-canvas" />
      <div className="ordl-scanline" />

      <div className="ordl-container">
        <header className="ordl-header">
          <div className="ordl-header-left">
            <div className="ordl-brand">
              <div className="ordl-binary">01001111 01010010 01000100 01001100</div>
              <div className="ordl-title">
                <span className="ordl-title-jp">AETHER</span>
                <span className="ordl-title-en">v1.0.0</span>
              </div>
              <div className="ordl-tagline">黒い画面の中の白い影 / A WHITE SHADOW IN THE BLACK SCREEN</div>
            </div>

            <nav className="ordl-nav">
              {navItems.map((item) => (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`ordl-nav-link ${isActivePath(item.path) ? 'active' : ''}`}
                >
                  <span className="ordl-nav-label">
                    <span className="ordl-nav-jp">{item.en}</span>
                    <span className="ordl-nav-en">{item.jp}</span>
                  </span>
                </Link>
              ))}
            </nav>
          </div>

          <div className="ordl-header-right">
            <div className="ordl-contrast-control">
              <label htmlFor="contrast-slider">
                <span className="ordl-contrast-label-jp">Brightness</span>
                <span className="ordl-contrast-label-en">Adjust</span>
              </label>
              <input id="contrast-slider" type="range" min="0.5" max="5" step="0.1" defaultValue="1" />
            </div>

            <div className="ordl-status">
              <span className={`ordl-status-indicator ${statusTone}`} />
              <span className="ordl-mono">{statusText}</span>
              <span className="ordl-mono ordl-muted">| {uiRevision}</span>
            </div>
          </div>
        </header>

        <aside className="ordl-sidebar">
          <div className="ordl-sysinfo">
            <div className="ordl-sysinfo-row">
              <span className="ordl-sysinfo-label">SYS.ID</span>
              <span className="ordl-sysinfo-value">AETHER-01</span>
            </div>
            <div className="ordl-sysinfo-row">
              <span className="ordl-sysinfo-label">CORE.VER</span>
              <span className="ordl-sysinfo-value">v1.0.0</span>
            </div>
            <div className="ordl-sysinfo-row">
              <span className="ordl-sysinfo-label">UPTIME</span>
              <span className="ordl-sysinfo-value">{formatUptime(uptimeSeconds)}</span>
            </div>
            <div className="ordl-sysinfo-row">
              <span className="ordl-sysinfo-label">MODULES</span>
              <span className="ordl-sysinfo-value">{moduleCount}.ACTIVE</span>
            </div>
          </div>

          <h3 className="ordl-section-title">Navigation</h3>
          <ul className="ordl-menu">
            {navItems.map((item) => (
              <li key={item.path} className="ordl-menu-item">
                <Link
                  to={item.path}
                  className={`ordl-menu-link ${isActivePath(item.path) ? 'active' : ''}`}
                >
                  <span className="ordl-menu-icon">{item.mark}</span>
                  <span className="ordl-nav-jp">{item.en} / {item.jp}</span>
                </Link>
              </li>
            ))}
          </ul>

          <h3 className="ordl-section-title">Modules</h3>
          <ul className="ordl-list">
            {moduleEntries.length ? moduleEntries.map(([name, module]) => (
              <li key={name} className="ordl-list-item">
                <span>{module?.initialized ? '[■]' : '[ ]'}</span>
                <span>{name.replaceAll('_', ' ').toUpperCase()}</span>
                <span className="ordl-muted">{module?.stats?.operations || 0} ops</span>
              </li>
            )) : (
              <li className="ordl-list-item">
                <span>[ ]</span>
                <span className="ordl-muted">No module metadata</span>
              </li>
            )}
          </ul>

          <div className="ordl-hex-decoration">
            0x4F52444C
            <br />
            0x41455448
            <br />
            0x45520000
            <br />
            <br />
            0xFFFFFFFF
            <br />
            0x00000000
          </div>
        </aside>

        <main className="ordl-main">
          <div className="ordl-content">
            {children}
          </div>
        </main>
      </div>
    </>
  )
}

export default Layout
