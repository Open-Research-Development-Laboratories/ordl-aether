import React, { useState } from 'react'
import axios from 'axios'
import { FileText, Send, Loader, CheckCircle, AlertCircle, Tag, Smile, BookOpen } from 'lucide-react'

function TextAnalysis() {
  const [text, setText] = useState('')
  const [analyzing, setAnalyzing] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const analyzeText = async () => {
    if (!text.trim()) return

    setAnalyzing(true)
    setError(null)

    try {
      const response = await axios.post('/analyze/text', {
        data_type: 'text',
        content: text,
        context: { tasks: ['all'] }
      })

      setResult(response.data)
    } catch (err) {
      console.error('Analysis error:', err)
      setError(err.response?.data?.detail || 'Analysis failed')
    } finally {
      setAnalyzing(false)
    }
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold gradient-text">Text Intelligence</h1>
        <p className="text-text-secondary mt-1">
          NLP analysis with summarization, NER, and sentiment
        </p>
      </div>

      {/* Input Area */}
      <div className="glass rounded-xl p-6">
        <label className="block text-sm font-medium mb-2">
          Enter text to analyze
        </label>
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Paste text here... (articles, reports, documents)"
          className="w-full h-48 p-4 rounded-lg bg-bg-dark border border-border text-white placeholder-text-secondary focus:border-accent focus:outline-none resize-none"
        />
        <div className="flex items-center justify-between mt-4 gap-4">
          <div className="text-sm text-text-secondary">
            <p>{text.length} characters</p>
            <p className="text-xs mt-1">First run may take a few minutes while NLP models download and warm up.</p>
          </div>
          <button
            onClick={analyzeText}
            disabled={analyzing || !text.trim()}
            className="px-6 py-3 bg-gradient-to-r from-accent to-blue-500 rounded-lg font-semibold text-white flex items-center gap-2 hover:opacity-90 transition-opacity disabled:opacity-50"
          >
            {analyzing ? (
              <>
                <Loader className="w-5 h-5 animate-spin" />
                Analyzing...
              </>
            ) : (
              <>
                <Send className="w-5 h-5" />
                Analyze Text
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
          {/* Summary */}
          {result.summary && (
            <div className="glass rounded-xl p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <BookOpen className="w-5 h-5 text-accent" />
                Summary
              </h3>
              <p className="text-white leading-relaxed">{result.summary.text}</p>
              <div className="flex items-center gap-4 mt-4 text-sm text-text-secondary">
                <span>Original: {result.summary.original_length} chars</span>
                <span>Summary: {result.summary.summary_length} chars</span>
                <span className="text-accent">
                  Compression: {(result.summary.compression_ratio * 100).toFixed(1)}%
                </span>
              </div>
            </div>
          )}

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Sentiment */}
            {result.sentiment && (
              <div className="glass rounded-xl p-6">
                <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                  <Smile className="w-5 h-5 text-accent" />
                  Sentiment Analysis
                </h3>
                <div className="flex items-center gap-4">
                  <div className={`text-4xl font-bold ${
                    result.sentiment.label === 'POSITIVE' ? 'text-green-400' : 'text-red-400'
                  }`}>
                    {result.sentiment.label === 'POSITIVE' ? ':)' : ':('}
                  </div>
                  <div>
                    <p className={`text-lg font-semibold ${
                      result.sentiment.label === 'POSITIVE' ? 'text-green-400' : 'text-red-400'
                    }`}>
                      {result.sentiment.label}
                    </p>
                    <p className="text-text-secondary">
                      Confidence: {(result.sentiment.confidence * 100).toFixed(1)}%
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Classification */}
            {result.classification && (
              <div className="glass rounded-xl p-6">
                <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                  <Tag className="w-5 h-5 text-accent" />
                  Classification
                </h3>
                <div className="space-y-2">
                  {result.classification.labels.slice(0, 3).map((label, idx) => (
                    <div key={idx} className="flex items-center justify-between">
                      <span className="capitalize">{label}</span>
                      <span className="text-accent">
                        {(result.classification.scores[idx] * 100).toFixed(1)}%
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Entities */}
          {result.entities && result.entities.length > 0 && (
            <div className="glass rounded-xl p-6">
              <h3 className="text-lg font-semibold mb-4">Named Entities</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {result.entities.map((entityGroup, idx) => (
                  <div key={idx} className="p-4 rounded-lg bg-white/5">
                    <h4 className="font-semibold text-accent mb-2 capitalize">
                      {entityGroup.type}
                    </h4>
                    <div className="flex flex-wrap gap-2">
                      {entityGroup.instances.slice(0, 5).map((instance, i) => (
                        <span
                          key={i}
                          className="px-2 py-1 text-xs rounded bg-white/10"
                        >
                          {instance.text}
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Keywords */}
          {result.keywords && result.keywords.length > 0 && (
            <div className="glass rounded-xl p-6">
              <h3 className="text-lg font-semibold mb-4">Keywords</h3>
              <div className="flex flex-wrap gap-2">
                {result.keywords.map((keyword, idx) => (
                  <span
                    key={idx}
                    className="px-3 py-1 rounded-full bg-accent/20 text-accent text-sm"
                  >
                    {keyword}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default TextAnalysis

