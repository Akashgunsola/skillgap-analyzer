import { useState, useRef, useCallback } from 'react';
import axios from 'axios';
import ForceGraph2D from 'react-force-graph-2d';
import type { DemoResult, GrJob } from './App';

const API_BASE = 'http://localhost:8000/api';

interface TraversalNode { id: string; label: string; type: string; x?: number; y?: number; }
interface TraversalEdge { source: string; target: string; type: string; similarity?: number; }
interface TraversalGraph { nodes: TraversalNode[]; edges: TraversalEdge[]; }

const LiveDemo = ({ onResultReady }: { onResultReady: (r: DemoResult) => void }) => {
  const [file, setFile] = useState<File | null>(null);
  const [extractor, setExtractor] = useState<string>('gemini');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<DemoResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const [expandedJob, setExpandedJob] = useState<string | null>(null);
  const [traversalData, setTraversalData] = useState<Record<string, TraversalGraph>>({});
  const [traversalLoading, setTraversalLoading] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true); setError(null); setResult(null);
    const formData = new FormData();
    formData.append('file', file);
    formData.append('extractor', extractor);
    try {
      const res = await axios.post(`${API_BASE}/test-resume`, formData);
      if (res.data.error) setError(res.data.error);
      else { setResult(res.data); onResultReady(res.data); }
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Failed to process resume.');
    } finally { setLoading(false); }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault(); setDragOver(false);
    if (e.dataTransfer.files[0]) setFile(e.dataTransfer.files[0]);
  };

  const reset = () => { setFile(null); setResult(null); setError(null); setExpandedJob(null); setTraversalData({}); };

  const loadTraversal = async (job: GrJob) => {
    if (traversalData[job.id]) return;
    if (!result) return;
    setTraversalLoading(job.id);
    try {
      const res = await axios.post(`${API_BASE}/traversal-graph`, {
        candidate_skills: result.extracted_skills,
        required_skills: job.required_skills,
        paths: job.paths,
      });
      setTraversalData(prev => ({ ...prev, [job.id]: res.data }));
    } catch { /* silently fail */ }
    finally { setTraversalLoading(null); }
  };

  const toggleJob = (job: GrJob) => {
    if (expandedJob === job.id) { setExpandedJob(null); return; }
    setExpandedJob(job.id);
    loadTraversal(job);
  };

  // ── Upload Screen ──
  if (!result) return (
    <div>
      <div style={{ marginBottom: 48 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8 }}>
          <span className="badge badge-cyan">Graph-Powered</span>
          <span className="badge badge-purple">AI-Driven</span>
        </div>
        <h2 style={{ fontSize: 36, fontWeight: 800, letterSpacing: '-0.04em', lineHeight: 1.2 }}>
          <span className="gradient-text">Intelligent</span> Job Recommendations
        </h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: 15, marginTop: 12, maxWidth: 560, lineHeight: 1.7 }}>
          Upload your resume and our AI extracts your skills, then traverses the Neo4j skill ontology graph
          to find semantically connected job recommendations.
        </p>
      </div>

      <div className={`upload-zone ${dragOver ? 'drag-over' : ''} ${file ? 'has-file' : ''}`}
        onClick={() => inputRef.current?.click()}
        onDragOver={e => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)} onDrop={handleDrop}>
        <input ref={inputRef} type="file" accept=".pdf,.txt" hidden
          onChange={e => { if (e.target.files?.[0]) setFile(e.target.files[0]); }} />
        <div style={{ position: 'relative', zIndex: 2 }}>
          <div style={{ fontSize: 40, marginBottom: 16, opacity: 0.4 }}>{file ? '📄' : '⬡'}</div>
          {file ? (
            <>
              <p style={{ fontSize: 16, fontWeight: 600, color: 'var(--text-primary)' }}>{file.name}</p>
              <p style={{ fontSize: 13, color: 'var(--text-muted)', marginTop: 4 }}>{(file.size / 1024).toFixed(1)} KB · Ready to analyze</p>
            </>
          ) : (
            <>
              <p style={{ fontSize: 15, fontWeight: 500, color: 'var(--text-secondary)' }}>Drop your resume here, or click to browse</p>
              <p style={{ fontSize: 12, color: 'var(--text-dim)', marginTop: 8 }}>Supports PDF and TXT formats</p>
            </>
          )}
        </div>
      </div>

      {error && (
        <div style={{ marginTop: 16, padding: '14px 18px', background: 'var(--accent-rose-soft)', border: '1px solid rgba(244,63,94,0.15)', borderRadius: 10, color: 'var(--accent-rose)', fontSize: 13 }}>
          {error}
        </div>
      )}

      <div style={{ display: 'flex', gap: 10, marginTop: 28, alignItems: 'center' }}>
        <select 
          value={extractor} 
          onChange={(e) => setExtractor(e.target.value)}
          style={{
            padding: '12px 16px',
            borderRadius: '8px',
            background: 'rgba(255, 255, 255, 0.05)',
            border: '1px solid var(--border-default)',
            color: 'var(--text-primary)',
            fontSize: '14px',
            outline: 'none',
            cursor: 'pointer'
          }}
        >
          <option value="gemini">Gemini (AI Extractor)</option>
          <option value="spacy">SpaCy (Rule-based Extractor)</option>
        </select>
        <button onClick={handleUpload} disabled={!file || loading} className="btn-primary">
          {loading ? <><div className="spinner-sm" /> Analyzing...</> : '⬡ Analyze with Graph AI'}
        </button>
        {file && !loading && <button onClick={reset} className="btn-ghost">Clear</button>}
      </div>

      {loading && (
        <div style={{ marginTop: 48, textAlign: 'center' }}>
          <div className="spinner" style={{ margin: '0 auto 16px' }} />
          <p className="pulse-ring" style={{ fontSize: 13, color: 'var(--text-muted)' }}>
            Extracting skills with AI and traversing the Neo4j graph...
          </p>
        </div>
      )}
    </div>
  );

  // ── Results Screen ──
  const gr = result.graph_recommendations;

  return (
    <div>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 32 }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 10 }}>
            <span className="badge badge-filled">Graph Traversal</span>
            <span className="badge badge-ghost">{result.total_jobs_scored} jobs analyzed</span>
          </div>
          <h2 style={{ fontSize: 32, fontWeight: 800, letterSpacing: '-0.04em' }}>
            Your <span className="gradient-text">Recommendations</span>
          </h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: 14, marginTop: 6 }}>
            {result.extracted_skills.length} skills extracted · Ranked by graph-based semantic matching
          </p>
        </div>
        <button onClick={reset} className="btn-ghost">← New Analysis</button>
      </div>

      {/* Extracted Skills */}
      <div style={{ marginBottom: 36 }}>
        <p className="section-title">Your Extracted Skills</p>
        <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
          {result.extracted_skills.map(s => <span key={s} className="skill-pill">{s}</span>)}
        </div>
      </div>

      {/* Graph Recommendations */}
      <div style={{ marginBottom: 16 }}>
        <p className="section-title">Recommended Jobs via Graph Traversal</p>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
        {gr.slice(0, 8).map((job, i) => (
          <JobCard key={job.id} job={job} rank={i + 1}
            expanded={expandedJob === job.id}
            onToggle={() => toggleJob(job)}
            traversal={traversalData[job.id]}
            traversalLoading={traversalLoading === job.id}
            candidateSkills={result.extracted_skills}
          />
        ))}
      </div>

      {/* Bottom insight */}
      <div style={{ marginTop: 32, padding: '18px 22px', background: 'var(--bg-card)', borderRadius: 12, border: '1px solid var(--border-default)' }}>
        <p style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.8 }}>
          💡 Click any job card to see the <strong style={{ color: 'var(--accent-cyan)' }}>interactive graph traversal</strong> showing
          exactly how your skills connect to job requirements through <strong style={{ color: 'var(--accent-cyan)' }}>SUBSET_OF</strong> and{' '}
          <strong style={{ color: 'var(--accent-amber)' }}>RELATED_TO</strong> relationships in Neo4j.
        </p>
      </div>
    </div>
  );
};

