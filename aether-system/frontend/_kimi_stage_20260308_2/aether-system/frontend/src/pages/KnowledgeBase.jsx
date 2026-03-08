import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { Database, Search, Loader, FileText, Image, AlertTriangle, Clock } from 'lucide-react'

function KnowledgeBase() {
  const [query, setQuery] = useState('')
  const [searching, setSearching] = useState(false)
  const [results, setResults] = useState([])
  const [stats, setStats] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchStats()
  }, [])

  const fetchStats = async () => {
    try {
      const response = await axios.get('/knowledge/stats')
      setStats(response.data)
    } catch (err) {
      console.error('Stats fetch error:', err)
    }
  }

  const searchKnowledge = async () => {
    if (!query.trim()) return

    setSearching(true)
    setError(null)

    try {
      const response = await axios.post('/knowledge/search', {
        query,
        limit: 20
      })

      setResults(response.data.results || [])
    } catch (err) {
      console.error('Search error:', err)
      setError(err.response?.data?.detail || 'Search failed')
    } finally {
      setSearching(false)
    }
  }

  const getTypeIcon = (type) => {
    switch (type) {
      case 'image_analysis': return Image
      case 'text_analysis': return FileText
      case 'anomaly_detection': return AlertTriangle
      default: return Database
    }
  }

  const getTypeColor = (type) => {
    switch (type) {
      case 'image_analysis': return 'text-purple-400 bg-purple-500/10'
      case 'text_analysis': return 'text-accent bg-accent/10'
      case 'anomaly_detection': return 'text-orange-400 bg-orange-500/10'
      default: return 'text-text-secondary bg-white/5'
    }
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold gradient-text">Knowledge Base</h1>
        <p className="text-text-secondary mt-1">
          Search and explore stored analyses and insights
        </p>
      </div>

      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="glass rounded-xl p-4 text-center">
            <p className="text-text-secondary text-sm mb-1">Total Items</p>
            <p className="text-3xl font-bold text-white">{stats.total_items}</p>
          </div>
          {Object.entries(stats.by_type || {}).map(([type, count]) => (
            <div key={type} className="glass rounded-xl p-4 text-center">
              <p className="text-text-secondary text-sm mb-1 capitalize">{type}</p>
              <p className="text-3xl font-bold text-accent">{count}</p>
            </div>
          ))}
        </div>
      )}

      {/* Search */}
      <div className="glass rounded-xl p-6">
        <div className="flex gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-text-secondary" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && searchKnowledge()}
              placeholder="Search knowledge base..."
              className="w-full pl-12 pr-4 py-3 rounded-lg bg-bg-dark border border-border text-white placeholder-text-secondary focus:border-accent focus:outline-none"
            />
          </div>
          <button
            onClick={searchKnowledge}
            disabled={searching || !query.trim()}
            className="px-6 py-3 bg-gradient-to-r from-accent to-blue-500 rounded-lg font-semibold text-white flex items-center gap-2 hover:opacity-90 transition-opacity disabled:opacity-50"
          >
            {searching ? (
              <>
                <Loader className="w-5 h-5 animate-spin" />
                Searching...
              </>
            ) : (
              <>
                <Search className="w-5 h-5" />
                Search
              </>
            )}
          </button>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="p-4 rounded-lg bg-red-500/10 border border-red-500/30 flex items-center gap-3">
          <AlertTriangle className="w-5 h-5 text-red-500" />
          <p className="text-red-400">{error}</p>
        </div>
      )}

      {/* Results */}
      {results.length > 0 && (
        <div className="space-y-4">
          <p className="text-text-secondary">
            Found {results.length} results
          </p>
          
          {results.map((item, idx) => {
            const Icon = getTypeIcon(item.type)
            return (
              <div key={idx} className="glass rounded-xl p-6 card-hover">
                <div className="flex items-start gap-4">
                  <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${getTypeColor(item.type)}`}>
                    <Icon className="w-6 h-6" />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="font-semibold text-lg">{item.title}</h3>
                      <span className={`px-2 py-1 text-xs rounded capitalize ${getTypeColor(item.type)}`}>
                        {item.type}
                      </span>
                    </div>
                    <p className="text-text-secondary text-sm mb-3 line-clamp-2">
                      {item.content}
                    </p>
                    <div className="flex items-center gap-4 text-xs text-text-secondary">
                      <span className="flex items-center gap-1">
                        <Database className="w-3 h-3" />
                        {item.source}
                      </span>
                      <span className="flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        {new Date(item.created_at).toLocaleString()}
                      </span>
                      {item.confidence && (
                        <span className="text-accent">
                          Confidence: {(item.confidence * 100).toFixed(0)}%
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      )}

      {/* Empty State */}
      {results.length === 0 && !searching && query && (
        <div className="text-center py-12">
          <Database className="w-16 h-16 mx-auto mb-4 text-text-secondary" />
          <p className="text-text-secondary">No results found</p>
          <p className="text-sm text-text-secondary mt-1">
            Try a different search term
          </p>
        </div>
      )}
    </div>
  )
}

export default KnowledgeBase