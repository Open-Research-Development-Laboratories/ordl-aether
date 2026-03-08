import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { 
  Activity, 
  Image, 
  FileText, 
  AlertTriangle, 
  Database,
  TrendingUp,
  Zap,
  Clock
} from 'lucide-react'
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  BarChart,
  Bar
} from 'recharts'

function StatCard({ icon: Icon, title, value, subtitle, trend, color = 'accent' }) {
  const colors = {
    accent: 'from-cyan-500 to-blue-500',
    purple: 'from-purple-500 to-pink-500',
    green: 'from-green-500 to-emerald-500',
    orange: 'from-orange-500 to-red-500'
  }

  return (
    <div className="glass rounded-xl p-6 card-hover">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-text-secondary text-sm mb-1">{title}</p>
          <h3 className="text-3xl font-bold text-white">{value}</h3>
          {subtitle && <p className="text-text-secondary text-sm mt-1">{subtitle}</p>}
        </div>
        <div className={`w-12 h-12 rounded-lg bg-gradient-to-br ${colors[color]} flex items-center justify-center`}>
          <Icon className="w-6 h-6 text-white" />
        </div>
      </div>
      {trend && (
        <div className="mt-4 flex items-center gap-2">
          <TrendingUp className="w-4 h-4 text-green-400" />
          <span className="text-green-400 text-sm">{trend}</span>
        </div>
      )}
    </div>
  )
}

function RecentEvents({ events }) {
  return (
    <div className="glass rounded-xl p-6">
      <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
        <Clock className="w-5 h-5 text-accent" />
        Recent Events
      </h3>
      <div className="space-y-3 max-h-80 overflow-auto">
        {events.length === 0 ? (
          <p className="text-text-secondary text-center py-4">No recent events</p>
        ) : (
          events.map((event, idx) => (
            <div key={idx} className="flex items-start gap-3 p-3 rounded-lg bg-white/5">
              <div className={`w-2 h-2 rounded-full mt-2 ${
                event.priority <= 3 ? 'bg-red-500' : 
                event.priority <= 5 ? 'bg-yellow-500' : 'bg-green-500'
              }`} />
              <div className="flex-1">
                <p className="text-sm font-medium">{event.type}</p>
                <p className="text-xs text-text-secondary">{event.source}</p>
                <p className="text-xs text-text-secondary mt-1">
                  {new Date(event.timestamp).toLocaleTimeString()}
                </p>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

function Dashboard({ systemStatus }) {
  const [stats, setStats] = useState({
    totalAnalyses: 0,
    imagesProcessed: 0,
    textsAnalyzed: 0,
    anomaliesDetected: 0,
    knowledgeItems: 0
  })
  const [events, setEvents] = useState([])
  const [activityData, setActivityData] = useState([])
  const moduleEntries = Object.entries(systemStatus?.modules || {})

  useEffect(() => {
    fetchDashboardData()
    const interval = setInterval(fetchDashboardData, 10000)
    return () => clearInterval(interval)
  }, [])

  const fetchDashboardData = async () => {
    try {
      // Get knowledge stats
      const kbResponse = await axios.get('/knowledge/stats')
      const kbStats = kbResponse.data

      // Get recent events
      const eventsResponse = await axios.get('/events/recent?limit=10')
      
      setStats(prev => ({
        ...prev,
        knowledgeItems: kbStats.total_items || 0
      }))
      
      setEvents(eventsResponse.data.events || [])

      // Generate activity data (mock for now)
      const mockData = Array.from({ length: 24 }, (_, i) => ({
        time: `${i}:00`,
        analyses: Math.floor(Math.random() * 20) + 5,
        events: Math.floor(Math.random() * 10)
      }))
      setActivityData(mockData)

    } catch (error) {
      console.error('Dashboard data fetch error:', error)
    }
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold gradient-text">Dashboard</h1>
          <p className="text-text-secondary mt-1">
            NASA-Inspired Unified AI System Overview
          </p>
        </div>
        <div className="flex items-center gap-2 px-4 py-2 rounded-lg bg-green-500/10 border border-green-500/30">
          <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
          <span className="text-green-400 text-sm font-medium">System Online</span>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          icon={Image}
          title="Images Processed"
          value={stats.imagesProcessed}
          subtitle="Computer vision analyses"
          color="purple"
        />
        <StatCard
          icon={FileText}
          title="Texts Analyzed"
          value={stats.textsAnalyzed}
          subtitle="NLP operations"
          color="accent"
        />
        <StatCard
          icon={AlertTriangle}
          title="Anomalies Detected"
          value={stats.anomaliesDetected}
          subtitle="Pattern deviations found"
          color="orange"
        />
        <StatCard
          icon={Database}
          title="Knowledge Items"
          value={stats.knowledgeItems}
          subtitle="Stored in database"
          color="green"
        />
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Activity Chart */}
        <div className="lg:col-span-2 glass rounded-xl p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Activity className="w-5 h-5 text-accent" />
            System Activity (24h)
          </h3>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={activityData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="time" stroke="#64748b" />
                <YAxis stroke="#64748b" />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#111936', 
                    border: '1px solid #1e293b',
                    borderRadius: '8px'
                  }}
                />
                <Line 
                  type="monotone" 
                  dataKey="analyses" 
                  stroke="#00bcd4" 
                  strokeWidth={2}
                  dot={false}
                />
                <Line 
                  type="monotone" 
                  dataKey="events" 
                  stroke="#7c3aed" 
                  strokeWidth={2}
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Recent Events */}
        <RecentEvents events={events} />
      </div>

      {/* Module Status */}
      <div className="glass rounded-xl p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Zap className="w-5 h-5 text-accent" />
          Active Modules
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {moduleEntries.map(([moduleName, module]) => (
            <div key={moduleName} className="p-4 rounded-lg bg-white/5 border border-border">
              <div className="flex items-center gap-2 mb-2">
                <div className={`w-2 h-2 rounded-full ${module?.initialized ? 'bg-green-500' : 'bg-red-500'}`}></div>
                <span className="font-medium capitalize">{moduleName.replaceAll('_', ' ')}</span>
              </div>
              <p className="text-xs text-text-secondary">
                Operations: {module.stats?.operations || 0}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default Dashboard
