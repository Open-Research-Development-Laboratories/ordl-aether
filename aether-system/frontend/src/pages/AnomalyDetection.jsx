import React, { useState } from 'react'
import axios from 'axios'
import { AlertTriangle, Activity, Send, Loader, CheckCircle, AlertCircle } from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts'

function AnomalyDetection() {
  const [data, setData] = useState('')
  const [detecting, setDetecting] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const detectAnomalies = async () => {
    if (!data.trim()) return

    setDetecting(true)
    setError(null)

    try {
      const response = await axios.post('/analyze/anomalies', {
        data_type: 'time_series',
        content: data,
        context: { method: 'ensemble', sensitivity: 'medium' }
      })

      setResult(response.data)
    } catch (err) {
      console.error('Detection error:', err)
      setError(err.response?.data?.detail || 'Detection failed')
    } finally {
      setDetecting(false)
    }
  }

  // Prepare chart data
  const getChartData = () => {
    if (!result) return []
    
    const values = data.split(',').map(v => parseFloat(v.trim())).filter(v => !isNaN(v))
    const anomalyIndices = new Set(result.anomalies?.map(a => a.index) || [])
    
    return values.map((value, index) => ({
      index,
      value,
      isAnomaly: anomalyIndices.has(index)
    }))
  }

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'high': return 'text-red-400 bg-red-500/10 border-red-500/30'
      case 'medium': return 'text-yellow-400 bg-yellow-500/10 border-yellow-500/30'
      default: return 'text-green-400 bg-green-500/10 border-green-500/30'
    }
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold gradient-text">Anomaly Detection</h1>
        <p className="text-text-secondary mt-1">
          Multi-algorithm time-series outlier detection
        </p>
      </div>

      {/* Input */}
      <div className="glass rounded-xl p-6">
        <label className="block text-sm font-medium mb-2">
          Enter time-series data (comma-separated values)
        </label>
        <textarea
          value={data}
          onChange={(e) => setData(e.target.value)}
          placeholder="e.g., 10, 12, 11, 13, 45, 12, 11, 10, 100, 12, 11"
          className="w-full h-32 p-4 rounded-lg bg-bg-dark border border-border text-white placeholder-text-secondary focus:border-accent focus:outline-none resize-none font-mono"
        />
        <div className="flex items-center justify-between mt-4">
          <div className="text-sm text-text-secondary">
            <p>Example: Normal values with occasional spikes</p>
            <p className="mt-1">Try: 1,2,3,2,3,50,2,3,2,100,3,2</p>
          </div>
          <button
            onClick={detectAnomalies}
            disabled={detecting || !data.trim()}
            className="px-6 py-3 bg-gradient-to-r from-orange-500 to-red-500 rounded-lg font-semibold text-white flex items-center gap-2 hover:opacity-90 transition-opacity disabled:opacity-50"
          >
            {detecting ? (
              <>
                <Loader className="w-5 h-5 animate-spin" />
                Analyzing...
              </>
            ) : (
              <>
                <Activity className="w-5 h-5" />
                Detect Anomalies
              </>
            )}
          </button>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="p-4 rounded-lg bg-red-500/10 border border-red-500/30 flex items-center gap-3">
          <AlertCircle className="w-5 h-5 text-red-500" />
          <p className="text-red-400">{error}</p>
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="space-y-6 animate-slide-in">
          {/* Stats */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="glass rounded-xl p-4 text-center">
              <p className="text-text-secondary text-sm mb-1">Data Points</p>
              <p className="text-3xl font-bold text-white">{result.data_points}</p>
            </div>
            <div className="glass rounded-xl p-4 text-center">
              <p className="text-text-secondary text-sm mb-1">Anomalies Found</p>
              <p className={`text-3xl font-bold ${result.anomaly_count > 0 ? 'text-red-400' : 'text-green-400'}`}>
                {result.anomaly_count}
              </p>
            </div>
            <div className="glass rounded-xl p-4 text-center">
              <p className="text-text-secondary text-sm mb-1">Anomaly Rate</p>
              <p className="text-3xl font-bold text-white">
                {(result.statistics?.anomaly_rate * 100).toFixed(2)}%
              </p>
            </div>
            <div className={`glass rounded-xl p-4 text-center border ${getSeverityColor(result.severity)}`}>
              <p className="text-sm mb-1 opacity-80">Severity</p>
              <p className="text-3xl font-bold uppercase">{result.severity}</p>
            </div>
          </div>

          {/* Chart */}
          <div className="glass rounded-xl p-6">
            <h3 className="text-lg font-semibold mb-4">Time-Series Visualization</h3>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={getChartData()}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis dataKey="index" stroke="#64748b" />
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
                    dataKey="value" 
                    stroke="#f59e0b" 
                    strokeWidth={2}
                    dot={(props) => {
                      const { cx, cy, payload } = props
                      if (payload.isAnomaly) {
                        return <circle cx={cx} cy={cy} r={6} fill="#f44336" stroke="#fff" strokeWidth={2} />
                      }
                      return <circle cx={cx} cy={cy} r={3} fill="#f59e0b" />
                    }}
                  />
                  <ReferenceLine y={result.statistics?.mean} stroke="#f5f2e9" strokeDasharray="3 3" label="Mean" />
                </LineChart>
              </ResponsiveContainer>
            </div>
            <div className="flex items-center justify-center gap-6 mt-4 text-sm">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-accent"></div>
                <span className="text-text-secondary">Normal</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-red-500"></div>
                <span className="text-text-secondary">Anomaly</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-white"></div>
                <span className="text-text-secondary">Mean</span>
              </div>
            </div>
          </div>

          {/* Anomaly Details */}
          {result.anomalies && result.anomalies.length > 0 && (
            <div className="glass rounded-xl p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <AlertTriangle className="w-5 h-5 text-red-500" />
                Anomaly Details
              </h3>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-border">
                      <th className="text-left p-3 text-text-secondary font-medium">Index</th>
                      <th className="text-left p-3 text-text-secondary font-medium">Value</th>
                      <th className="text-left p-3 text-text-secondary font-medium">Methods</th>
                      <th className="text-left p-3 text-text-secondary font-medium">Confidence</th>
                    </tr>
                  </thead>
                  <tbody>
                    {result.anomalies.slice(0, 10).map((anomaly, idx) => (
                      <tr key={idx} className="border-b border-border/50 hover:bg-white/5">
                        <td className="p-3">{anomaly.index}</td>
                        <td className="p-3 font-mono text-red-400">{anomaly.value?.toFixed ? anomaly.value.toFixed(2) : anomaly.value}</td>
                        <td className="p-3">
                          <div className="flex flex-wrap gap-1">
                            {(anomaly.methods || []).map((method, i) => (
                              <span key={i} className="px-2 py-1 text-xs rounded bg-white/10 capitalize">
                                {method}
                              </span>
                            ))}
                          </div>
                        </td>
                        <td className="p-3">
                          <div className="flex items-center gap-2">
                            <div className="w-20 h-2 bg-white/10 rounded-full overflow-hidden">
                              <div
                                className="h-full bg-gradient-to-r from-orange-500 to-red-500"
                                style={{ width: `${(anomaly.confidence / 3) * 100}%` }}
                              />
                            </div>
                            <span className="text-sm">{anomaly.confidence}/3</span>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Statistics */}
          {result.statistics && (
            <div className="glass rounded-xl p-6">
              <h3 className="text-lg font-semibold mb-4">Statistical Summary</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="p-3 rounded-lg bg-white/5">
                  <p className="text-text-secondary text-sm">Mean</p>
                  <p className="text-xl font-mono">{result.statistics.mean?.toFixed(2)}</p>
                </div>
                <div className="p-3 rounded-lg bg-white/5">
                  <p className="text-text-secondary text-sm">Std Dev</p>
                  <p className="text-xl font-mono">{result.statistics.std?.toFixed(2)}</p>
                </div>
                <div className="p-3 rounded-lg bg-white/5">
                  <p className="text-text-secondary text-sm">Min</p>
                  <p className="text-xl font-mono">{result.statistics.min?.toFixed(2)}</p>
                </div>
                <div className="p-3 rounded-lg bg-white/5">
                  <p className="text-text-secondary text-sm">Max</p>
                  <p className="text-xl font-mono">{result.statistics.max?.toFixed(2)}</p>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default AnomalyDetection
