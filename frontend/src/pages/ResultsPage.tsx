import { useState } from 'react'
import type { FormEvent } from 'react'
import { runAnalysis, getRecommendations } from '../api/client'
import { useAppState } from '../context/AppStateContext'
import type { FitScorePerJob, GapItem, RoadmapItem, RecommendationModel } from '../types/api'

export function ResultsPage() {
  const { profile, jobs, analysis, recommendations, setAnalysis, setRecommendations } = useAppState()
  const [weeklyHours, setWeeklyHours] = useState<number | ''>('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleAnalyze(e: FormEvent) {
    e.preventDefault()
    if (!profile || jobs.length === 0) {
      setError('Please provide a resume and at least one job first.')
      return
    }
    setLoading(true)
    setError(null)

    try {
      const payload = {
        profile,
        jobs,
        weekly_hours: typeof weeklyHours === 'number' ? weeklyHours : undefined,
      }
      const [analysisResult, recsResult] = await Promise.all([
        runAnalysis(payload),
        getRecommendations(profile)
      ]);
      setAnalysis(analysisResult)
      setRecommendations(recsResult)
    } catch (err) {
      console.error(err)
      setError('Failed to run analysis.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page">
      <h1>Fit, Gaps & Roadmap</h1>
      <p>Run the full analysis and explore your job readiness and learning plan.</p>

      <form onSubmit={handleAnalyze} className="card">
        <label className="field">
          <span>Weekly learning hours (optional)</span>
          <input
            type="number"
            min={1}
            value={weeklyHours}
            onChange={(e) =>
              setWeeklyHours(
                e.target.value === '' ? '' : Number(e.target.value),
              )
            }
          />
        </label>

        <button type="submit" disabled={loading} className="primary">
          {loading ? 'Analyzing…' : 'Run analysis'}
        </button>

        {error && <p className="error">{error}</p>}
      </form>

      {analysis && (
        <>
          <section className="card">
            <h2>Job Recommendations (Top Matches)</h2>
            {recommendations.length === 0 ? (
              <p>No job recommendations found in graph.</p>
            ) : (
               <div className="recommendations-list">
                 {recommendations.map((rec: RecommendationModel, idx: number) => (
                   <div key={idx} className="job-card" style={{ border: '1px solid #ccc', borderRadius: '8px', padding: '16px', marginBottom: '16px' }}>
                     <h3 style={{ margin: '0 0 8px 0' }}>{rec.title} - <span style={{ color: '#666' }}>{rec.company}</span></h3>
                     <div style={{ marginBottom: '8px', fontWeight: 'bold', color: 'green' }}>
                       Match Ratio: {rec.match_ratio}%
                     </div>
                     <ul style={{ paddingLeft: '20px', margin: '0 0 16px 0', fontSize: '14px' }}>
                       {rec.explanation.map((ex, i) => <li key={i}>{ex}</li>)}
                     </ul>
                     <a href={rec.apply_url} target="_blank" rel="noreferrer" style={{ display: 'inline-block', background: '#0056b3', color: '#fff', padding: '8px 16px', borderRadius: '4px', textDecoration: 'none' }}>
                        Apply Now
                     </a>
                   </div>
                 ))}
               </div>
            )}
          </section>

          <section className="card">
            <h2>Job Fit Ranking</h2>
            {analysis.fit_results.length === 0 ? (
              <p>No fit results yet.</p>
            ) : (
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Job</th>
                    <th>Fit score</th>
                    <th>Category</th>
                  </tr>
                </thead>
                <tbody>
                  {analysis.fit_results.map((r: FitScorePerJob) => (
                    <tr key={r.job.title}>
                      <td>{r.job.title}</td>
                      <td>{(r.fit_score * 100).toFixed(1)}%</td>
                      <td>{r.category}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </section>

          <section className="card">
            <h2>Skill Gaps (prioritized)</h2>
            {analysis.gaps.length === 0 ? (
              <p>No significant gaps detected.</p>
            ) : (
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Skill</th>
                    <th>Gap score</th>
                    <th>Difficulty</th>
                    <th>Learning hours</th>
                  </tr>
                </thead>
                <tbody>
                  {analysis.gaps.map((g: GapItem) => (
                    <tr key={g.skill_id}>
                      <td>{g.name}</td>
                      <td>{g.gap_score.toFixed(3)}</td>
                      <td>{g.difficulty}</td>
                      <td>{g.learning_hours}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </section>

          <section className="card">
            <h2>Learning Roadmap</h2>
            {analysis.roadmap.length === 0 ? (
              <p>You look ready to apply for your target roles.</p>
            ) : (
              <ul className="roadmap">
                {analysis.roadmap.map((step: RoadmapItem) => (
                  <li key={step.timeframe} className="roadmap-step">
                    <div className="roadmap-time">{step.timeframe}</div>
                    <div className="roadmap-content">
                      <div className="roadmap-title">
                        Focus: {step.learning_focus}
                      </div>
                      <div className="roadmap-meta">
                        ~{step.learning_hours} hours · Priority{' '}
                        {step.priority_score.toFixed(3)}
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </section>
        </>
      )}
    </div>
  )
}

