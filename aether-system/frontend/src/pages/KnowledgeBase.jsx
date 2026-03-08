import React, { useEffect, useState } from 'react'
import axios from 'axios'
import {
  AlertTriangle,
  Clock,
  Database,
  Eye,
  FileText,
  Image as ImageIcon,
  Loader,
  Search,
  Sparkles,
  Tag,
} from 'lucide-react'

function DetailSection({ title, children, action = null }) {
  return (
    <div className="glass rounded-xl p-5">
      <div className="flex items-center justify-between gap-3 mb-4">
        <h3 className="text-lg font-semibold">{title}</h3>
        {action}
      </div>
      {children}
    </div>
  )
}

function normalizeAssetUrl(value) {
  if (!value || typeof value !== 'string') {
    return null
  }
  if (value.startsWith('http://') || value.startsWith('https://')) {
    return value
  }
  if (value.startsWith('//')) {
    return `https:${value}`
  }
  if (value.startsWith('/')) {
    return value
  }
  return `/${value}`
}

function resolveAssetUrl(metadata = {}) {
  const candidates = [
    metadata.asset_url,
    metadata.image_url,
    metadata.thumbnail_url,
    metadata.preview_image,
    metadata.og_image,
  ]
  const matched = candidates.find((entry) => typeof entry === 'string' && entry.trim())
  return normalizeAssetUrl(matched)
}

function getItemSummary(item) {
  if (!item) {
    return ''
  }
  const metadata = item.metadata || {}
  return (
    metadata.analysis?.summary
    || metadata.summary?.text
    || item.preview
    || item.content
    || item.full_content
    || ''
  )
}

