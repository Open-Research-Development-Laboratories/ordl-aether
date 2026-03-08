import React, { useState, useCallback } from 'react'
import axios from 'axios'
import { useDropzone } from 'react-dropzone'
import { Image, Upload, Loader, CheckCircle, AlertCircle, BarChart3 } from 'lucide-react'

function ImageAnalysis() {
  const [file, setFile] = useState(null)
  const [preview, setPreview] = useState(null)
  const [analyzing, setAnalyzing] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const onDrop = useCallback((acceptedFiles) => {
    const selectedFile = acceptedFiles[0]
    if (selectedFile) {
      setFile(selectedFile)
      setPreview(URL.createObjectURL(selectedFile))
      setResult(null)
      setError(null)
    }
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg', '.gif']
    },
    maxFiles: 1
  })

  const analyzeImage = async () => {
    if (!file) return

    setAnalyzing(true)
    setError(null)

    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('analysis_type', 'full')

      const response = await axios.post('/analyze/image', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
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
        <h1 className="text-3xl font-bold gradient-text">Image Analysis</h1>
        <p className="text-text-secondary mt-1">
          Computer vision powered by Vision Transformers
        </p>
      </div>

      {/* Upload Area */}
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-all ${
          isDragActive 
            ? 'border-accent bg-accent/10' 
            : 'border-border hover:border-accent/50 hover:bg-white/5'
        }`}
      >
        <input {...getInputProps()} />
        <Upload className="w-16 h-16 mx-auto mb-4 text-text-secondary" />
        {isDragActive ? (
          <p className="text-accent text-lg">Drop the image here...</p>
        ) : (
          <>
            <p className="text-white text-lg mb-2">
              Drag & drop an image, or click to select
            </p>
            <p className="text-text-secondary text-sm">
              Supports PNG, JPG, GIF (max 50MB)
            </p>
          </>
        )}
      </div>

      {/* Preview & Analyze */}
      {preview && (
        <div className="glass rounded-xl p-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Image Preview */}
            <div>
              <h3 className="text-lg font-semibold mb-4">Preview</h3>
              <img
                src={preview}
                alt="Preview"
                className="max-w-full max-h-96 rounded-lg"
              />
            </div>

            {/* Analyze Button */}
            <div className="flex flex-col justify-center items-center">
              <button
                onClick={analyzeImage}
                disabled={analyzing}
                className="px-8 py-4 bg-gradient-to-r from-accent to-blue-500 rounded-lg font-semibold text-white flex items-center gap-3 hover:opacity-90 transition-opacity disabled:opacity-50"
              >
                {analyzing ? (
                  <>
                    <Loader className="w-5 h-5 animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <Image className="w-5 h-5" />
                    Analyze Image
                  </>
                )}
              </button>
              <p className="text-text-secondary text-sm mt-4 text-center">
                Powered by Vision Transformer (ViT) model
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="p-4 rounded-lg bg-red-500/10 border border-red-500/30 flex items-center gap-3">
          <AlertCircle className="w-5 h-5 text-red-500" />
          <p className="text-red-400">{error}</p>
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="glass rounded-xl p-6 animate-slide-in">
          <div className="flex items-center gap-3 mb-6">
            <CheckCircle className="w-6 h-6 text-green-500" />
            <h3 className="text-xl font-semibold">Analysis Results</h3>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Classifications */}
            {result.classifications && (
              <div className="p-4 rounded-lg bg-white/5">
                <h4 className="font-semibold mb-4 flex items-center gap-2">
                  <BarChart3 className="w-4 h-4 text-accent" />
                  Classifications
                </h4>
                <div className="space-y-3">
                  {result.classifications.map((cls, idx) => (
                    <div key={idx} className="flex items-center justify-between">
                      <span className="text-sm">{cls.label}</span>
                      <div className="flex items-center gap-3">
                        <div className="w-32 h-2 bg-white/10 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-gradient-to-r from-accent to-blue-500"
                            style={{ width: `${cls.confidence * 100}%` }}
                          />
                        </div>
                        <span className="text-sm text-text-secondary w-12 text-right">
                          {(cls.confidence * 100).toFixed(1)}%
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Detections */}
            {result.detections && result.detections.length > 0 && (
              <div className="p-4 rounded-lg bg-white/5">
                <h4 className="font-semibold mb-4">Object Detections</h4>
                <div className="space-y-2">
                  {result.detections.map((det, idx) => (
                    <div key={idx} className="flex items-center justify-between p-2 rounded bg-white/5">
                      <span className="text-sm">{det.label}</span>
                      <span className="text-sm text-accent">
                        {(det.confidence * 100).toFixed(1)}%
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Image Info */}
            <div className="p-4 rounded-lg bg-white/5">
              <h4 className="font-semibold mb-4">Image Information</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-text-secondary">Dimensions</span>
                  <span>{result.image_size?.join(' x ')}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-text-secondary">Analysis Type</span>
                  <span className="capitalize">{result.analysis_type}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-text-secondary">Has Embedding</span>
                  <span>{result.embedding ? 'Yes' : 'No'}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default ImageAnalysis