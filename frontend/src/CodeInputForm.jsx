import { useState } from 'react'

const styles = `
  .form-section-label {
    display: block;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.07em;
    text-transform: uppercase;
    color: #6b6b80;
    margin-bottom: 8px;
  }

  .tab-group {
    display: flex;
    gap: 6px;
    background: #0d0d0f;
    border: 1px solid #1e1e2e;
    border-radius: 10px;
    padding: 5px;
    margin-bottom: 20px;
  }

  .tab-btn {
    flex: 1;
    padding: 8px 14px;
    border: none;
    border-radius: 7px;
    background: transparent;
    color: #6b6b80;
    font-size: 13px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.18s ease;
  }

  .tab-btn.active {
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    color: #fff;
    font-weight: 600;
  }

  .tab-btn:not(.active):hover {
    background: #1e1e2e;
    color: #e2e2e8;
  }

  .form-row {
    margin-bottom: 18px;
  }

  .lang-input {
    width: 100%;
    background: #0d0d0f;
    border: 1px solid #1e1e2e;
    border-radius: 8px;
    padding: 10px 14px;
    color: #e2e2e8;
    font-size: 14px;
    outline: none;
    transition: border-color 0.18s;
  }

  .lang-input:focus {
    border-color: #6366f1;
  }

  .lang-input::placeholder { color: #3a3a4a; }

  .code-textarea {
    width: 100%;
    background: #0d0d0f;
    border: 1px solid #1e1e2e;
    border-radius: 10px;
    padding: 14px;
    color: #c9d1d9;
    font-family: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', monospace;
    font-size: 13px;
    line-height: 1.7;
    resize: vertical;
    outline: none;
    transition: border-color 0.18s;
    min-height: 220px;
  }

  .code-textarea:focus { border-color: #6366f1; }
  .code-textarea::placeholder { color: #3a3a4a; }

  .file-drop {
    border: 2px dashed #1e1e2e;
    border-radius: 10px;
    padding: 36px 20px;
    text-align: center;
    cursor: pointer;
    transition: all 0.18s;
    position: relative;
    margin-bottom: 4px;
  }

  .file-drop:hover { border-color: #6366f1; background: rgba(99,102,241,0.04); }
  .file-drop input[type="file"] {
    position: absolute; inset: 0; opacity: 0; cursor: pointer; width: 100%; height: 100%;
  }

  .file-drop-icon { font-size: 28px; margin-bottom: 8px; }
  .file-drop-text { color: #6b6b80; font-size: 14px; }
  .file-drop-text strong { color: #a78bfa; }
  .file-name { color: #a78bfa; font-size: 13px; margin-top: 8px; }

  .submit-btn {
    width: 100%;
    padding: 13px;
    border: none;
    border-radius: 10px;
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    color: #fff;
    font-size: 15px;
    font-weight: 600;
    cursor: pointer;
    letter-spacing: 0.02em;
    transition: opacity 0.18s, transform 0.12s;
    margin-top: 6px;
  }

  .submit-btn:hover:not(:disabled) { opacity: 0.88; transform: translateY(-1px); }
  .submit-btn:active:not(:disabled) { transform: translateY(0); }
  .submit-btn:disabled { opacity: 0.45; cursor: not-allowed; }
`

export default function CodeInputForm({ onResult, onError, onLoading }) {
  const [inputType, setInputType] = useState('paste')
  const [code,      setCode]      = useState('')
  const [file,      setFile]      = useState(null)
  const [language,  setLanguage]  = useState('')
  const [busy,      setBusy]      = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setBusy(true)
    onLoading(true)
    onError(null)
    onResult(null)

    const formData = new FormData()
    formData.append('input_type', inputType)
    if (language) formData.append('language', language)

    if (inputType === 'paste') {
      formData.append('code', code)
    } else {
      if (!file) {
        onError('Please select a file to upload.')
        onLoading(false)
        setBusy(false)
        return
      }
      formData.append('file', file)
    }

    try {
      const res = await fetch('/api/analyze', { method: 'POST', body: formData })
      let data
      try { data = await res.json() }
      catch { throw new Error('Server returned a non-JSON response.') }
      if (!res.ok) { onError(data.error || `Server error ${res.status}`); return }
      onResult(data)
    } catch (err) {
      onError(err instanceof TypeError
        ? "Couldn't reach the server. Is the backend running?"
        : err.message)
    } finally {
      onLoading(false)
      setBusy(false)
    }
  }

  const tabs = [
    { id: 'paste', label: '✦ Paste Code' },
    { id: 'file',  label: '⬆ Upload File' },
    { id: 'zip',   label: '🗜 Upload Zip' },
  ]

  return (
    <>
      <style>{styles}</style>
      <form onSubmit={handleSubmit}>

        {/* Mode tabs */}
        <div className="tab-group">
          {tabs.map(t => (
            <button
              key={t.id}
              type="button"
              className={`tab-btn ${inputType === t.id ? 'active' : ''}`}
              onClick={() => { setInputType(t.id); setFile(null) }}
            >
              {t.label}
            </button>
          ))}
        </div>

        {/* Language hint */}
        <div className="form-row">
          <label className="form-section-label">Language hint (optional)</label>
          <input
            className="lang-input"
            type="text"
            placeholder="python · javascript · java · go · …"
            value={language}
            onChange={e => setLanguage(e.target.value)}
          />
        </div>

        {/* Code input */}
        <div className="form-row">
          <label className="form-section-label">
            {inputType === 'paste' ? 'Source Code' : inputType === 'zip' ? 'Zip Archive' : 'Source File'}
          </label>

          {inputType === 'paste' ? (
            <textarea
              className="code-textarea"
              placeholder="// Paste your code here…"
              value={code}
              onChange={e => setCode(e.target.value)}
              required
              spellCheck={false}
            />
          ) : (
            <div className="file-drop">
              <input
                type="file"
                accept={inputType === 'zip' ? '.zip' : undefined}
                onChange={e => setFile(e.target.files[0] ?? null)}
                required
              />
              <div className="file-drop-icon">{inputType === 'zip' ? '🗜' : '📄'}</div>
              <div className="file-drop-text">
                <strong>Click to browse</strong> or drag & drop
              </div>
              {file && <div className="file-name">📎 {file.name}</div>}
            </div>
          )}
        </div>

        <button className="submit-btn" type="submit" disabled={busy}>
          {busy ? 'Analysing…' : 'Analyse Code →'}
        </button>
      </form>
    </>
  )
}
