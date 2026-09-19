import { useState } from 'react'
import CodeInputForm from './CodeInputForm'
import ResultsPanel from './ResultsPanel'

const styles = `
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    background: #0d0d0f;
    color: #e2e2e8;
    font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
    min-height: 100vh;
    line-height: 1.6;
  }

  ::-webkit-scrollbar { width: 6px; }
  ::-webkit-scrollbar-track { background: #1a1a1f; }
  ::-webkit-scrollbar-thumb { background: #3a3a4a; border-radius: 3px; }

  .app-shell {
    max-width: 900px;
    margin: 0 auto;
    padding: 40px 20px 80px;
  }

  .app-header {
    text-align: center;
    margin-bottom: 40px;
  }

  .app-header .badge {
    display: inline-block;
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    color: #fff;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 4px 12px;
    border-radius: 20px;
    margin-bottom: 14px;
  }

  .app-header h1 {
    font-size: clamp(26px, 5vw, 38px);
    font-weight: 700;
    background: linear-gradient(135deg, #e2e2e8 30%, #8b5cf6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.2;
    margin-bottom: 10px;
  }

  .app-header p {
    color: #6b6b80;
    font-size: 15px;
  }

  .card {
    background: #13131a;
    border: 1px solid #1e1e2e;
    border-radius: 16px;
    padding: 28px;
    margin-bottom: 24px;
  }

  .error-banner {
    display: flex;
    align-items: center;
    gap: 10px;
    background: rgba(239, 68, 68, 0.08);
    border: 1px solid rgba(239, 68, 68, 0.25);
    border-radius: 10px;
    padding: 14px 18px;
    color: #f87171;
    font-size: 14px;
    margin-bottom: 24px;
  }

  .loading-bar {
    height: 3px;
    background: linear-gradient(90deg, #6366f1, #8b5cf6, #a78bfa, #6366f1);
    background-size: 200% 100%;
    border-radius: 2px;
    margin-bottom: 24px;
    animation: shimmer 1.6s linear infinite;
  }

  .loading-text {
    text-align: center;
    color: #6b6b80;
    font-size: 14px;
    margin-bottom: 20px;
    letter-spacing: 0.03em;
  }

  @keyframes shimmer {
    0%   { background-position: 200% 0; }
    100% { background-position: -200% 0; }
  }
`

export default function App() {
  const [result,  setResult]  = useState(null)
  const [error,   setError]   = useState(null)
  const [loading, setLoading] = useState(false)

  return (
    <>
      <style>{styles}</style>
      <div className="app-shell">
        <header className="app-header">
          <div className="badge">AI Powered</div>
          <h1>AI Code Intelligence</h1>
          <p>Analyse, document, diagram and refactor your code instantly</p>
        </header>

        <div className="card">
          <CodeInputForm
            onResult={setResult}
            onError={setError}
            onLoading={setLoading}
          />
        </div>

        {loading && (
          <>
            <div className="loading-bar" />
            <p className="loading-text">Analysing your code with Qwen 2.5 Coder…</p>
          </>
        )}

        {error && (
          <div className="error-banner">
            <span>⚠</span> {error}
          </div>
        )}

        <ResultsPanel result={result} />
      </div>
    </>
  )
}
