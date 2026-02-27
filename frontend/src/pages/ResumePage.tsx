import { FormEvent, useState } from 'react'
import { parseResumeFromFile, parseResumeFromText } from '../api/client'
import { useAppState } from '../context/AppStateContext'
import type { UserSkill } from '../types/api'

export function ResumePage() {
  const { profile, setProfile, setAnalysis } = useAppState()
  const [file, setFile] = useState<File | null>(null)
  const [text, setText] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

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
          <span>Upload PDF/TXT</span>
          <input
            type="file"
            accept=".pdf,.txt"
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          />
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

