import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { Activity, Cpu, Database, Server, Clock, Zap, CheckCircle, AlertCircle, Loader } from 'lucide-react'

const backendBaseUrl = import.meta.env.VITE_BACKEND_BASE_URL || ''

function SystemStatus() {
  const [status, setStatus] = useState(null)
  const [events, setEvents] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchStatus()
    const interval = setInterval(fetchStatus, 5000)
    return () => clearInterval(interval)
  }, [])

  const fetchStatus = async () => {
    try {
      const [statusRes, eventsRes] = await Promise.all([
        axios.get(`${backendBaseUrl}/status`),
        axios.get('/events/recent?limit=20')
      ])

      setStatus(statusRes.data)
      setEvents(eventsRes.data.events || [])
      setLoading(false)
    } catch (err) {
      console.error('Status fetch error:', err)
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader className="w-8 h-8 animate-spin text-accent" />
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold gradient-text">System Status</h1>
        <p className="text-text-secondary mt-1">
          Monitor AETHER system health and performance
        </p>
      </div>

      {/* Overall Status */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="glass rounded-xl p-6">
          <div className="flex items-center gap-4">
            <div className={`w-16 h-16 rounded-full flex items-center justify-center ${
              status?.core_initialized 
                ? 'bg-green-500/20' 
                : 'bg-red-500/20'
            }`}>
              <Server className={`w-8 h-8 ${
                status?.core_initialized ? 'text-green-500' : 'text-red-500'
              }`} />
            </div>
            <div>
              <p className="text-text-secondary text-sm">Core Status</p>
              <p className={`text-xl font-semibold ${
                status?.core_initialized ? 'text-green-400' : 'text-red-400'
              }`}>
                {status?.core_initialized ? 'Initialized' : 'Offline'}
              </p>
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
              <p className="text-xl font-semibold text-white">
                {Object.keys(status?.modules || {}).length}
              </p>
            </div>
          </div>
        </div>

        <div className="glass rounded-xl p-6">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 rounded-full bg-purple-500/20 flex items-center justify-center">
              <Activity className="w-8 h-8 text-purple-500" />
            </div>
            <div>
              <p className="text-text-secondary text-sm">Event Bus</p>
              <p className="text-xl font-semibold text-white">
                {status?.event_bus?.active_subscriptions || 0} subscriptions
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Module Status */}
      <div className="glass rounded-xl p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Zap className="w-5 h-5 text-accent" />
          Module Status
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {Object.entries(status?.modules || {}).map(([name, module]) => (
            <div key={name} className="p-4 rounded-lg bg-white/5 border border-border">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <div className={`w-2 h-2 rounded-full ${
                    module.initialized ? 'bg-green-500' : 'bg-red-500'
                  }`} />
                  <span className="font-medium capitalize">{name.replace('_', ' ')}</span>
                </div>
                <span className="text-xs text-text-secondary">
                  {module.stats?.operations || 0} ops
                </span>
              </div>
              {module.stats?.errors > 0 && (
                <p className="text-xs text-red-400">
                  {module.stats.errors} errors
                </p>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Event Statistics */}
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
              <span className="font-mono">{status?.event_bus?.active_subscriptions || 0}</span>
            </div>
            <div className="flex justify-between p-3 rounded-lg bg-white/5">
              <span className="text-text-secondary">Event Types</span>
              <span className="font-mono">{status?.event_bus?.event_types?.length || 0}</span>
            </div>
          </div>
        </div>

        {/* Recent Events */}
        <div className="glass rounded-xl p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Clock className="w-5 h-5 text-accent" />
            Recent Events
          </h3>
          <div className="space-y-2 max-h-80 overflow-auto">
            {events.length === 0 ? (
              <p className="text-text-secondary text-center py-4">No recent events</p>
            ) : (
              events.map((event, idx) => (
                <div key={idx} className="p-3 rounded-lg bg-white/5 text-sm">
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-medium text-accent">{event.type}</span>
                    <span className="text-xs text-text-secondary">
                      {new Date(event.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                  <p className="text-text-secondary text-xs">{event.source}</p>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Scheduler Status */}
      {status?.scheduler && (
        <div className="glass rounded-xl p-6">
          <h3 className="text-lg font-semibold mb-4">Scheduler Status</h3>
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-2">
              <div className={`w-3 h-3 rounded-full ${
                status.scheduler.running ? 'bg-green-500 animate-pulse' : 'bg-red-500'
              }`} />
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
    </div>
  )
}

export default SystemStatus
