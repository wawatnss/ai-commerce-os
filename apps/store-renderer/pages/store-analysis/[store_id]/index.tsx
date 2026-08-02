import { useState } from 'react'
import { GetServerSideProps } from 'next'
import Head from 'next/head'
import axios from 'axios'

interface Suggestion {
  id: string
  optimizer: string
  severity: 'high' | 'medium' | 'low' | 'info'
  title: string
  description: string
  applied: boolean
}

interface OptimizerResult {
  optimizer: string
  score: number
  suggestions: Suggestion[]
  details: Record<string, any>
}

interface ConversionReport {
  conversion_score: number
  seo_score: number
  ux_score: number
  trust_score: number
  persuasion_score: number
  strengths: string[]
  weaknesses: string[]
  recommended_actions: Suggestion[]
  optimizer_results: OptimizerResult[]
  generated_at: string
  demo_mode: boolean
}

interface StoreAnalysisPageProps {
  storeId: string
  report?: ConversionReport
  storeName?: string | null
  error?: string
}

const SEVERITY_COLORS: Record<string, string> = {
  high: '#EF4444',
  medium: '#F59E0B',
  low: '#3B82F6',
  info: '#6B7280',
}

function scoreColor(score: number): string {
  if (score >= 85) return '#10B981'
  if (score >= 65) return '#F59E0B'
  return '#EF4444'
}

function ScoreCard({ label, score }: { label: string; score: number }) {
  return (
    <div
      style={{
        flex: '1 1 140px',
        minWidth: '140px',
        padding: '20px',
        borderRadius: '12px',
        border: '1px solid #E5E7EB',
        backgroundColor: '#FFFFFF',
        textAlign: 'center',
      }}
    >
      <div style={{ fontSize: '32px', fontWeight: 'bold', color: scoreColor(score) }}>
        {Math.round(score)}
      </div>
      <div style={{ fontSize: '13px', color: '#6B7280', marginTop: '4px' }}>{label}</div>
    </div>
  )
}

