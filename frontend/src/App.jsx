// App.jsx
// The whole UI: complaint form (left) + AI Copilot chat (right).
// RULE from the demo: the form is READ-ONLY. Only the chat can change it.

import { useState } from 'react'
import { useSelector, useDispatch } from 'react-redux'
import { setForm } from './formSlice'

const API = 'http://localhost:8000'   // our FastAPI backend

// The form fields we show, in display order: [field key, label]
const FIELDS = [
  ['complainant_name', 'Complainant Name'],
  ['product_name', 'Product Name'],
  ['product_strength', 'Product Strength'],
  ['batch_number', 'Batch / Lot Number'],
  ['manufacturing_date', 'Manufacturing Date'],
  ['expiry_date', 'Expiry Date'],
  ['affected_quantity', 'Affected Quantity'],
  ['complaint_description', 'Complaint Description'],
]

const RISK_FIELDS = [
  ['severity', 'Severity'],
  ['recommended_action', 'Recommended Action'],
  ['risk_details', 'Risk Details'],
]

export default function App() {
  const form = useSelector((state) => state.form)  // READ the memory box
  const dispatch = useDispatch()                   // tool to WRITE to it

  const [messages, setMessages] = useState([       // the chat history
    { role: 'ai', text: 'Hi! Describe a complaint, or upload a PDF/email, and I will fill the form.' },
  ])
  const [input, setInput] = useState('')           // what's typed in the chat box
  const [loading, setLoading] = useState(false)    // waiting for AI?

  // ---- Send a typed message to POST /chat ----
  async function sendMessage() {
    if (!input.trim() || loading) return
    const userText = input
    setInput('')
    setMessages((m) => [...m, { role: 'user', text: userText }])
    setLoading(true)
    try {
      const res = await fetch(`${API}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userText, current_form_state: form }),
      })
      const data = await res.json()
      dispatch(setForm(data.form))   // update the memory box -> form re-renders
      setMessages((m) => [...m, { role: 'ai', text: 'Done! I updated the form and risk assessment.' }])
    } catch {
      setMessages((m) => [...m, { role: 'ai', text: 'Error: could not reach the backend. Is it running?' }])
    }
    setLoading(false)
  }

  // ---- Send an uploaded file to POST /upload ----
  async function uploadFile(e) {
    const file = e.target.files[0]
    if (!file || loading) return
    setMessages((m) => [...m, { role: 'user', text: `Uploaded: ${file.name}` }])
    setLoading(true)
    try {
      const fd = new FormData()
      fd.append('file', file)
      fd.append('current_form_state', JSON.stringify(form))
      const res = await fetch(`${API}/upload`, { method: 'POST', body: fd })
      const data = await res.json()
      dispatch(setForm(data.form))
      setMessages((m) => [...m, { role: 'ai', text: 'Document processed! Form and risk assessment updated.' }])
    } catch {
      setMessages((m) => [...m, { role: 'ai', text: 'Error processing the document.' }])
    }
    setLoading(false)
    e.target.value = ''   // allow re-uploading the same file
  }

  return (
    <div style={{ display: 'flex', height: '100vh', fontFamily: 'Inter, sans-serif', background: '#f4f6f8' }}>

      {/* ================= LEFT: THE FORM (read-only) ================= */}
      <div style={{ flex: 1, padding: 24, overflowY: 'auto', borderRight: '1px solid #ddd' }}>
        <h2 style={{ marginTop: 0 }}>Log Customer Complaint</h2>

        {FIELDS.map(([key, label]) => (
          <div key={key} style={{ marginBottom: 12 }}>
            <label style={{ fontSize: 13, fontWeight: 600, color: '#444' }}>{label}</label>
            <input
              value={form[key] ?? ''}
              readOnly
              placeholder="—"
              style={{ width: '100%', padding: 8, marginTop: 4, border: '1px solid #ccc',
                       borderRadius: 6, background: '#fff', boxSizing: 'border-box' }}
            />
          </div>
        ))}

        <h3>AI Copilot Risk Assessment</h3>
        {RISK_FIELDS.map(([key, label]) => (
          <div key={key} style={{ marginBottom: 12 }}>
            <label style={{ fontSize: 13, fontWeight: 600, color: '#444' }}>{label}</label>
            <textarea
              value={form[key] ?? ''}
              readOnly
              placeholder="—"
              rows={key === 'severity' ? 1 : 2}
              style={{ width: '100%', padding: 8, marginTop: 4, border: '1px solid #ccc',
                       borderRadius: 6, background: '#fffbe6', boxSizing: 'border-box', resize: 'none' }}
            />
          </div>
        ))}
      </div>

      {/* ================= RIGHT: AI COPILOT CHAT ================= */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', padding: 24 }}>
        <h2 style={{ marginTop: 0 }}>AIVOA Copilot</h2>

        {/* chat history */}
        <div style={{ flex: 1, overflowY: 'auto', marginBottom: 12 }}>
          {messages.map((m, i) => (
            <div key={i} style={{
              maxWidth: '80%', padding: '10px 14px', borderRadius: 12, marginBottom: 8,
              background: m.role === 'user' ? '#2563eb' : '#fff',
              color: m.role === 'user' ? '#fff' : '#111',
              marginLeft: m.role === 'user' ? 'auto' : 0,
              boxShadow: '0 1px 2px rgba(0,0,0,0.08)',
            }}>
              {m.text}
            </div>
          ))}
          {loading && <div style={{ color: '#888' }}>Thinking…</div>}
        </div>

        {/* input row: upload button + text box + send button */}
        <div style={{ display: 'flex', gap: 8 }}>
          <label style={{ padding: '10px 12px', background: '#e5e7eb', borderRadius: 8, cursor: 'pointer' }}>
            📎
            <input type="file" accept=".pdf" onChange={uploadFile} style={{ display: 'none' }} />
          </label>
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
            placeholder="Describe the complaint…"
            style={{ flex: 1, padding: 10, border: '1px solid #ccc', borderRadius: 8 }}
          />
          <button onClick={sendMessage} disabled={loading}
            style={{ padding: '10px 18px', background: '#2563eb', color: '#fff',
                     border: 'none', borderRadius: 8, cursor: 'pointer' }}>
            Send
          </button>
        </div>
      </div>
    </div>
  )
}