function KnowledgeBase() {
  const [query, setQuery] = useState('')
  const [searching, setSearching] = useState(false)
  const [results, setResults] = useState([])
  const [stats, setStats] = useState(null)
  const [error, setError] = useState(null)
  const [selectedItem, setSelectedItem] = useState(null)
  const [hasSearched, setHasSearched] = useState(false)
  const [enrichingItemId, setEnrichingItemId] = useState(null)
  const [enrichError, setEnrichError] = useState(null)
  const [enrichmentAttempts, setEnrichmentAttempts] = useState({})

  useEffect(() => {
    fetchStats()
  }, [])

  useEffect(() => {
    if (!selectedItem?.id) {
      return
    }

    if (selectedItem.type !== 'web_research') {
      return
    }

    const metadata = selectedItem.metadata || {}
    if (metadata.analysis || enrichmentAttempts[selectedItem.id]) {
      return
    }

    setEnrichmentAttempts((current) => ({ ...current, [selectedItem.id]: true }))
    enrichKnowledgeItem(selectedItem.id)
  }, [selectedItem?.id, selectedItem?.type])

  const fetchStats = async () => {
    try {
      const response = await axios.get('/knowledge/stats')
      setStats(response.data)
    } catch (err) {
      console.error('Stats fetch error:', err)
    }
  }

  const updateItemInState = (nextItem) => {
    if (!nextItem) {
      return
    }
    setResults((current) => current.map((entry) => (entry.id === nextItem.id ? nextItem : entry)))
    setSelectedItem((current) => {
      if (!current || current.id !== nextItem.id) {
        return current
      }
      return nextItem
    })
  }

  const searchKnowledge = async (value = query) => {
    setSearching(true)
    setError(null)
    setEnrichError(null)
    setHasSearched(true)

    try {
      const normalizedQuery = value.trim()
      const response = await axios.post('/knowledge/search', {
        query: normalizedQuery || null,
        limit: 20,
      })

      const nextResults = response.data.results || []
      setResults(nextResults)
      setSelectedItem((current) => {
        if (!nextResults.length) {
          return null
        }
        if (current) {
          const match = nextResults.find((item) => item.id === current.id)
          if (match) {
            return match
          }
        }
        return nextResults[0]
      })
    } catch (err) {
      console.error('Search error:', err)
      setError(err.response?.data?.detail || 'Search failed')
    } finally {
      setSearching(false)
    }
  }

  const enrichKnowledgeItem = async (itemId, force = false) => {
    setEnrichingItemId(itemId)
    setEnrichError(null)

    try {
      const response = await axios.post(`/knowledge/enrich/${itemId}`, {
        force,
        max_chars: 3500,
      })

      if (response.data?.item) {
        updateItemInState(response.data.item)
      }
    } catch (err) {
      console.error('Knowledge enrichment error:', err)
      setEnrichError(err.response?.data?.detail || 'Unable to enrich this record right now')
    } finally {
      setEnrichingItemId(null)
    }
  }

  const getTypeIcon = (type) => {
    switch (type) {
      case 'image_analysis':
        return ImageIcon
      case 'text_analysis':
        return FileText
      case 'anomaly_detection':
        return AlertTriangle
      default:
        return Database
    }
  }

  const getTypeColor = (type) => {
    switch (type) {
      case 'image_analysis':
        return 'text-slate-300 bg-slate-500/10 border border-slate-500/20'
      case 'text_analysis':
        return 'text-accent bg-accent/10 border border-accent/20'
      case 'anomaly_detection':
        return 'text-orange-300 bg-orange-500/10 border border-orange-500/20'
      default:
        return 'text-text-secondary bg-white/5 border border-border'
    }
  }

  const selectedMetadata = selectedItem?.metadata || {}
  const selectedAssetUrl = resolveAssetUrl(selectedMetadata)
  const selectedAnalysis = selectedMetadata.analysis || null
  const selectedSummary = getItemSummary(selectedItem)
  const entityGroups = selectedMetadata.entities || selectedAnalysis?.entities || []
  const classifications = selectedMetadata.classifications || []
  const detections = selectedMetadata.detections || []
  const anomalyIndices = selectedMetadata.anomaly_indices || []
  const anomalyStats = selectedMetadata.statistics || {}
  const keywordList = selectedMetadata.keywords || selectedAnalysis?.keywords || []
  const classificationScores = selectedMetadata.classification || selectedAnalysis?.classification || {}

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold gradient-text">KNOWLEDGE BASE / 知識ベース</h1>
        <p className="text-text-secondary mt-1">
          SEARCH AND REPORT INSPECTION / 検索と詳細確認
        </p>
      </div>

      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="glass rounded-xl p-4 text-center">
            <p className="text-text-secondary text-sm mb-1">Total Items</p>
            <p className="text-3xl font-bold text-white">{stats.total_items}</p>
          </div>
          {Object.entries(stats.by_type || {}).map(([type, count]) => (
            <div key={type} className="glass rounded-xl p-4 text-center">
              <p className="text-text-secondary text-sm mb-1 capitalize">{type.replaceAll('_', ' ')}</p>
              <p className="text-3xl font-bold text-accent">{count}</p>
            </div>
          ))}
        </div>
      )}

      <div className="glass rounded-xl p-6">
        <div className="flex flex-col gap-4 lg:flex-row">
          <div className="flex-1 relative">
            <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-text-secondary" />
            <input
              type="text"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === 'Enter') {
                  searchKnowledge()
                }
              }}
              placeholder="Enter query, then run Search"
              className="w-full pl-12 pr-4 py-3 rounded-lg bg-bg-dark border border-border text-white placeholder-text-secondary focus:border-accent focus:outline-none"
            />
          </div>
          <button
            onClick={() => searchKnowledge()}
            disabled={searching}
            className="px-6 py-3 bg-gradient-to-r from-amber-500 to-amber-700 rounded-lg font-semibold text-black flex items-center justify-center gap-2 hover:opacity-90 transition-opacity disabled:opacity-50"
          >
            {searching ? (
              <>
                <Loader className="w-5 h-5 animate-spin" />
                Searching
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

      {error && (
        <div className="p-4 rounded-lg bg-red-500/10 border border-red-500/30 flex items-center gap-3">
          <AlertTriangle className="w-5 h-5 text-red-500" />
          <p className="text-red-300">{error}</p>
        </div>
      )}

      <div className="grid grid-cols-1 xl:grid-cols-[minmax(0,1.1fr)_minmax(0,1fr)] gap-6 items-start xl:h-[calc(100vh-320px)]">
        <div className="space-y-4 xl:min-h-0 xl:overflow-y-auto xl:pr-2">
          {!hasSearched ? (
            <p className="text-text-secondary">No query executed yet. Enter a term and run search.</p>
          ) : (
            <p className="text-text-secondary">
              {query.trim() ? `Found ${results.length} results` : `Showing ${results.length} recent records`}
            </p>
          )}

          {results.map((item) => {
            const Icon = getTypeIcon(item.type)
            const active = selectedItem?.id === item.id
            const metadata = item.metadata || {}
            const assetUrl = resolveAssetUrl(metadata)
            const sentiment = metadata.sentiment || metadata.analysis?.sentiment
            const anomalyCount = metadata.anomaly_count
            const severity = metadata.severity
            const previewText = getItemSummary(item)

            return (
              <button
                key={item.id}
                type="button"
                onClick={() => setSelectedItem(item)}
                className={`w-full text-left glass rounded-xl p-5 transition-all ${
                  active ? 'border border-accent/40 shadow-[0_0_0_1px_rgba(0,188,212,0.2)]' : 'hover:border-border/80'
                }`}
              >
                <div className="flex items-start gap-4">
                  {assetUrl ? (
                    <img
                      src={assetUrl}
                      alt={item.title}
                      className="w-24 h-24 rounded-lg object-cover border border-border"
                    />
                  ) : (
                    <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${getTypeColor(item.type)}`}>
                      <Icon className="w-6 h-6" />
                    </div>
                  )}

                  <div className="flex-1 min-w-0">
                    <div className="flex flex-wrap items-center gap-3 mb-2">
                      <h3 className="font-semibold text-lg">{item.title}</h3>
                      <span className={`px-2 py-1 text-xs rounded capitalize ${getTypeColor(item.type)}`}>
                        {item.type.replaceAll('_', ' ')}
                      </span>
                    </div>

                    <p className="text-text-secondary text-sm mb-4 whitespace-pre-wrap line-clamp-3">
                      {previewText}
                    </p>

                    <div className="flex flex-wrap items-center gap-4 text-xs text-text-secondary">
                      <span className="flex items-center gap-1">
                        <Database className="w-3 h-3" />
                        {item.source}
                      </span>
                      <span className="flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        {new Date(item.created_at).toLocaleString()}
                      </span>
                      {item.confidence ? (
                        <span className="text-accent">Confidence {(item.confidence * 100).toFixed(1)}%</span>
                      ) : null}
                      {sentiment?.label ? (
                        <span className="text-green-300">Sentiment {sentiment.label}</span>
                      ) : null}
                      {typeof anomalyCount === 'number' ? (
                        <span className="text-orange-300">
                          {anomalyCount} anomalies{severity ? `, ${severity}` : ''}
                        </span>
                      ) : null}
                    </div>
                  </div>

                  <Eye className="w-5 h-5 text-text-secondary shrink-0" />
                </div>
              </button>
            )
          })}

          {hasSearched && !results.length && !searching && (
            <div className="glass rounded-xl p-12 text-center">
              <Database className="w-16 h-16 mx-auto mb-4 text-text-secondary" />
              <p className="text-text-secondary">No records matched the current query.</p>
            </div>
          )}
        </div>

        <div className="space-y-4 xl:min-h-0 xl:overflow-y-auto xl:pr-2">
          {selectedItem ? (
            <>
              <DetailSection
                title={selectedItem.title}
                action={
                  <div className="flex items-center gap-2">
                    <span className={`px-2 py-1 text-xs rounded capitalize ${getTypeColor(selectedItem.type)}`}>
                      {selectedItem.type.replaceAll('_', ' ')}
                    </span>
                    {selectedItem.type === 'web_research' ? (
                      <button
                        type="button"
                        onClick={() => enrichKnowledgeItem(selectedItem.id, true)}
                        className="px-3 py-1 rounded border border-border text-xs text-text-secondary hover:text-white"
                        disabled={enrichingItemId === selectedItem.id}
                      >
                        {enrichingItemId === selectedItem.id ? 'Analyzing...' : 'Re-run Analysis'}
                      </button>
                    ) : null}
                  </div>
                }
              >
                <div className="space-y-4">
                  {selectedAssetUrl && (
                    <img
                      src={selectedAssetUrl}
                      alt={selectedItem.title}
                      className="w-full max-h-80 object-cover rounded-lg border border-border"
                    />
                  )}

                  <div className="flex flex-wrap gap-4 text-xs text-text-secondary">
                    <span>Source {selectedItem.source}</span>
                    <span>Created {new Date(selectedItem.created_at).toLocaleString()}</span>
                    {selectedItem.updated_at ? <span>Updated {new Date(selectedItem.updated_at).toLocaleString()}</span> : null}
                  </div>

                  {selectedMetadata.url ? (
                    <a
                      href={selectedMetadata.url}
                      target="_blank"
                      rel="noreferrer"
                      className="inline-flex items-center gap-2 text-xs text-accent hover:underline"
                    >
                      <Eye className="w-3 h-3" />
                      View source page
                    </a>
                  ) : null}

                  {selectedItem.type === 'web_research' && enrichingItemId === selectedItem.id ? (
                    <div className="p-3 rounded-lg bg-accent/10 border border-accent/20 text-sm text-accent">
                      Running text intelligence on this source...
                    </div>
                  ) : null}

                  {selectedSummary ? (
                    <div className="p-4 rounded-lg bg-white/5 border border-border">
                      <p className="text-sm font-semibold mb-2">Summary</p>
                      <p className="text-sm text-white whitespace-pre-wrap">{selectedSummary}</p>
                    </div>
                  ) : null}

                  {enrichError ? (
                    <div className="p-4 rounded-lg bg-orange-500/10 border border-orange-500/30 text-sm text-orange-200">
                      {enrichError}
                    </div>
                  ) : null}

                  <details className="p-4 rounded-lg bg-white/5 border border-border">
                    <summary className="cursor-pointer text-sm font-semibold">Source Text</summary>
                    <pre className="mt-3 whitespace-pre-wrap text-sm text-white font-sans max-h-96 overflow-y-auto">
                      {selectedItem.full_content || selectedItem.content}
                    </pre>
                  </details>
                </div>
              </DetailSection>

              {selectedAnalysis && (
                <DetailSection title="Research Intelligence">
                  <div className="space-y-4">
                    {selectedAnalysis.sentiment?.label ? (
                      <div className="p-4 rounded-lg bg-white/5 border border-border">
                        <p className="text-sm font-semibold mb-2">Sentiment</p>
                        <p className="text-green-300">
                          {selectedAnalysis.sentiment.label} {(Number(selectedAnalysis.sentiment.confidence || 0) * 100).toFixed(1)}%
                        </p>
                      </div>
                    ) : null}

                    {selectedAnalysis.classification?.labels?.length ? (
                      <div className="space-y-2">
                        <p className="text-sm font-semibold">Classification</p>
                        {selectedAnalysis.classification.labels.map((label, index) => (
                          <div key={`${label}-${index}`} className="p-3 rounded-lg bg-white/5 border border-border">
                            <div className="flex items-center justify-between gap-3">
                              <span className="capitalize">{label}</span>
                              <span className="text-accent">
                                {(Number(selectedAnalysis.classification.scores?.[index] || 0) * 100).toFixed(1)}%
                              </span>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : null}

                    {selectedAnalysis.keywords?.length ? (
                      <div>
                        <p className="text-sm font-semibold mb-2">Keywords</p>
                        <div className="flex flex-wrap gap-2">
                          {selectedAnalysis.keywords.map((keyword) => (
                            <span key={keyword} className="px-3 py-1 rounded-full bg-accent/10 text-accent text-sm">
                              <Tag className="w-3 h-3 inline mr-1" />
                              {keyword}
                            </span>
                          ))}
                        </div>
                      </div>
                    ) : null}
                  </div>
                </DetailSection>
              )}

              {selectedItem.type === 'image_analysis' && (
                <DetailSection title="Image Analysis">
                  <div className="space-y-4">
                    <div className="grid grid-cols-2 gap-3 text-sm">
                      <div className="p-3 rounded-lg bg-white/5 border border-border">
                        <p className="text-text-secondary">File</p>
                        <p className="text-white">{selectedMetadata.filename || 'Unknown'}</p>
                      </div>
                      <div className="p-3 rounded-lg bg-white/5 border border-border">
                        <p className="text-text-secondary">Type</p>
                        <p className="text-white capitalize">{selectedMetadata.analysis_type || 'full'}</p>
                      </div>
                    </div>

                    <div>
                      <h4 className="text-sm font-semibold mb-2">Classifications</h4>
                      <div className="space-y-2">
                        {classifications.length ? classifications.map((item) => (
                          <div key={`${item.label}-${item.confidence}`} className="p-3 rounded-lg bg-white/5 border border-border">
                            <div className="flex items-center justify-between gap-3">
                              <span>{item.label}</span>
                              <span className="text-accent">{(item.confidence * 100).toFixed(1)}%</span>
                            </div>
                            <p className="text-xs text-text-secondary mt-1 capitalize">{item.category}</p>
                          </div>
                        )) : (
                          <p className="text-text-secondary text-sm">No classifications stored.</p>
                        )}
                      </div>
                    </div>

                    <div>
                      <h4 className="text-sm font-semibold mb-2">Detections</h4>
                      <div className="space-y-2">
                        {detections.length ? detections.map((item, index) => (
                          <div key={`${item.label}-${index}`} className="p-3 rounded-lg bg-white/5 border border-border">
                            <div className="flex items-center justify-between gap-3">
                              <span>{item.label}</span>
                              <span className="text-accent">{(item.confidence * 100).toFixed(1)}%</span>
                            </div>
                          </div>
                        )) : (
                          <p className="text-text-secondary text-sm">No detections stored.</p>
                        )}
                      </div>
                    </div>
                  </div>
                </DetailSection>
              )}

              {selectedItem.type === 'text_analysis' && (
                <DetailSection title="Text Intelligence">
                  <div className="space-y-4">
                    {selectedMetadata.summary?.text && (
                      <div className="p-4 rounded-lg bg-white/5 border border-border">
                        <p className="text-sm font-semibold mb-2">Summary</p>
                        <p className="text-sm text-white leading-relaxed">{selectedMetadata.summary.text}</p>
                      </div>
                    )}

                    {selectedMetadata.sentiment && (
                      <div className="p-4 rounded-lg bg-white/5 border border-border">
                        <p className="text-sm font-semibold mb-2">Sentiment</p>
                        <p className="text-green-300">
                          {selectedMetadata.sentiment.label} {(selectedMetadata.sentiment.confidence * 100).toFixed(1)}%
                        </p>
                      </div>
                    )}

                    {classificationScores.labels?.length ? (
                      <div className="space-y-2">
                        <p className="text-sm font-semibold">Classification</p>
                        {classificationScores.labels.map((label, index) => (
                          <div key={label} className="p-3 rounded-lg bg-white/5 border border-border">
                            <div className="flex items-center justify-between gap-3">
                              <span className="capitalize">{label}</span>
                              <span className="text-accent">
                                {(classificationScores.scores[index] * 100).toFixed(1)}%
                              </span>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : null}

                    {keywordList.length ? (
                      <div>
                        <p className="text-sm font-semibold mb-2">Keywords</p>
                        <div className="flex flex-wrap gap-2">
                          {keywordList.map((keyword) => (
                            <span key={keyword} className="px-3 py-1 rounded-full bg-accent/10 text-accent text-sm">
                              <Tag className="w-3 h-3 inline mr-1" />
                              {keyword}
                            </span>
                          ))}
                        </div>
                      </div>
                    ) : null}

                    {entityGroups.length ? (
                      <div className="space-y-2">
                        <p className="text-sm font-semibold">Entities</p>
                        {entityGroups.map((group) => (
                          <div key={group.type} className="p-3 rounded-lg bg-white/5 border border-border">
                            <p className="text-accent text-sm font-medium">{group.type}</p>
                            <p className="text-sm text-text-secondary mt-1">
                              {group.instances?.map((entry) => entry.text).join(', ')}
                            </p>
                          </div>
                        ))}
                      </div>
                    ) : null}
                  </div>
                </DetailSection>
              )}

              {selectedItem.type === 'anomaly_detection' && (
                <DetailSection title="Anomaly Detection">
                  <div className="space-y-4">
                    <div className="grid grid-cols-2 gap-3">
                      <div className="p-3 rounded-lg bg-white/5 border border-border">
                        <p className="text-text-secondary text-sm">Severity</p>
                        <p className="text-orange-300 capitalize">{selectedMetadata.severity || 'unknown'}</p>
                      </div>
                      <div className="p-3 rounded-lg bg-white/5 border border-border">
                        <p className="text-text-secondary text-sm">Anomalies</p>
                        <p className="text-white">{selectedMetadata.anomaly_count ?? 0}</p>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-3">
                      <div className="p-3 rounded-lg bg-white/5 border border-border">
                        <p className="text-text-secondary text-sm">Mean</p>
                        <p className="text-white">{Number(anomalyStats.mean || 0).toFixed(3)}</p>
                      </div>
                      <div className="p-3 rounded-lg bg-white/5 border border-border">
                        <p className="text-text-secondary text-sm">Std Dev</p>
                        <p className="text-white">{Number(anomalyStats.std || 0).toFixed(3)}</p>
                      </div>
                    </div>

                    <div className="p-4 rounded-lg bg-white/5 border border-border">
                      <p className="text-sm font-semibold mb-2">Anomaly Rate</p>
                      <p className="text-orange-300">{(Number(selectedMetadata.anomaly_rate || 0) * 100).toFixed(2)}%</p>
                    </div>

                    <div className="p-4 rounded-lg bg-white/5 border border-border">
                      <p className="text-sm font-semibold mb-2">Indices</p>
                      <p className="text-sm text-text-secondary">
                        {anomalyIndices.length ? anomalyIndices.join(', ') : 'No anomaly indices stored.'}
                      </p>
                    </div>
                  </div>
                </DetailSection>
              )}

              {selectedMetadata.models && (
                <DetailSection title="Model Stack">
                  <div className="space-y-2">
                    {Object.entries(selectedMetadata.models).map(([name, value]) => (
                      <div key={name} className="flex items-start justify-between gap-3 p-3 rounded-lg bg-white/5 border border-border">
                        <span className="capitalize text-text-secondary">{name}</span>
                        <span className="text-right text-sm text-white break-all">{value}</span>
                      </div>
                    ))}
                  </div>
                </DetailSection>
              )}
            </>
          ) : (
            <div className="glass rounded-xl p-12 text-center">
              <Sparkles className="w-14 h-14 mx-auto mb-4 text-accent" />
              <p className="text-white text-lg font-semibold">Open a record</p>
              <p className="text-text-secondary mt-2">
                Select a result on the left to inspect the stored report and model metadata.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default KnowledgeBase