export default function StoreAnalysisPage({ storeId, report: initialReport, storeName, error: initialError }: StoreAnalysisPageProps) {
  const [report, setReport] = useState<ConversionReport | undefined>(initialReport)
  const [error, setError] = useState<string | undefined>(initialError)
  const [running, setRunning] = useState(false)

  const runOptimization = async () => {
    setRunning(true)
    setError(undefined)
    try {
      const response = await axios.post(`/api/v1/stores/${storeId}/optimize`)
      setReport(response.data.report)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not reach the API.')
    } finally {
      setRunning(false)
    }
  }

  return (
    <>
      <Head>
        <title>Store Analysis - {storeName || `Store #${storeId}`}</title>
      </Head>
      <div style={{ minHeight: '100vh', backgroundColor: '#F9FAFB', fontFamily: 'Inter, sans-serif', padding: '40px 20px' }}>
        <div style={{ maxWidth: '900px', margin: '0 auto' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '16px', marginBottom: '24px' }}>
            <div>
              <h1 style={{ fontSize: '28px', fontWeight: 'bold', color: '#1F2937', margin: 0 }}>
                Conversion Analysis
              </h1>
              <p style={{ color: '#6B7280', marginTop: '4px' }}>
                {storeName || `Store #${storeId}`}
                {report?.demo_mode && (
                  <span style={{ marginLeft: '8px', fontSize: '12px', color: '#F59E0B', fontWeight: 'bold' }}>
                    DEMO MODE
                  </span>
                )}
              </p>
            </div>
            <button
              onClick={runOptimization}
              disabled={running}
              style={{
                backgroundColor: running ? '#93C5FD' : '#2563EB',
                color: '#FFFFFF',
                border: 'none',
                borderRadius: '8px',
                padding: '12px 24px',
                fontSize: '15px',
                fontWeight: 'bold',
                cursor: running ? 'not-allowed' : 'pointer',
              }}
            >
              {running ? 'Optimizing...' : 'Run Optimization'}
            </button>
          </div>

          {error && (
            <p style={{ color: '#EF4444', marginBottom: '16px' }}>{error}</p>
          )}

          {!report && !error && (
            <p style={{ color: '#6B7280' }}>No analysis available yet. Click &ldquo;Run Optimization&rdquo; to generate one.</p>
          )}

          {report && (
            <>
              <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', marginBottom: '32px' }}>
                <ScoreCard label="Conversion Score" score={report.conversion_score} />
                <ScoreCard label="SEO Score" score={report.seo_score} />
                <ScoreCard label="UX Score" score={report.ux_score} />
                <ScoreCard label="Trust Score" score={report.trust_score} />
                <ScoreCard label="Persuasion Score" score={report.persuasion_score} />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '32px' }}>
                <div style={{ backgroundColor: '#FFFFFF', border: '1px solid #E5E7EB', borderRadius: '12px', padding: '20px' }}>
                  <h2 style={{ fontSize: '16px', fontWeight: 'bold', color: '#10B981', marginTop: 0 }}>Strengths</h2>
                  <ul style={{ paddingLeft: '20px', color: '#374151', fontSize: '14px' }}>
                    {report.strengths.map((s, i) => (
                      <li key={i} style={{ marginBottom: '6px' }}>{s}</li>
                    ))}
                  </ul>
                </div>
                <div style={{ backgroundColor: '#FFFFFF', border: '1px solid #E5E7EB', borderRadius: '12px', padding: '20px' }}>
                  <h2 style={{ fontSize: '16px', fontWeight: 'bold', color: '#EF4444', marginTop: 0 }}>Weaknesses</h2>
                  <ul style={{ paddingLeft: '20px', color: '#374151', fontSize: '14px' }}>
                    {report.weaknesses.map((w, i) => (
                      <li key={i} style={{ marginBottom: '6px' }}>{w}</li>
                    ))}
                  </ul>
                </div>
              </div>

              <div style={{ backgroundColor: '#FFFFFF', border: '1px solid #E5E7EB', borderRadius: '12px', padding: '20px' }}>
                <h2 style={{ fontSize: '16px', fontWeight: 'bold', color: '#1F2937', marginTop: 0 }}>
                  Recommended Actions ({report.recommended_actions.length})
                </h2>
                {report.recommended_actions.map((action) => (
                  <div
                    key={action.id}
                    style={{
                      display: 'flex',
                      gap: '12px',
                      padding: '12px 0',
                      borderTop: '1px solid #F3F4F6',
                      alignItems: 'flex-start',
                    }}
                  >
                    <span
                      style={{
                        flexShrink: 0,
                        fontSize: '11px',
                        fontWeight: 'bold',
                        color: '#FFFFFF',
                        backgroundColor: SEVERITY_COLORS[action.severity] || '#6B7280',
                        borderRadius: '999px',
                        padding: '2px 10px',
                        textTransform: 'uppercase',
                      }}
                    >
                      {action.severity}
                    </span>
                    <div>
                      <div style={{ fontWeight: 600, color: '#1F2937', fontSize: '14px' }}>
                        {action.title}{' '}
                        <span style={{ fontWeight: 400, color: '#9CA3AF', fontSize: '12px' }}>
                          ({action.optimizer}{action.applied ? ', applied' : ', suggestion only'})
                        </span>
                      </div>
                      <div style={{ color: '#6B7280', fontSize: '13px', marginTop: '2px' }}>
                        {action.description}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
      </div>
    </>
  )
}

export const getServerSideProps: GetServerSideProps = async (context) => {
  const { store_id } = context.params ?? {}

  if (!store_id || typeof store_id !== 'string') {
    return { props: { storeId: '', error: 'Invalid store ID' } }
  }

  try {
    const response = await fetch(`http://localhost:8000/api/v1/stores/${store_id}/conversion-report`)
    if (!response.ok) {
      return { props: { storeId: store_id, error: `Failed to load analysis: ${response.statusText}` } }
    }

    const data = await response.json()

    let storeName: string | undefined
    try {
      const storeResponse = await fetch(`http://localhost:8000/api/v1/stores/${store_id}`)
      if (storeResponse.ok) {
        const storeData = await storeResponse.json()
        storeName = storeData.store_name
      }
    } catch {
      // Non-fatal: the analysis can still be shown without the store name.
    }

    return { props: { storeId: store_id, report: data.report, storeName: storeName ?? null } }
  } catch (error) {
    return {
      props: {
        storeId: store_id,
        error: `Error fetching analysis: ${error instanceof Error ? error.message : 'Unknown error'}`,
      },
    }
  }
}
