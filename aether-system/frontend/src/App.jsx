import React, { useState, useEffect } from 'react'
import { Routes, Route } from 'react-router-dom'
import axios from 'axios'

import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import ImageAnalysis from './pages/ImageAnalysis'
import TextAnalysis from './pages/TextAnalysis'
import AnomalyDetection from './pages/AnomalyDetection'
import KnowledgeBase from './pages/KnowledgeBase'
import SystemStatus from './pages/SystemStatus'

// Configure axios
axios.defaults.baseURL = 'http://localhost:8000/api/v1'

function App() {
  const [systemStatus, setSystemStatus] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    checkSystemStatus()
    const interval = setInterval(checkSystemStatus, 5000)
    return () => clearInterval(interval)
  }, [])

  const checkSystemStatus = async () => {
    try {
      const [healthResponse, statusResponse] = await Promise.all([
        axios.get('http://localhost:8000/health'),
        axios.get('http://localhost:8000/status'),
      ])

      setSystemStatus({
        status: healthResponse.data.status,
        system: healthResponse.data.system,
        version: healthResponse.data.version,
        coreInitialized: statusResponse.data.core_initialized,
        modules: statusResponse.data.modules || {},
        eventBus: statusResponse.data.event_bus || {},
        scheduler: statusResponse.data.scheduler || {},
      })
      setLoading(false)
    } catch (error) {
      console.error('System status check failed:', error)
      setSystemStatus({
        status: 'offline',
        coreInitialized: false,
        modules: {},
        eventBus: {},
        scheduler: {},
      })
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-bg-dark flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-accent border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-text-secondary">Initializing AETHER...</p>
        </div>
      </div>
    )
  }

  return (
    <Layout systemStatus={systemStatus}>
      <Routes>
        <Route path="/" element={<Dashboard systemStatus={systemStatus} />} />
        <Route path="/image" element={<ImageAnalysis />} />
        <Route path="/text" element={<TextAnalysis />} />
        <Route path="/anomalies" element={<AnomalyDetection />} />
        <Route path="/knowledge" element={<KnowledgeBase />} />
        <Route path="/status" element={<SystemStatus />} />
      </Routes>
    </Layout>
  )
}

export default App
