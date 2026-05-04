import { useState, useEffect } from 'react';
import axios from 'axios';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell
} from 'recharts';
import type { DemoResult, KwJob, GrJob } from './App';

const API_BASE = 'http://localhost:8000/api';

interface HistorySession {
  filename: string;
  timestamp: string;
  skills: string[];
  keyword_recommendations: KwJob[];
  graph_recommendations: GrJob[];
  keyword_scores: number[];
  graph_scores: number[];
  total_jobs: number;
}

const colors = { kw: '#5c5c78', gr: '#00d4ff' };

const tooltipStyle = {
  background: '#1e1e2a', border: '1px solid rgba(255,255,255,0.08)',
  borderRadius: 8, fontSize: 13, color: '#f0f0f5',
};

const Research = ({ currentResult }: { currentResult: DemoResult | null }) => {
  const [showHistory, setShowHistory] = useState(false);
  const [history, setHistory] = useState<HistorySession[]>([]);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [selectedSession, setSelectedSession] = useState<HistorySession | null>(null);

  const loadHistory = async () => {
    setHistoryLoading(true);
    try {
      const res = await axios.get(`${API_BASE}/history`);
      setHistory(res.data.sessions || []);
    } catch { setHistory([]); }
    finally { setHistoryLoading(false); }
  };

  const openHistory = () => { setShowHistory(true); loadHistory(); };

  const viewSession = (session: HistorySession) => {
    setSelectedSession(session);
    setShowHistory(false);
  };

  const formatTime = (ts: string) => {
    try {
      const d = new Date(ts);
      return d.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }) + ' ' +
             d.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' });
    } catch { return ts; }
  };

  // Determine what data to show: selected history session, or current result
  const activeKw: KwJob[] = selectedSession?.keyword_recommendations || currentResult?.keyword_recommendations || [];
  const activeGr: GrJob[] = selectedSession?.graph_recommendations || currentResult?.graph_recommendations || [];
  const activeSkills: string[] = selectedSession?.skills || currentResult?.extracted_skills || [];
  const hasData = activeKw.length > 0 || activeGr.length > 0;

  // ── History Panel ──
  if (showHistory) return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 28 }}>
        <div>
          <h2 style={{ fontSize: 28, fontWeight: 800, letterSpacing: '-0.04em' }}>
            <span className="gradient-text">Analysis</span> History
          </h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: 14, marginTop: 6 }}>
            {history.length} resume{history.length !== 1 ? 's' : ''} analyzed — click to compare
          </p>
        </div>
        <button onClick={() => setShowHistory(false)} className="btn-ghost">← Back to Research</button>
      </div>

      {historyLoading ? (
        <div style={{ textAlign: 'center', padding: '80px 0', color: 'var(--text-muted)', fontSize: 13 }}>
          <div className="spinner" style={{ margin: '0 auto 12px' }} />
          Loading history...
        </div>
      ) : history.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '100px 24px' }}>
          <div style={{ fontSize: 48, marginBottom: 16, opacity: 0.15 }}>◈</div>
          <p style={{ fontSize: 16, fontWeight: 700, marginBottom: 8, color: 'var(--text-primary)' }}>No history yet</p>
          <p style={{ color: 'var(--text-muted)', fontSize: 13 }}>Upload a resume in the Recommendations tab to see results here</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          {history.map((session, i) => {
            const avgKw = session.keyword_scores?.length
              ? Math.round(session.keyword_scores.reduce((a, b) => a + b, 0) / session.keyword_scores.length * 100)
              : 0;
            const avgGr = session.graph_scores?.length
              ? Math.round(session.graph_scores.reduce((a, b) => a + b, 0) / session.graph_scores.length * 100)
              : 0;
            return (
              <div key={i} className="card" style={{ padding: 0, cursor: 'pointer' }}
                onClick={() => viewSession(session)}>
                <div style={{ padding: '18px 22px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 6 }}>
                        <span style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-dim)', fontFamily: 'var(--font-mono)' }}>
                          #{history.length - i}
                        </span>
                        <span style={{ fontSize: 14, fontWeight: 600, color: 'var(--text-primary)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                          {session.filename || 'Unknown file'}
                        </span>
                        <span style={{ fontSize: 11, color: 'var(--text-muted)', fontWeight: 500 }}>
                          {formatTime(session.timestamp)}
                        </span>
                      </div>
                      <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap', marginTop: 6 }}>
                        {session.skills.slice(0, 8).map(s => (
                          <span key={s} className="skill-pill" style={{ fontSize: 10, padding: '2px 8px' }}>{s}</span>
                        ))}
                        {session.skills.length > 8 && (
                          <span style={{ fontSize: 11, color: 'var(--text-dim)', padding: '4px 8px' }}>+{session.skills.length - 8}</span>
                        )}
                      </div>
                    </div>
                    <div style={{ display: 'flex', gap: 20, marginLeft: 16, flexShrink: 0 }}>
                      <div style={{ textAlign: 'center' }}>
                        <p style={{ fontSize: 9, fontWeight: 700, color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>Keyword</p>
                        <p style={{ fontSize: 18, fontWeight: 800, color: colors.kw, fontFamily: 'var(--font-mono)' }}>{avgKw}%</p>
                      </div>
                      <div style={{ textAlign: 'center' }}>
                        <p style={{ fontSize: 9, fontWeight: 700, color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>Graph</p>
                        <p style={{ fontSize: 18, fontWeight: 800, fontFamily: 'var(--font-mono)', background: 'var(--gradient-primary)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>{avgGr}%</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );

  // ── Empty state ──
  if (!hasData) return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 32 }}>
        <div>
          <h2 style={{ fontSize: 28, fontWeight: 800, letterSpacing: '-0.04em' }}>
            <span className="gradient-text">Research</span> Comparison
          </h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: 14, marginTop: 6 }}>
            Keyword Matching vs Graph Traversal — side by side
          </p>
        </div>
        <button onClick={openHistory} className="btn-ghost">📋 History</button>
      </div>
      <div style={{ textAlign: 'center', padding: '100px 24px' }}>
        <div style={{ fontSize: 48, marginBottom: 16, opacity: 0.15 }}>◈</div>
        <h3 style={{ fontSize: 18, fontWeight: 700, marginBottom: 8, color: 'var(--text-primary)' }}>No analysis data</h3>
        <p style={{ color: 'var(--text-muted)', fontSize: 14, maxWidth: 420, margin: '0 auto', lineHeight: 1.7 }}>
          Upload a resume in the <strong style={{ color: 'var(--accent-cyan)' }}>Recommendations</strong> tab, or check{' '}
          <button onClick={openHistory} style={{ background: 'none', border: 'none', color: 'var(--accent-purple)', cursor: 'pointer', fontWeight: 600, fontSize: 14, textDecoration: 'underline' }}>History</button>{' '}
          for past analyses.
        </p>
      </div>
    </div>
  );

  // ── Compute comparison data ──
  const kwAvg = activeKw.length ? activeKw.slice(0, 5).reduce((s, j) => s + j.score, 0) / Math.min(activeKw.length, 5) * 100 : 0;
  const grAvg = activeGr.length ? activeGr.slice(0, 5).reduce((s, j) => s + j.score, 0) / Math.min(activeGr.length, 5) * 100 : 0;
  const improvement = grAvg - kwAvg;

  const comparisonChartData = [
    { name: 'Keyword', value: Math.round(kwAvg) },
    { name: 'Graph', value: Math.round(grAvg) },
  ];

  // Per-job comparison (top 5)
  const top5Kw = activeKw.slice(0, 5);
  const top5Gr = activeGr.slice(0, 5);

  const perJobData = top5Gr.map((grJob, i) => ({
    name: grJob.title.length > 18 ? grJob.title.slice(0, 18) + '…' : grJob.title,
    graph: Math.round(grJob.score * 100),
    keyword: top5Kw[i] ? Math.round(top5Kw[i].score * 100) : 0,
  }));

  // ── Comparison View ──
  return (
    <div>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 32 }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 10 }}>
            <span className="badge badge-ghost">
              {selectedSession ? selectedSession.filename : 'Current Resume'}
            </span>
            {selectedSession && (
              <span style={{ fontSize: 11, color: 'var(--text-dim)' }}>{formatTime(selectedSession.timestamp)}</span>
            )}
          </div>
          <h2 style={{ fontSize: 28, fontWeight: 800, letterSpacing: '-0.04em' }}>
            <span className="gradient-text">Research</span> Comparison
          </h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: 14, marginTop: 6 }}>
            Keyword Matching vs Graph Traversal Engine — {activeSkills.length} skills · Top 5 recommendations
          </p>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <button onClick={openHistory} className="btn-ghost">📋 History</button>
          {selectedSession && (
            <button onClick={() => setSelectedSession(null)} className="btn-ghost">← Current</button>
          )}
        </div>
      </div>

      {/* Stat Cards Row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12, marginBottom: 28 }}>
        <StatCard label="Keyword Avg" value={`${Math.round(kwAvg)}%`} color={colors.kw} />
        <StatCard label="Graph Avg" value={`${Math.round(grAvg)}%`} gradient />
        <StatCard label="Improvement" value={`${improvement >= 0 ? '+' : ''}${improvement.toFixed(1)}%`}
          color={improvement >= 0 ? 'var(--accent-green)' : 'var(--accent-rose)'} />
        <StatCard label="Skills Extracted" value={String(activeSkills.length)} color="var(--text-primary)" />
      </div>

      {/* Extracted Skills */}
      <div style={{ marginBottom: 28 }}>
        <p className="section-title">Extracted Skills</p>
        <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
          {activeSkills.map(s => <span key={s} className="skill-pill">{s}</span>)}
        </div>
      </div>

      {/* Charts */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 28 }}>
        {/* Overall Comparison */}
        <div className="card">
          <p className="section-title">Overall Average Score</p>
          <div style={{ height: 220 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={comparisonChartData} margin={{ top: 8, right: 8, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.04)" />
                <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fill: '#9898b0', fontSize: 12, fontWeight: 600 }} />
                <YAxis unit="%" axisLine={false} tickLine={false} tick={{ fill: '#5c5c78', fontSize: 11 }} domain={[0, 100]} />
                <Tooltip cursor={{ fill: 'rgba(255,255,255,0.02)' }} contentStyle={tooltipStyle} />
                <Bar dataKey="value" radius={[6, 6, 0, 0]} barSize={56}>
                  <Cell fill={colors.kw} />
                  <Cell fill={colors.gr} />
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Per-Job Comparison */}
        <div className="card">
          <p className="section-title">Top-5 Job Score Comparison</p>
          <div style={{ height: 220 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={perJobData} layout="vertical" margin={{ top: 0, right: 8, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="rgba(255,255,255,0.04)" />
                <XAxis type="number" unit="%" axisLine={false} tickLine={false} tick={{ fill: '#5c5c78', fontSize: 10 }} domain={[0, 100]} />
                <YAxis type="category" dataKey="name" axisLine={false} tickLine={false}
                  tick={{ fill: '#9898b0', fontSize: 10, fontWeight: 500 }} width={100} />
                <Tooltip cursor={{ fill: 'rgba(255,255,255,0.02)' }} contentStyle={tooltipStyle} />
                <Bar dataKey="keyword" fill={colors.kw} radius={[0, 4, 4, 0]} barSize={10} name="Keyword" />
                <Bar dataKey="graph" fill={colors.gr} radius={[0, 4, 4, 0]} barSize={10} name="Graph" />
              </BarChart>
            </ResponsiveContainer>
          </div>
          {/* Legend */}
          <div style={{ display: 'flex', gap: 20, justifyContent: 'center', marginTop: 12 }}>
            <div className="legend-item"><div className="legend-dot" style={{ background: colors.kw }} /><span style={{ fontSize: 11 }}>Keyword</span></div>
            <div className="legend-item"><div className="legend-dot" style={{ background: colors.gr }} /><span style={{ fontSize: 11 }}>Graph</span></div>
          </div>
        </div>
      </div>

      {/* Side-by-Side Job Lists */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 28 }}>
        {/* Keyword Column */}
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 14 }}>
            <span className="badge badge-ghost">Keyword Matching</span>
            <span style={{ fontSize: 11, color: 'var(--text-dim)' }}>Baseline</span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {top5Kw.map((job, i) => (
              <KwJobCard key={job.id} job={job} rank={i + 1} />
            ))}
          </div>
        </div>

        {/* Graph Column */}
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 14 }}>
            <span className="badge badge-cyan">Graph Engine</span>
            <span style={{ fontSize: 11, color: 'var(--text-dim)' }}>Proposed</span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {top5Gr.map((job, i) => (
              <GrJobCard key={job.id} job={job} rank={i + 1} />
            ))}
          </div>
        </div>
      </div>

      {/* Key Finding */}
      <div className="card" style={{
        borderColor: improvement > 0 ? 'rgba(0, 212, 255, 0.15)' : 'var(--border-default)',
        background: improvement > 0 ? 'linear-gradient(135deg, rgba(0, 212, 255, 0.03) 0%, var(--bg-card) 100%)' : undefined,
      }}>
        <p className="section-title">Key Finding</p>
        <p style={{ fontSize: 14, color: 'var(--text-secondary)', lineHeight: 1.8 }}>
          {improvement > 0 ? (
            <>The <strong style={{ color: 'var(--accent-cyan)' }}>graph-based engine</strong> outperforms keyword matching
            by <strong style={{ color: 'var(--accent-green)' }}>+{improvement.toFixed(1)}%</strong> on average.
            By traversing <em>SUBSET_OF</em> and <em>RELATED_TO</em> edges in Neo4j, the system identifies indirect
            semantic matches that direct keyword comparison misses entirely.</>
          ) : (
            <>For this particular resume, both approaches perform similarly. The graph engine still provides
            richer explanations by showing <em>how</em> skills connect via the ontology.</>
          )}
        </p>
      </div>
    </div>
  );
};

