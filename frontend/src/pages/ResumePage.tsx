import { useState, useRef } from 'react'
import type { FormEvent, DragEvent } from 'react'
import { parseResumeFromFile, parseResumeFromText } from '../api/client'
import { useAppState } from '../context/AppStateContext'
import type { UserSkill } from '../types/api'

export function ResumePage() {
  const { profile, setProfile, setAnalysis } = useAppState()
  const [file, setFile] = useState<File | null>(null)
  const [text, setText] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [isDragOver, setIsDragOver] = useState(false)
  
  const fileInputRef = useRef<HTMLInputElement>(null)

  function handleFileChange(selectedFile: File | null) {
     if (selectedFile && (selectedFile.type === "application/pdf" || selectedFile.type === "text/plain" || selectedFile.name.endsWith('.docx'))) {
        setFile(selectedFile)
     } else {
        setError('Please upload a valid PDF, DOCX, or TXT file.')
     }
  }

  function handleDragOver(e: DragEvent<HTMLDivElement>) {
    e.preventDefault()
    setIsDragOver(true)
  }

  function handleDragLeave(e: DragEvent<HTMLDivElement>) {
    e.preventDefault()
    setIsDragOver(false)
  }

  function handleDrop(e: DragEvent<HTMLDivElement>) {
    e.preventDefault()
    setIsDragOver(false)
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileChange(e.dataTransfer.files[0])
    }
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setAnalysis(null)

    try {
      let data
      if (file) {
        data = await parseResumeFromFile(file)
      } else if (text.trim()) {
        data = await parseResumeFromText(text)
      } else {
        setError('Please upload a file or paste resume text.')
        return
      }
      setProfile(data.profile)
    } catch (err) {
      console.error(err)
      setError('Failed to parse resume. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page">
      <h1>Resume & Skills</h1>
      <p>Upload your resume or paste the text to extract your skills profile.</p>

      <form onSubmit={handleSubmit} className="card">
        <label className="field">
          <span>Upload PDF/DOCX/TXT</span>
          <div 
            className={`drop-zone ${isDragOver ? 'drag-over' : ''}`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            style={{ 
              border: '2px dashed #007bff', 
              borderRadius: '8px', 
              padding: '40px', 
              textAlign: 'center',
              cursor: 'pointer',
              backgroundColor: isDragOver ? '#e9f5ff' : '#fafafa',
              transition: 'background-color 0.2s ease',
              marginBottom: '10px'
            }}
          >
            <input
              type="file"
              accept=".pdf,.txt,.docx"
              ref={fileInputRef}
              onChange={(e) => handleFileChange(e.target.files?.[0] ?? null)}
              style={{ display: 'none' }}
            />
            {file ? (
              <p style={{ margin: 0, fontWeight: 'bold', color: '#0056b3' }}>File selected: {file.name}</p>
            ) : (
              <p style={{ margin: 0, color: '#666' }}>Drag and drop your file here, or click to browse</p>
            )}
          </div>
        </label>

        <div className="or-separator">or</div>

        <label className="field">
          <span>Paste resume text</span>
          <textarea
            rows={8}
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Paste your resume here..."
          />
        </label>

        <button type="submit" disabled={loading} className="primary">
          {loading ? 'Analyzing…' : 'Extract Skills'}
        </button>

        {error && <p className="error">{error}</p>}
      </form>

      {profile && (
        <section className="card">
          <h2>Extracted Skills</h2>
          {profile.skills.length === 0 ? (
            <p>No skills detected yet.</p>
          ) : (
            <table className="data-table">
              <thead>
                <tr>
                  <th>Skill</th>
                  <th>Proficiency</th>
                  <th>Evidence</th>
                </tr>
              </thead>
              <tbody>
                {profile.skills.map((s: UserSkill) => (
                  <tr key={s.skill_id}>
                    <td>{s.name}</td>
                    <td>{s.proficiency}</td>
                    <td>{s.evidence_count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </section>
      )}
    </div>
  )
}

