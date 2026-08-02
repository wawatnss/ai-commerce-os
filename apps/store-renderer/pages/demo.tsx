import { useRouter } from 'next/router'
import { useState } from 'react'
import axios from 'axios'
import Head from 'next/head'

interface DemoStep {
  key: string
  label: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  detail?: string | null
  duration_ms?: number | null
}

interface DemoGenerateResponse {
  success: boolean
  steps: DemoStep[]
  store_id?: number | null
  error?: string | null
}

// Mirrors the pipeline order in apps/api/app/demo/services/demo_service.py
const PIPELINE_STEPS: { key: string; label: string }[] = [
  { key: 'trend_detected', label: 'Trend detected' },
  { key: 'product_evaluated', label: 'Product evaluated' },
  { key: 'supplier_selected', label: 'Supplier selected' },
  { key: 'brand_generated', label: 'Brand generated' },
  { key: 'store_generated', label: 'Store generated' },
  { key: 'preview_ready', label: 'Preview ready' },
]

const REVEAL_DELAY_MS = 450

function sleep(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

export default function DemoPage() {
  const router = useRouter()
  const [running, setRunning] = useState(false)
  const [visibleSteps, setVisibleSteps] = useState<DemoStep[]>([])
  const [error, setError] = useState<string | null>(null)

  const generateDemoStore = async () => {
    setRunning(true)
    setError(null)
    setVisibleSteps([])

    try {
      const response = await axios.post<DemoGenerateResponse>('/api/v1/demo/generate')
      const result = response.data

      // Reveal each step one by one for a clear sense of progress, even
      // though the backend already ran the whole pipeline synchronously.
      for (const step of result.steps) {
        setVisibleSteps((prev) => [...prev, step])
        await sleep(REVEAL_DELAY_MS)
      }

      if (result.success && result.store_id) {
        await sleep(REVEAL_DELAY_MS)
        router.push(`/store-preview/${result.store_id}`)
      } else {
        setError(result.error || 'Demo generation failed.')
        setRunning(false)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not reach the API.')
      setRunning(false)
    }
  }

  return (
    <>
      <Head>
        <title>Generate Demo Store - AI Commerce OS</title>
      </Head>
      <div
        style={{
          minHeight: '100vh',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '40px 20px',
          backgroundColor: '#F9FAFB',
          fontFamily: 'Inter, sans-serif',
        }}
      >
        <div style={{ maxWidth: '560px', width: '100%', textAlign: 'center' }}>
          <h1 style={{ fontSize: '32px', fontWeight: 'bold', color: '#1F2937', marginBottom: '12px' }}>
            End-to-End Demo
          </h1>
          <p style={{ fontSize: '16px', color: '#6B7280', marginBottom: '32px' }}>
            Runs the entire platform pipeline - trend detection, product
            evaluation, supplier selection, brand generation and store
            generation - using local rule-based logic only. No external AI
            API is called.
          </p>

          <button
            onClick={generateDemoStore}
            disabled={running}
            style={{
              backgroundColor: running ? '#93C5FD' : '#2563EB',
              color: '#FFFFFF',
              border: 'none',
              borderRadius: '8px',
              padding: '16px 32px',
              fontSize: '18px',
              fontWeight: 'bold',
              cursor: running ? 'not-allowed' : 'pointer',
              transition: 'background-color 0.2s ease',
            }}
          >
            {running ? 'Generating...' : 'Generate Demo Store'}
          </button>

          <div style={{ marginTop: '40px', textAlign: 'left' }}>
            {PIPELINE_STEPS.map((pipelineStep) => {
              const revealed = visibleSteps.find((s) => s.key === pipelineStep.key)
              const isDone = revealed?.status === 'completed'
              const isFailed = revealed?.status === 'failed'

              return (
                <div
                  key={pipelineStep.key}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px',
                    padding: '10px 16px',
                    marginBottom: '8px',
                    borderRadius: '8px',
                    backgroundColor: revealed ? '#FFFFFF' : 'transparent',
                    border: revealed ? '1px solid #E5E7EB' : '1px solid transparent',
                    opacity: revealed ? 1 : 0.4,
                    transition: 'all 0.3s ease',
                  }}
                >
                  <span
                    style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      width: '24px',
                      height: '24px',
                      borderRadius: '50%',
                      fontSize: '14px',
                      fontWeight: 'bold',
                      color: '#FFFFFF',
                      backgroundColor: isFailed ? '#EF4444' : isDone ? '#10B981' : '#D1D5DB',
                    }}
                  >
                    {isFailed ? '!' : isDone ? '✓' : ''}
                  </span>
                  <span style={{ fontSize: '15px', color: '#1F2937', fontWeight: revealed ? 600 : 400 }}>
                    {pipelineStep.label}
                  </span>
                  {revealed?.detail && (
                    <span style={{ fontSize: '13px', color: '#EF4444', marginLeft: 'auto' }}>
                      {revealed.detail}
                    </span>
                  )}
                </div>
              )
            })}
          </div>

          {error && (
            <p style={{ marginTop: '24px', color: '#EF4444', fontSize: '14px' }}>
              {error}
            </p>
          )}
        </div>
      </div>
    </>
  )
}