// ── Stat Card ──
const StatCard = ({ label, value, color, gradient }: {
  label: string; value: string; color?: string; gradient?: boolean;
}) => (
  <div className="card" style={{ textAlign: 'center' }}>
    <p style={{ fontSize: 10, fontWeight: 700, color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.1em' }}>
      {label}
    </p>
    <p style={{
      fontSize: 28, fontWeight: 800, marginTop: 6, fontFamily: 'var(--font-mono)',
      ...(gradient
        ? { background: 'var(--gradient-primary)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }
        : { color: color || 'var(--text-primary)' }),
    }}>
      {value}
    </p>
  </div>
);

// ── Keyword Job Card ──
const KwJobCard = ({ job, rank }: { job: KwJob; rank: number }) => {
  const [open, setOpen] = useState(false);
  const scorePct = Math.round(job.score * 100);
  return (
    <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
      <div style={{ padding: '14px 16px', cursor: 'pointer' }} onClick={() => setOpen(!open)}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, flex: 1, minWidth: 0 }}>
            <span style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-dim)', fontFamily: 'var(--font-mono)' }}>{rank}</span>
            <span style={{ fontSize: 13, fontWeight: 600, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', color: 'var(--text-primary)' }}>{job.title}</span>
          </div>
          <span style={{ fontSize: 14, fontWeight: 800, color: colors.kw, fontFamily: 'var(--font-mono)', marginLeft: 8 }}>{scorePct}%</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginTop: 8 }}>
          <div className="score-bar-bg" style={{ height: 4 }}>
            <div style={{ height: '100%', borderRadius: 999, background: colors.kw, width: `${scorePct}%`, transition: 'width 0.5s' }} />
          </div>
          <span style={{ fontSize: 10, color: 'var(--text-dim)', fontWeight: 600, whiteSpace: 'nowrap' }}>{job.match_ratio}</span>
        </div>
      </div>
      {open && (
        <div style={{ padding: '0 16px 14px', borderTop: '1px solid var(--border-subtle)' }}>
          <p style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 10, marginBottom: 8 }}>{job.explanation}</p>
          {job.matched?.length > 0 && (
            <div style={{ marginBottom: 6 }}>
              <p style={{ fontSize: 10, fontWeight: 700, color: 'var(--text-dim)', marginBottom: 4, textTransform: 'uppercase' }}>Matched</p>
              <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap' }}>
                {job.matched.map(s => <span key={s} className="badge badge-green" style={{ fontSize: 10, padding: '2px 8px' }}>{s}</span>)}
              </div>
            </div>
          )}
          {job.missing?.length > 0 && (
            <div>
              <p style={{ fontSize: 10, fontWeight: 700, color: 'var(--text-dim)', marginBottom: 4, textTransform: 'uppercase' }}>Missing</p>
              <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap' }}>
                {job.missing.map(s => <span key={s} className="badge badge-rose" style={{ fontSize: 10, padding: '2px 8px' }}>{s}</span>)}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

// ── Graph Job Card ──
const GrJobCard = ({ job, rank }: { job: GrJob; rank: number }) => {
  const [open, setOpen] = useState(false);
  const scorePct = Math.round(job.score * 100);
  const directCount = job.direct_matches?.length || 0;
  const graphCount = job.graph_matches?.length || 0;
  return (
    <div className="card" style={{ padding: 0, overflow: 'hidden', borderColor: rank === 1 ? 'rgba(0,212,255,0.2)' : undefined }}>
      <div style={{ padding: '14px 16px', cursor: 'pointer' }} onClick={() => setOpen(!open)}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, flex: 1, minWidth: 0 }}>
            <span style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-dim)', fontFamily: 'var(--font-mono)' }}>{rank}</span>
            <span style={{ fontSize: 13, fontWeight: 600, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', color: 'var(--text-primary)' }}>{job.title}</span>
          </div>
          <span style={{
            fontSize: 14, fontWeight: 800, fontFamily: 'var(--font-mono)', marginLeft: 8,
            background: 'var(--gradient-primary)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
          }}>{scorePct}%</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginTop: 8 }}>
          <div className="score-bar-bg" style={{ height: 4 }}>
            <div className="score-bar-fill" style={{ width: `${scorePct}%` }} />
          </div>
          <span style={{ fontSize: 10, color: 'var(--text-dim)', fontWeight: 600, whiteSpace: 'nowrap' }}>
            {directCount}+{graphCount}
          </span>
        </div>
      </div>
      {open && (
        <div style={{ padding: '0 16px 14px', borderTop: '1px solid var(--border-subtle)' }}>
          <p style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 10, marginBottom: 8 }}>{job.explanation}</p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
            {job.paths?.filter(p => p.type !== 'none').map((p, pi) => (
              <div key={pi} className={`path-tag ${p.type}`} style={{ fontSize: 11 }}>{p.label}</div>
            ))}
            {job.unmatched?.length > 0 && (
              <div style={{ marginTop: 4 }}>
                <p style={{ fontSize: 10, fontWeight: 700, color: 'var(--text-dim)', marginBottom: 4, textTransform: 'uppercase' }}>No connection</p>
                <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap' }}>
                  {job.unmatched.map(s => <span key={s} className="badge badge-rose" style={{ fontSize: 10, padding: '2px 8px' }}>{s}</span>)}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default Research;
