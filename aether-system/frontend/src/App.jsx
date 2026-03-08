import React, { useEffect, useState } from 'react'
import { Routes, Route } from 'react-router-dom'
import axios from 'axios'

import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import ImageAnalysis from './pages/ImageAnalysis'
import TextAnalysis from './pages/TextAnalysis'
import AnomalyDetection from './pages/AnomalyDetection'
import KnowledgeBase from './pages/KnowledgeBase'
import SystemStatus from './pages/SystemStatus'

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || '/api/v1'
const backendBaseUrl = import.meta.env.VITE_BACKEND_BASE_URL || ''

const systemClient = axios.create({
  baseURL: backendBaseUrl || undefined,
})

axios.defaults.baseURL = apiBaseUrl

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
      const [healthResult, statusResult] = await Promise.allSettled([
        systemClient.get('/health'),
        systemClient.get('/status'),
      ])

      const checkedAt = new Date().toISOString()
      const healthPayload = healthResult.status === 'fulfilled' ? healthResult.value.data : null
      const statusPayload = statusResult.status === 'fulfilled' ? statusResult.value.data : null

      if (!healthPayload && !statusPayload) {
        throw new Error('Unable to reach health or status endpoints')
      }

      setSystemStatus((current) => ({
        status: healthPayload?.status || current?.status || 'degraded',
        system: healthPayload?.system || current?.system || 'AETHER',
        version: healthPayload?.version || current?.version || '1.0.0',
        coreInitialized: statusPayload?.core_initialized ?? current?.coreInitialized ?? false,
        core_initialized: statusPayload?.core_initialized ?? current?.core_initialized ?? false,
        modules: statusPayload?.modules || current?.modules || {},
        eventBus: statusPayload?.event_bus || current?.eventBus || {},
        scheduler: statusPayload?.scheduler || current?.scheduler || {},
        warmup: statusPayload?.warmup || current?.warmup || {},
        connectionError: healthResult.status === 'rejected' || statusResult.status === 'rejected',
        lastChecked: checkedAt,
      }))
    } catch (error) {
      console.error('System status check failed:', error)
      setSystemStatus((current) => {
        if (current) {
          return {
            ...current,
            status: current.status === 'healthy' ? 'degraded' : current.status,
            connectionError: true,
            lastChecked: new Date().toISOString(),
          }
        }

        return {
          status: 'offline',
          system: 'AETHER',
          version: '1.0.0',
          coreInitialized: false,
          modules: {},
          eventBus: {},
          scheduler: {},
          warmup: {},
          connectionError: true,
          lastChecked: new Date().toISOString(),
        }
      })
    } finally {
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
        <Route path="/system-status" element={<SystemStatus initialStatus={systemStatus} />} />
      </Routes>
    </Layout>
  )
}

export default App
