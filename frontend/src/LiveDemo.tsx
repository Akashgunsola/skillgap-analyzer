import { useState, useRef } from 'react';
import axios from 'axios';

const API_BASE = 'http://localhost:8000/api';

interface GraphPath {
  req: string;
  via: string;
  type: string;
  label: string;
  score: number;
}

interface KwJob {
  id: string; title: string; score: number; required_skills: string[];
  matched: string[]; missing: string[]; match_ratio: string; explanation: string;
}

interface GrJob {
  id: string; title: string; score: number; required_skills: string[];
  paths: GraphPath[]; direct_matches: string[]; graph_matches: string[];
  unmatched: string[]; explanation: string;
}

interface DemoResult {
  extracted_skills: string[];
  keyword_recommendations: KwJob[];
  graph_recommendations: GrJob[];
  total_jobs_scored: number;
  error?: string;
}

const LiveDemo = () => {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<DemoResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const [expandedKw, setExpandedKw] = useState<string | null>(null);
  const [expandedGr, setExpandedGr] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true); setError(null); setResult(null);
    const formData = new FormData();
    formData.append('file', file);
    try {
      const res = await axios.post(`${API_BASE}/test-resume`, formData);
      if (res.data.error) setError(res.data.error);
      else setResult(res.data);
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Failed to process resume.');
    } finally { setLoading(false); }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault(); setDragOver(false);
    if (e.dataTransfer.files[0]) setFile(e.dataTransfer.files[0]);
  };

  const reset = () => { setFile(null); setResult(null); setError(null); setExpandedKw(null); setExpandedGr(null); };

  // ── Upload Screen ──
  if (!result) return (
    <div>
      <div style={{ marginBottom: 40 }}>
        <h2 style={{ fontSize: 28, fontWeight: 800, letterSpacing: '-0.04em' }}>Resume Analyzer</h2>
        <p style={{ color: '#a1a1aa', fontSize: 14, marginTop: 6 }}>
          Upload a resume to compare keyword-based and graph-based job matching side-by-side
        </p>
      </div>
      <div className={`upload-zone ${dragOver ? 'drag-over' : ''} ${file ? 'has-file' : ''}`}
        onClick={() => inputRef.current?.click()}
        onDragOver={e => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)} onDrop={handleDrop}>
        <input ref={inputRef} type="file" accept=".pdf,.txt" hidden
          onChange={e => { if (e.target.files?.[0]) setFile(e.target.files[0]); }} />
        <div style={{ fontSize: 32, marginBottom: 16, opacity: 0.25 }}>{file ? '📄' : '↑'}</div>
        {file
          ? <><p style={{ fontSize: 15, fontWeight: 600 }}>{file.name}</p><p style={{ fontSize: 13, color: '#a1a1aa', marginTop: 4 }}>{(file.size / 1024).toFixed(1)} KB</p></>
          : <><p style={{ fontSize: 15, fontWeight: 500, color: '#71717a' }}>Drop your resume here, or click to browse</p><p style={{ fontSize: 12, color: '#a1a1aa', marginTop: 6 }}>PDF or TXT</p></>
        }
      </div>
      {error && <div style={{ marginTop: 16, padding: '12px 16px', background: '#fafafa', border: '1px solid #e4e4e7', borderRadius: 8, color: '#71717a', fontSize: 13 }}>{error}</div>}
      <div style={{ display: 'flex', gap: 10, marginTop: 24 }}>
        <button onClick={handleUpload} disabled={!file || loading}
          style={{ padding: '10px 28px', background: file && !loading ? '#18181b' : '#d4d4d8', color: '#fff', border: 'none', borderRadius: 8, fontSize: 14, fontWeight: 600, cursor: file ? 'pointer' : 'default', display: 'flex', alignItems: 'center', gap: 8 }}>
          {loading ? <><div style={{ width: 14, height: 14, border: '2px solid #fff4', borderTopColor: '#fff', borderRadius: '50%', animation: 'spin 0.8s linear infinite' }} />Analyzing...</> : 'Analyze'}
        </button>
        {file && !loading && <button onClick={reset} style={{ padding: '10px 20px', background: '#f4f4f5', color: '#71717a', border: '1px solid #e4e4e7', borderRadius: 8, fontSize: 13, fontWeight: 500, cursor: 'pointer' }}>Clear</button>}
      </div>
      {loading && <div style={{ marginTop: 40, textAlign: 'center' }}><div className="pulse-ring" style={{ fontSize: 13, color: '#a1a1aa' }}>Extracting skills with AI and querying the Neo4j graph...</div></div>}
    </div>
  );

  // ── Results Screen ──
  const kw = result.keyword_recommendations;
  const gr = result.graph_recommendations;

  return (
    <div>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 24 }}>
        <div>
          <h2 style={{ fontSize: 28, fontWeight: 800, letterSpacing: '-0.04em' }}>Analysis Results</h2>
          <p style={{ color: '#a1a1aa', fontSize: 13, marginTop: 4 }}>
            {result.extracted_skills.length} skills extracted · {result.total_jobs_scored} jobs scored
          </p>
        </div>
        <button onClick={reset} style={{ padding: '8px 20px', background: '#f4f4f5', color: '#71717a', border: '1px solid #e4e4e7', borderRadius: 8, fontSize: 13, fontWeight: 500, cursor: 'pointer' }}>← New Upload</button>
      </div>

      {/* Extracted Skills */}
      <div style={{ marginBottom: 28 }}>
        <p className="section-title">Your Skills</p>
        <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
          {result.extracted_skills.map(s => <span key={s} className="skill-pill">{s}</span>)}
        </div>
      </div>

      {/* ── Split Screen ── */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>

        {/* LEFT: Keyword */}
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 16 }}>
            <span className="badge badge-outline">Keyword Matching</span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {kw.slice(0, 5).map((job, i) => (
              <div key={job.id} className="card" style={{ padding: 0, overflow: 'hidden' }}>
                {/* Job header */}
                <div style={{ padding: '14px 16px', cursor: 'pointer' }}
                  onClick={() => setExpandedKw(expandedKw === job.id ? null : job.id)}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, flex: 1, minWidth: 0 }}>
                      <span style={{ fontSize: 11, fontWeight: 700, color: '#d4d4d8', fontFamily: 'monospace' }}>{i + 1}</span>
                      <span style={{ fontSize: 13, fontWeight: 600, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{job.title}</span>
                    </div>
                    <span style={{ fontSize: 14, fontWeight: 800, color: '#71717a', fontFamily: 'monospace', marginLeft: 12 }}>{Math.round(job.score * 100)}%</span>
                  </div>
                  {/* Match bar */}
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginTop: 10 }}>
                    <div style={{ flex: 1, height: 4, background: '#f4f4f5', borderRadius: 99, overflow: 'hidden' }}>
                      <div style={{ width: `${Math.round(job.score * 100)}%`, height: '100%', background: '#a1a1aa', borderRadius: 99, transition: 'width 0.5s' }} />
                    </div>
                    <span style={{ fontSize: 11, color: '#a1a1aa', fontWeight: 600, whiteSpace: 'nowrap' }}>{job.match_ratio}</span>
                  </div>
                </div>
                {/* Expanded explanation */}
                {expandedKw === job.id && (
                  <div style={{ padding: '0 16px 14px', borderTop: '1px solid #f4f4f5' }}>
                    <p style={{ fontSize: 12, color: '#71717a', marginTop: 12, marginBottom: 8, fontWeight: 600 }}>Why recommended</p>
                    <p style={{ fontSize: 12, color: '#a1a1aa', marginBottom: 10 }}>{job.explanation}</p>
                    {job.matched.length > 0 && (
                      <div style={{ marginBottom: 8 }}>
                        <p style={{ fontSize: 11, fontWeight: 600, color: '#71717a', marginBottom: 4 }}>Matched</p>
                        <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap' }}>
                          {job.matched.map(s => <span key={s} style={{ padding: '2px 8px', borderRadius: 4, fontSize: 11, fontWeight: 500, background: '#f0fdf4', color: '#16a34a', border: '1px solid #bbf7d0' }}>{s}</span>)}
                        </div>
                      </div>
                    )}
                    {job.missing.length > 0 && (
                      <div>
                        <p style={{ fontSize: 11, fontWeight: 600, color: '#71717a', marginBottom: 4 }}>Missing</p>
                        <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap' }}>
                          {job.missing.map(s => <span key={s} style={{ padding: '2px 8px', borderRadius: 4, fontSize: 11, fontWeight: 500, background: '#fef2f2', color: '#dc2626', border: '1px solid #fecaca' }}>{s}</span>)}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* RIGHT: Graph */}
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 16 }}>
            <span className="badge badge-dark">Graph Matching</span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {gr.slice(0, 5).map((job, i) => (
              <div key={job.id} className="card" style={{ padding: 0, overflow: 'hidden', borderColor: i === 0 ? '#18181b' : undefined }}>
                {/* Job header */}
                <div style={{ padding: '14px 16px', cursor: 'pointer' }}
                  onClick={() => setExpandedGr(expandedGr === job.id ? null : job.id)}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, flex: 1, minWidth: 0 }}>
                      <span style={{ fontSize: 11, fontWeight: 700, color: '#d4d4d8', fontFamily: 'monospace' }}>{i + 1}</span>
                      <span style={{ fontSize: 13, fontWeight: 600, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{job.title}</span>
                    </div>
                    <span style={{ fontSize: 14, fontWeight: 800, color: '#18181b', fontFamily: 'monospace', marginLeft: 12 }}>{Math.round(job.score * 100)}%</span>
                  </div>
                  {/* Score bar */}
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginTop: 10 }}>
                    <div style={{ flex: 1, height: 4, background: '#f4f4f5', borderRadius: 99, overflow: 'hidden' }}>
                      <div style={{ width: `${Math.round(job.score * 100)}%`, height: '100%', background: '#18181b', borderRadius: 99, transition: 'width 0.5s' }} />
                    </div>
                    <span style={{ fontSize: 11, color: '#71717a', fontWeight: 600, whiteSpace: 'nowrap' }}>
                      {job.direct_matches.length + job.graph_matches.length}/{job.direct_matches.length + job.graph_matches.length + job.unmatched.length}
                    </span>
                  </div>
                </div>
                {/* Expanded explanation */}
                {expandedGr === job.id && (
                  <div style={{ padding: '0 16px 14px', borderTop: '1px solid #f4f4f5' }}>
                    <p style={{ fontSize: 12, color: '#71717a', marginTop: 12, marginBottom: 8, fontWeight: 600 }}>Why recommended</p>
                    <p style={{ fontSize: 12, color: '#a1a1aa', marginBottom: 10 }}>{job.explanation}</p>
                    {/* Graph paths */}
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                      {job.paths.filter(p => p.type !== 'none').map((p, pi) => (
                        <div key={pi} style={{
                          padding: '6px 10px', borderRadius: 6, fontSize: 11, fontWeight: 500,
                          background: p.type === 'direct' ? '#f0fdf4' : p.type === 'none' ? '#fef2f2' : '#f4f4f5',
                          color: p.type === 'direct' ? '#16a34a' : p.type === 'none' ? '#dc2626' : '#18181b',
                          border: `1px solid ${p.type === 'direct' ? '#bbf7d0' : p.type === 'none' ? '#fecaca' : '#e4e4e7'}`,
                          fontFamily: 'monospace'
                        }}>
                          {p.label}
                        </div>
                      ))}
                      {job.unmatched.length > 0 && (
                        <div style={{ marginTop: 4 }}>
                          <p style={{ fontSize: 11, fontWeight: 600, color: '#a1a1aa', marginBottom: 4 }}>No connection found</p>
                          <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap' }}>
                            {job.unmatched.map(s => <span key={s} style={{ padding: '2px 8px', borderRadius: 4, fontSize: 11, background: '#fef2f2', color: '#dc2626', border: '1px solid #fecaca' }}>{s}</span>)}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Bottom insight */}
      <div style={{ marginTop: 28, padding: '14px 18px', background: '#fafafa', borderRadius: 8, border: '1px solid #e4e4e7' }}>
        <p style={{ fontSize: 13, color: '#71717a', lineHeight: 1.7 }}>
          Click any job card to expand the <strong style={{ color: '#18181b' }}>explanation panel</strong>. Keyword shows matched vs missing skills.
          Graph shows the <strong style={{ color: '#18181b' }}>semantic paths</strong> (SUBSET_OF, RELATED_TO) that connected your skills to job requirements.
        </p>
      </div>
    </div>
  );
};

export default LiveDemo;