// ──────────────────────────────
// Job Card Component
// ──────────────────────────────
const JobCard = ({ job, rank, expanded, onToggle, traversal, traversalLoading, candidateSkills }: {
  job: GrJob; rank: number; expanded: boolean; onToggle: () => void;
  traversal?: TraversalGraph; traversalLoading: boolean; candidateSkills: string[];
}) => {
  const directCount = job.direct_matches?.length || 0;
  const graphCount = job.graph_matches?.length || 0;
  const unmatchedCount = job.unmatched?.length || 0;
  const totalReq = directCount + graphCount + unmatchedCount;
  const scorePct = Math.round(job.score * 100);

  return (
    <div className={`job-card ${expanded ? 'expanded' : ''} ${rank === 1 ? 'top-pick' : ''}`}>
      {/* Main row */}
      <div style={{ padding: '18px 22px', cursor: 'pointer' }} onClick={onToggle}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 14, flex: 1, minWidth: 0 }}>
            {/* Rank */}
            <div style={{
              width: 32, height: 32, borderRadius: 8,
              background: rank === 1 ? 'var(--gradient-primary)' : 'rgba(255,255,255,0.04)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: 13, fontWeight: 700, color: rank === 1 ? '#000' : 'var(--text-muted)',
              fontFamily: 'var(--font-mono)', flexShrink: 0,
            }}>
              {rank}
            </div>
            <div style={{ minWidth: 0 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <span style={{ fontSize: 15, fontWeight: 600, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', color: 'var(--text-primary)' }}>
                  {job.title}
                </span>
                {rank === 1 && <span className="badge badge-cyan" style={{ fontSize: 10 }}>Best Match</span>}
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginTop: 6 }}>
                <span style={{ fontSize: 11, color: 'var(--accent-green)', fontWeight: 600 }}>
                  {directCount} direct
                </span>
                <span style={{ fontSize: 11, color: 'var(--accent-cyan)', fontWeight: 600 }}>
                  {graphCount} graph
                </span>
                {unmatchedCount > 0 && (
                  <span style={{ fontSize: 11, color: 'var(--accent-rose)', fontWeight: 600 }}>
                    {unmatchedCount} unmatched
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* Score */}
          <div style={{ textAlign: 'right', flexShrink: 0, marginLeft: 16 }}>
            <span style={{
              fontSize: 24, fontWeight: 800, fontFamily: 'var(--font-mono)',
              background: 'var(--gradient-primary)', WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }}>
              {scorePct}%
            </span>
            <div style={{ fontSize: 10, color: 'var(--text-dim)', fontWeight: 600, marginTop: 2 }}>
              {directCount + graphCount}/{totalReq} skills
            </div>
          </div>
        </div>

        {/* Progress bar */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginTop: 12 }}>
          <div className="score-bar-bg" style={{ height: 5 }}>
            <div className="score-bar-fill" style={{ width: `${scorePct}%` }} />
          </div>
        </div>
      </div>

      {/* Expanded Details */}
      {expanded && (
        <div style={{ borderTop: '1px solid var(--border-subtle)', padding: '20px 22px' }}>
          {/* Why recommended */}
          <div style={{ marginBottom: 20 }}>
            <p style={{ fontSize: 12, color: 'var(--accent-cyan)', fontWeight: 700, marginBottom: 8, textTransform: 'uppercase', letterSpacing: '0.1em' }}>
              Why This Was Recommended
            </p>
            <p style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.7, marginBottom: 14 }}>
              {job.explanation}
            </p>
            {/* Path tags */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
              {job.paths?.map((p, pi) => (
                <div key={pi} className={`path-tag ${p.type}`}>
                  {p.type === 'direct' && '✓ '}
                  {p.type === 'subset_of' && '↳ '}
                  {p.type === 'parent_of' && '↰ '}
                  {p.type === 'related_to' && '↔ '}
                  {p.type === 'none' && '✗ '}
                  {p.label}
                </div>
              ))}
            </div>
          </div>

          {/* Interactive Graph Traversal */}
          <div style={{ marginTop: 24 }}>
            <p style={{ fontSize: 12, color: 'var(--accent-purple)', fontWeight: 700, marginBottom: 12, textTransform: 'uppercase', letterSpacing: '0.1em' }}>
              Interactive Graph Traversal
            </p>
            {traversalLoading ? (
              <div style={{ textAlign: 'center', padding: '40px 0' }}>
                <div className="spinner" style={{ margin: '0 auto 12px' }} />
                <p style={{ fontSize: 12, color: 'var(--text-muted)' }}>Loading graph traversal...</p>
              </div>
            ) : traversal ? (
              <TraversalViz data={traversal} candidateSkills={candidateSkills} requiredSkills={job.required_skills} />
            ) : (
              <div style={{ textAlign: 'center', padding: '40px 0', color: 'var(--text-dim)', fontSize: 12 }}>
                Could not load graph data
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

// ──────────────────────────────
// Traversal Visualization
// ──────────────────────────────
const TraversalViz = ({ data, candidateSkills, requiredSkills }: {
  data: TraversalGraph; candidateSkills: string[]; requiredSkills: string[];
}) => {
  const candSet = new Set(candidateSkills.map(s => s.toLowerCase()));
  const reqSet = new Set(requiredSkills.map(s => s.toLowerCase()));

  const getNodeColor = useCallback((node: TraversalNode) => {
    const id = node.id.toLowerCase();
    if (candSet.has(id) && reqSet.has(id)) return '#22c55e';  // Both = green
    if (candSet.has(id)) return '#00d4ff';   // Candidate = cyan
    if (reqSet.has(id)) return '#a855f7';     // Required = purple
    return '#5c5c78';                          // Intermediate = gray
  }, [candSet, reqSet]);

  const graphNodes = data.nodes.map(n => ({ ...n, id: n.id }));
  const graphEdges = data.edges.map(e => ({
    source: e.source, target: e.target, type: e.type, similarity: e.similarity,
  }));

  if (graphNodes.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: '30px 0', color: 'var(--text-dim)', fontSize: 12 }}>
        No graph connections found for this job
      </div>
    );
  }

  return (
    <div>
      {/* Legend */}
      <div className="graph-legend" style={{ marginBottom: 14 }}>
        <div className="legend-item"><div className="legend-dot" style={{ background: '#00d4ff' }} /><span>Your Skills</span></div>
        <div className="legend-item"><div className="legend-dot" style={{ background: '#a855f7' }} /><span>Required Skills</span></div>
        <div className="legend-item"><div className="legend-dot" style={{ background: '#22c55e' }} /><span>Direct Match</span></div>
        <div className="legend-item"><div className="legend-line" style={{ background: 'var(--accent-cyan)' }} /><span>SUBSET_OF</span></div>
        <div className="legend-item"><div className="legend-line" style={{ background: 'var(--accent-amber)', opacity: 0.6 }} /><span>RELATED_TO</span></div>
      </div>

      <div className="graph-viz-container" style={{ height: 360 }}>
        <ForceGraph2D
          graphData={{ nodes: graphNodes, links: graphEdges }}
          nodeLabel={(node: TraversalNode) => {
            const id = node.id.toLowerCase();
            const isCand = candSet.has(id);
            const isReq = reqSet.has(id);
            if (isCand && isReq) return `${node.id} (Direct Match)`;
            if (isCand) return `${node.id} (Your Skill)`;
            if (isReq) return `${node.id} (Required)`;
            return `${node.id} (Intermediate)`;
          }}
          nodeColor={(node: TraversalNode) => getNodeColor(node)}
          linkColor={(link: any) =>
            link.type === 'SUBSET_OF' ? 'rgba(0, 212, 255, 0.4)' : 'rgba(245, 158, 11, 0.35)'
          }
          linkWidth={(link: any) => link.type === 'SUBSET_OF' ? 2 : 1.5}
          linkDirectionalArrowLength={4}
          linkDirectionalArrowRelPos={1}
          linkLabel={(link: any) => {
            if (link.type === 'RELATED_TO' && link.similarity != null)
              return `${link.type} (${Math.round(link.similarity * 100)}%)`;
            return link.type;
          }}
          nodeCanvasObject={(node: TraversalNode, ctx: CanvasRenderingContext2D, globalScale: number) => {
            const color = getNodeColor(node);
            const fontSize = 10 / globalScale;
            const x = node.x || 0;
            const y = node.y || 0;

            // Glow ring
            ctx.beginPath();
            ctx.arc(x, y, 10, 0, 2 * Math.PI);
            ctx.fillStyle = color + '15';
            ctx.fill();

            // Node circle
            ctx.beginPath();
            ctx.arc(x, y, 5, 0, 2 * Math.PI);
            ctx.fillStyle = color;
            ctx.fill();
            ctx.strokeStyle = color + '40';
            ctx.lineWidth = 1.5 / globalScale;
            ctx.stroke();

            // Label
            ctx.font = `600 ${fontSize}px Inter, system-ui, sans-serif`;
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillStyle = 'rgba(240, 240, 245, 0.85)';
            ctx.fillText(node.id, x, y + 14 / globalScale);
          }}
          backgroundColor="#0a0a0f"
          height={360}
          width={Math.min(1072, window.innerWidth - 112)}
          d3VelocityDecay={0.3}
          cooldownTicks={80}
        />
      </div>
    </div>
  );
};

export default LiveDemo;
