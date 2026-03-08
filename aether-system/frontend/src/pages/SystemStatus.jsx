import React, { useEffect, useMemo, useState } from 'react'
import axios from 'axios'
import {
  Activity,
  AlertCircle,
  AlertTriangle,
  CheckCircle2,
  Clock,
  Cpu,
  Loader,
  Server,
  WifiOff,
  Zap,
} from 'lucide-react'

const backendBaseUrl = import.meta.env.VITE_BACKEND_BASE_URL || ''

const systemClient = axios.create({
  baseURL: backendBaseUrl || undefined,
})

function ModuleCard({ name, module }) {
  const loadedComponents = module.loaded_components || []
  const hasErrors = (module.stats?.errors || 0) > 0 || Boolean(module.loading_error)

  return (
    <div className="p-4 rounded-lg bg-white/5 border border-border space-y-3">
      <div className="flex items-start justify-between gap-3">
        <div>
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${module.initialized ? 'bg-green-500' : 'bg-red-500'}`} />
            <span className="font-medium capitalize">{name.replaceAll('_', ' ')}</span>
          </div>
          <p className="text-xs text-text-secondary mt-1">
            {module.initialized ? 'Ready for inference' : 'Not initialized'}
          </p>
        </div>
        <div className="text-right text-xs text-text-secondary">
          <p>{module.stats?.operations || 0} ops</p>
          <p>{module.stats?.errors || 0} errors</p>
        </div>
      </div>

      <div className="flex flex-wrap gap-2">
        {loadedComponents.length > 0 ? (
          loadedComponents.map((component) => (
            <span key={component} className="px-2 py-1 rounded bg-accent/10 text-accent text-xs">
              {component.replaceAll('_', ' ')}
            </span>
          ))
        ) : (
          <span className="px-2 py-1 rounded bg-white/5 text-text-secondary text-xs">
            No model components loaded yet
          </span>
        )}
      </div>

      {module.loading_error && (
        <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/30 text-sm text-red-300">
          {module.loading_error}
        </div>
      )}

      {!module.loading_error && hasErrors && (
        <div className="p-3 rounded-lg bg-orange-500/10 border border-orange-500/30 text-sm text-orange-300">
          Recent runtime errors detected. Check logs if this keeps increasing.
        </div>
      )}
    </div>
  )
}

function SystemStatus({ initialStatus = null }) {
  const [status, setStatus] = useState(initialStatus)
  const [events, setEvents] = useState([])
  const [loading, setLoading] = useState(!initialStatus)
  const [error, setError] = useState(null)
  const [lastUpdated, setLastUpdated] = useState(initialStatus?.lastChecked || null)

  useEffect(() => {
    fetchStatus()
    const interval = setInterval(fetchStatus, 5000)
    return () => clearInterval(interval)
  }, [])

  const moduleEntries = useMemo(
    () => Object.entries(status?.modules || {}),
    [status]
  )

  const fetchStatus = async () => {
    const [statusResult, eventsResult] = await Promise.allSettled([
      systemClient.get('/status'),
      axios.get('/events/recent?limit=20'),
    ])

    if (statusResult.status === 'fulfilled') {
      const coreInitialized = Boolean(statusResult.value.data?.core_initialized)
      setStatus((current) => ({
        ...current,
        ...statusResult.value.data,
        coreInitialized,
        core_initialized: coreInitialized,
        connectionError: false,
      }))
      setLastUpdated(new Date().toISOString())
      setError(
        eventsResult.status === 'rejected'
          ? 'System state is live, but recent events could not be refreshed.'
          : null
      )
    } else if (status) {
      setStatus((current) => ({ ...(current || {}), connectionError: true }))
      setError('Unable to refresh live status. Showing the last known system state.')
    } else {
      setError('Unable to reach the backend status endpoint.')
    }

    if (eventsResult.status === 'fulfilled') {
      setEvents(eventsResult.value.data.events || [])
    }

    setLoading(false)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader className="w-8 h-8 animate-spin text-accent" />
      </div>
    )
  }

  const coreInitialized = Boolean(status?.core_initialized ?? status?.coreInitialized)
  const statusState = coreInitialized ? 'Initialized' : (status?.connectionError ? 'Offline' : 'Warming')
  const statusTone = coreInitialized
    ? 'text-green-400'
    : status?.connectionError
      ? 'text-red-400'
      : 'text-amber-400'
  const statusPanelTone = coreInitialized
    ? 'bg-green-500/20'
    : status?.connectionError
      ? 'bg-red-500/20'
      : 'bg-amber-500/20'
  const eventSubscriptions = status?.event_bus?.active_subscriptions || 0

  return (
    <div className="space-y-8">
      <div className="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <h1 className="text-3xl font-bold gradient-text">SYSTEM STATUS / システム状態</h1>
          <p className="text-text-secondary mt-1">
            HEALTH MONITOR / 健全性監視
          </p>
        </div>
        <div className="text-sm text-text-secondary flex items-center gap-2">
          <Clock className="w-4 h-4" />
          <span>{lastUpdated ? `Last updated ${new Date(lastUpdated).toLocaleTimeString()}` : 'Waiting for first refresh'}</span>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-lg bg-orange-500/10 border border-orange-500/30 flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-orange-300 mt-0.5" />
          <p className="text-orange-200">{error}</p>
        </div>
      )}

      {!status && (
        <div className="glass rounded-xl p-8 text-center">
          <WifiOff className="w-14 h-14 mx-auto mb-4 text-red-400" />
          <h2 className="text-xl font-semibold mb-2">Status endpoint unavailable</h2>
          <p className="text-text-secondary">
            The dashboard could not load system details from the backend.
          </p>
        </div>
      )}

      {status && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="glass rounded-xl p-6">
              <div className="flex items-center gap-4">
                <div className={`w-16 h-16 rounded-full flex items-center justify-center ${statusPanelTone}`}>
                  <Server className={`w-8 h-8 ${statusTone}`} />
                </div>
                <div>
                  <p className="text-text-secondary text-sm">Core Status</p>
                  <p className={`text-xl font-semibold ${statusTone}`}>{statusState}</p>
                </div>
              </div>
            </div>

            <div className="glass rounded-xl p-6">
              <div className="flex items-center gap-4">
                <div className="w-16 h-16 rounded-full bg-accent/20 flex items-center justify-center">
                  <Cpu className="w-8 h-8 text-accent" />
                </div>
                <div>
                  <p className="text-text-secondary text-sm">Active Modules</p>
                  <p className="text-xl font-semibold text-white">{moduleEntries.length}</p>
                </div>
              </div>
            </div>

            <div className="glass rounded-xl p-6">
              <div className="flex items-center gap-4">
                <div className="w-16 h-16 rounded-full bg-amber-500/20 flex items-center justify-center">
                  <Activity className="w-8 h-8 text-amber-400" />
                </div>
                <div>
                  <p className="text-text-secondary text-sm">Event Bus</p>
                  <p className="text-xl font-semibold text-white">{eventSubscriptions} subscriptions</p>
                </div>
              </div>
            </div>
          </div>

          <div className="glass rounded-xl p-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Zap className="w-5 h-5 text-accent" />
              Module Status
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {moduleEntries.map(([name, module]) => (
                <ModuleCard key={name} name={name} module={module} />
              ))}
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="glass rounded-xl p-6">
              <h3 className="text-lg font-semibold mb-4">Event Bus Statistics</h3>
              <div className="space-y-3">
                <div className="flex justify-between p-3 rounded-lg bg-white/5">
                  <span className="text-text-secondary">Events Published</span>
                  <span className="font-mono">{status?.event_bus?.events_published || 0}</span>
                </div>
                <div className="flex justify-between p-3 rounded-lg bg-white/5">
                  <span className="text-text-secondary">Events Processed</span>
                  <span className="font-mono">{status?.event_bus?.events_processed || 0}</span>
                </div>
                <div className="flex justify-between p-3 rounded-lg bg-white/5">
                  <span className="text-text-secondary">Active Subscriptions</span>
                  <span className="font-mono">{eventSubscriptions}</span>
                </div>
                <div className="flex justify-between p-3 rounded-lg bg-white/5">
                  <span className="text-text-secondary">Event Types</span>
                  <span className="font-mono">{status?.event_bus?.event_types?.length || 0}</span>
                </div>
              </div>
            </div>

            <div className="glass rounded-xl p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <Clock className="w-5 h-5 text-accent" />
                Recent Events
              </h3>
              <div className="space-y-2 max-h-80 overflow-auto">
                {events.length === 0 ? (
                  <p className="text-text-secondary text-center py-4">No recent events</p>
                ) : (
                  events.map((event) => (
                    <div key={event.id} className="p-3 rounded-lg bg-white/5 text-sm">
                      <div className="flex items-center justify-between mb-1 gap-3">
                        <span className="font-medium text-accent">{event.type}</span>
                        <span className="text-xs text-text-secondary">
                          {new Date(event.timestamp).toLocaleTimeString()}
                        </span>
                      </div>
                      <div className="flex items-center gap-2 text-xs text-text-secondary">
                        <span>{event.source}</span>
                        <span className="w-1 h-1 rounded-full bg-border"></span>
                        <span>P{event.priority}</span>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>

          {status?.scheduler && (
            <div className="glass rounded-xl p-6">
              <h3 className="text-lg font-semibold mb-4">Scheduler Status</h3>
              <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:gap-8">
                <div className="flex items-center gap-2">
                  {status.scheduler.running ? (
                    <CheckCircle2 className="w-5 h-5 text-green-400" />
                  ) : (
                    <AlertCircle className="w-5 h-5 text-red-400" />
                  )}
                  <span>{status.scheduler.running ? 'Running' : 'Stopped'}</span>
                </div>
                <div className="text-text-secondary">
                  Jobs Executed: <span className="text-white font-mono">{status.scheduler.jobs_executed}</span>
                </div>
                <div className="text-text-secondary">
                  Scheduled Jobs: <span className="text-white font-mono">{status.scheduler.scheduled_jobs}</span>
                </div>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}

export default SystemStatus
