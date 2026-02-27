import { FormEvent, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { extractJobs } from '../api/client'
import { useAppState } from '../context/AppStateContext'
import type { JobInput, JobModel, JobRequirement } from '../types/api'

export function JobsPage() {
  const { jobs, setJobs, profile, setAnalysis } = useAppState()
  const [rawJobs, setRawJobs] = useState<JobInput[]>(
    jobs.length
      ? jobs.map((j) => ({ title: j.title, description: '' }))
      : [{ title: '', description: '' }],
  )
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const navigate = useNavigate()

  function updateJob(index: number, field: 'title' | 'description', value: string) {
    setRawJobs((prev) => {
      const copy = [...prev]
      copy[index] = { ...copy[index], [field]: value }
      return copy
    })
  }

  function addJobRow() {
    setRawJobs((prev) => [...prev, { title: '', description: '' }])
  }

  async function handleExtract(e: FormEvent) {
    e.preventDefault()
    setError(null)
    setLoading(true)
    setAnalysis(null)

    try {
      const filled = rawJobs.filter(
        (j) => j.title.trim() && j.description.trim(),
      )
      if (!filled.length) {
        setError('Please enter at least one job with title and description.')
        return
      }
      const { jobs: structured } = await extractJobs(filled)
      setJobs(structured)
    } catch (err) {
      console.error(err)
      setError('Failed to extract job requirements.')
    } finally {
      setLoading(false)
    }
  }

  function goToResults() {
    if (!profile) {
      setError('Please extract your skills from the resume first.')
      return
    }
    if (!jobs.length) {
      setError('Please extract at least one target job.')
      return
    }
    navigate('/results')
  }

  return (
    <div className="page">
      <h1>Target Jobs</h1>
      <p>Paste job descriptions to extract their required skills.</p>

      <form onSubmit={handleExtract} className="card">
        {rawJobs.map((job, idx) => (
          <div key={idx} className="job-block">
            <label className="field">
              <span>Job title</span>
              <input
                type="text"
                value={job.title}
                onChange={(e) => updateJob(idx, 'title', e.target.value)}
                placeholder="Backend Developer"
              />
            </label>
            <label className="field">
              <span>Job description</span>
              <textarea
                rows={5}
                value={job.description}
                onChange={(e) =>
                  updateJob(idx, 'description', e.target.value)
                }
                placeholder="Paste the full job description here..."
              />
            </label>
          </div>
        ))}

        <button type="button" onClick={addJobRow} className="secondary">
          Add another job
        </button>

        <button type="submit" disabled={loading} className="primary">
          {loading ? 'Extracting skills…' : 'Extract job skills'}
        </button>

        {error && <p className="error">{error}</p>}
      </form>

      {jobs.length > 0 && (
        <section className="card">
          <h2>Structured Job Requirements</h2>
          {jobs.map((job: JobModel) => (
            <div key={job.title} className="job-summary">
              <h3>{job.title}</h3>
              {job.extracted_skills.length === 0 ? (
                <p>No skills extracted.</p>
              ) : (
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Skill ID</th>
                      <th>Weight</th>
                      <th>Required level</th>
                    </tr>
                  </thead>
                  <tbody>
                    {job.extracted_skills.map((req: JobRequirement) => (
                      <tr key={req.skill_id}>
                        <td>{req.skill_id}</td>
                        <td>{req.weight}</td>
                        <td>{req.required_level}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          ))}

          <button className="primary" type="button" onClick={goToResults}>
            Analyze fit & roadmap
          </button>
        </section>
      )}
    </div>
  )
}

