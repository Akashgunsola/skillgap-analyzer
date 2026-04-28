import { useState, useEffect, ReactNode } from 'react';
import axios from 'axios';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  Cell
} from 'recharts';
import { motion, AnimatePresence } from 'framer-motion';
import ForceGraph2D from 'react-force-graph-2d';
import LiveDemo from './LiveDemo';
import Metrics from './Metrics';

const API_BASE = 'http://localhost:8000/api';

// ──────────────────────────────
// Types
// ──────────────────────────────
interface JobScore {
  id: string;
  title: string;
  score: number;
}

interface CandidateResult {
  candidate: string;
  skills: string[];
  relevant_jobs: string[];
  keyword_top: JobScore[];
  graph_top: JobScore[];
  keyword_precision: number;
  graph_precision: number;
}

interface ResultsData {
  k: number;
  avg_keyword_precision: number;
  avg_graph_precision: number;
  details: CandidateResult[];
}

interface GraphNode {
  id: string;
  label: string;
  type: string;
  x?: number;
  y?: number;
}

interface GraphLink {
  source: string;
  target: string;
  type: string;
}

interface GraphData {
  nodes: GraphNode[];
  links: GraphLink[];
}

// ──────────────────────────────
// Main App
// ──────────────────────────────
const App = () => {
  const [graphData, setGraphData] = useState<GraphData | null>(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('demo');

  // Only fetch graph data when the Skill Graph tab is opened
  useEffect(() => {
    if (activeTab === 'graph' && !graphData) {
      setLoading(true);
      axios.get(`${API_BASE}/graph`)
        .then(res => setGraphData(res.data))
        .catch(err => console.error('Graph fetch failed:', err))
        .finally(() => setLoading(false));
    }
  }, [activeTab, graphData]);

  const tabs = [
    { key: 'demo', label: 'Live Demo' },
    { key: 'metrics', label: 'Metrics' },
    { key: 'graph', label: 'Skill Graph' },
  ];

  return (
    <div style={{ minHeight: '100vh', background: '#fff' }}>
      {/* Header */}
      <header style={{ borderBottom: '1px solid #e4e4e7', background: '#fff', position: 'sticky', top: 0, zIndex: 50 }}>
        <div style={{ maxWidth: 1060, margin: '0 auto', padding: '0 24px', height: 56, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <div style={{ width: 28, height: 28, background: '#18181b', borderRadius: 6, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="5" r="3"/><circle cx="5" cy="19" r="3"/><circle cx="19" cy="19" r="3"/>
                <line x1="12" y1="8" x2="5" y2="16"/><line x1="12" y1="8" x2="19" y2="16"/>
              </svg>
            </div>
            <h1 style={{ fontSize: 15, fontWeight: 800, letterSpacing: '-0.02em', color: '#18181b' }}>SkillGraph</h1>
          </div>

          <nav style={{ display: 'flex', gap: 2 }}>
            {tabs.map(tab => (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key)}
                style={{
                  padding: '6px 16px',
                  borderRadius: 6,
                  fontSize: 13,
                  fontWeight: 500,
                  border: 'none',
                  cursor: 'pointer',
                  transition: 'all 0.15s',
                  background: activeTab === tab.key ? '#f4f4f5' : 'transparent',
                  color: activeTab === tab.key ? '#18181b' : '#a1a1aa',
                }}
              >
                {tab.label}
              </button>
            ))}
          </nav>
        </div>
      </header>

      {/* Content */}
      <main style={{ maxWidth: 1120, margin: '0 auto', padding: '32px 24px 64px' }}>
        <AnimatePresence mode="wait">
          {activeTab === 'demo' && <motion.div key="demo" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -12 }} transition={{ duration: 0.2 }}><LiveDemo /></motion.div>}
          {activeTab === 'metrics' && <motion.div key="metrics" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -12 }} transition={{ duration: 0.2 }}><Metrics /></motion.div>}
          {activeTab === 'graph' && (loading ? (
            <div style={{ textAlign: 'center', padding: '80px 0', color: '#a1a1aa', fontSize: 13 }}>
              <div style={{ width: 20, height: 20, border: '2px solid #e4e4e7', borderTopColor: '#18181b', borderRadius: '50%', animation: 'spin 0.8s linear infinite', margin: '0 auto 12px' }} />
              Loading skill graph...
            </div>
          ) : graphData ? <GraphView key="graph" data={graphData} /> : (
            <div style={{ textAlign: 'center', padding: '80px 0', color: '#a1a1aa', fontSize: 13 }}>Failed to load graph data</div>
          ))}
        </AnimatePresence>
      </main>
    </div>
  );
};

// ──────────────────────────────
// Page Wrapper
// ──────────────────────────────
const Page = ({ children }: { children: ReactNode }) => (
  <motion.div
    initial={{ opacity: 0, y: 12 }}
    animate={{ opacity: 1, y: 0 }}
    exit={{ opacity: 0, y: -12 }}
    transition={{ duration: 0.2 }}
  >
    {children}
  </motion.div>
);

// ──────────────────────────────
// Summary View
// ──────────────────────────────
const SummaryView = ({ data }: { data: ResultsData }) => {
  const kwPct = (data.avg_keyword_precision * 100).toFixed(1);
  const grPct = (data.avg_graph_precision * 100).toFixed(1);
  const diff = ((data.avg_graph_precision - data.avg_keyword_precision) * 100).toFixed(1);

  const chartData = [
    { name: 'Keyword', precision: parseFloat(kwPct), fill: '#a1a1aa' },
    { name: 'Graph-Based', precision: parseFloat(grPct), fill: '#18181b' },
  ];

  return (
    <Page>
      {/* Page Title */}
      <div style={{ marginBottom: 32 }}>
        <h2 style={{ fontSize: 24, fontWeight: 800, letterSpacing: '-0.03em' }}>Evaluation Overview</h2>
        <p style={{ color: '#a1a1aa', fontSize: 14, marginTop: 4 }}>
          Comparative results for Precision@{data.k} across {data.details.length} candidate profiles
        </p>
      </div>

      {/* Stat Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 16, marginBottom: 32 }}>
        <StatCard label="Baseline (Keyword)" value={`${kwPct}%`} badge="P@2" badgeColor="subtle" />
        <StatCard label="Proposed (Graph)" value={`${grPct}%`} badge="P@2" badgeColor="dark" accent />
        <StatCard label="Improvement" value={`+${diff}%`} badge="Δ" badgeColor="subtle" />
        <StatCard label="Test Candidates" value={String(data.details.length)} badge="N" badgeColor="subtle" />
      </div>

      {/* Chart + Insight */}
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 24 }}>
        <div className="card">
          <p className="section-title">Precision@{data.k} Comparison</p>
          <div style={{ height: 280 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 8, right: 8, left: -16, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f3f4f6" />
                <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fill: '#6b7280', fontSize: 12, fontWeight: 600 }} />
                <YAxis unit="%" axisLine={false} tickLine={false} tick={{ fill: '#9ca3af', fontSize: 12 }} domain={[0, 100]} />
                <Tooltip
                  cursor={{ fill: 'rgba(0,0,0,0.02)' }}
                  contentStyle={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: 8, fontSize: 13 }}
                />
                <Bar dataKey="precision" radius={[6, 6, 0, 0]} barSize={56}>
                  {chartData.map((entry, i) => (
                    <Cell key={i} fill={entry.fill} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div>
            <p className="section-title">Key Finding</p>
            <p style={{ fontSize: 14, color: '#374151', lineHeight: 1.7 }}>
              The <strong>graph-based approach</strong> successfully captures semantic skill relationships,
              outperforming keyword matching by <strong>{diff} percentage points</strong>.
            </p>
            <p style={{ fontSize: 14, color: '#6b7280', marginTop: 12, lineHeight: 1.7 }}>
              By traversing <em>SUBSET_OF</em> and <em>RELATED_TO</em> edges in Neo4j, the system
              identifies indirect matches that direct keyword comparison misses entirely.
            </p>
          </div>
          <div style={{ marginTop: 20, padding: '12px 16px', background: '#f8f9fa', borderRadius: 8, border: '1px solid #e4e4e7' }}>
            <p style={{ fontSize: 12, color: '#71717a', fontWeight: 500 }}>
              ✓ Graph matching reduced false negatives by treating specialized skills as valid subsets of general requirements.
            </p>
          </div>
        </div>
      </div>
    </Page>
  );
};

// ──────────────────────────────
// Stat Card
// ──────────────────────────────
const StatCard = ({ label, value, badge, badgeColor = 'gray', accent = false }: {
  label: string; value: string; badge: string; badgeColor?: string; accent?: boolean;
}) => (
  <div className="card" style={{ border: accent ? '1.5px solid #18181b' : undefined }}>
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
      <span style={{ fontSize: 13, color: '#6b7280', fontWeight: 500 }}>{label}</span>
      <span className={`badge badge-${badgeColor}`}>{badge}</span>
    </div>
    <p className="stat-value">{value}</p>
  </div>
);

// ──────────────────────────────
// Analysis View
// ──────────────────────────────
const AnalysisView = ({ data }: { data: ResultsData }) => {
  return (
    <Page>
      <div style={{ marginBottom: 32 }}>
        <h2 style={{ fontSize: 24, fontWeight: 800, letterSpacing: '-0.03em' }}>Candidate Analysis</h2>
        <p style={{ color: '#6b7280', fontSize: 14, marginTop: 4 }}>
          Per-candidate breakdown comparing top-{data.k} recommendations from each method
        </p>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
        {data.details.map((item, idx) => (
          <div key={idx} className="card-flush">
            {/* Header */}
            <div style={{ padding: '20px 24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #f3f4f6' }}>
              <div>
                <h3 style={{ fontSize: 16, fontWeight: 700 }}>{item.candidate}</h3>
                <div style={{ display: 'flex', gap: 6, marginTop: 8, flexWrap: 'wrap' }}>
                  {item.skills.map((s: string) => (
                    <span key={s} className="badge badge-gray">{s}</span>
                  ))}
                </div>
              </div>
              <div style={{ display: 'flex', gap: 24, textAlign: 'center' }}>
                <div>
                  <p style={{ fontSize: 11, color: '#9ca3af', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Keyword</p>
                  <p style={{ fontSize: 22, fontWeight: 800, color: item.keyword_precision > 0 ? '#71717a' : '#d4d4d8', marginTop: 2 }}>
                    {item.keyword_precision.toFixed(2)}
                  </p>
                </div>
                <div>
                  <p style={{ fontSize: 11, color: '#9ca3af', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Graph</p>
                  <p style={{ fontSize: 22, fontWeight: 800, color: item.graph_precision > 0 ? '#18181b' : '#d4d4d8', marginTop: 2 }}>
                    {item.graph_precision.toFixed(2)}
                  </p>
                </div>
              </div>
            </div>

            {/* Recommendations */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr' }}>
              {/* Keyword */}
              <div style={{ padding: '16px 24px', borderRight: '1px solid #f3f4f6' }}>
                <p style={{ fontSize: 11, fontWeight: 700, color: '#9ca3af', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 10 }}>
                  Keyword Recommendations
                </p>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                  {item.keyword_top.map((job: JobScore) => (
                    <div key={job.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '8px 12px', background: '#f9fafb', borderRadius: 8 }}>
                      <span style={{ fontSize: 13, fontWeight: 500 }}>{job.title}</span>
                      <span style={{ fontSize: 12, fontWeight: 700, color: '#9ca3af', fontFamily: 'monospace' }}>{(job.score * 100).toFixed(0)}%</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Graph */}
              <div style={{ padding: '16px 24px' }}>
                <p style={{ fontSize: 11, fontWeight: 700, color: '#9ca3af', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 10 }}>
                  Graph Recommendations
                </p>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                  {item.graph_top.map((job: JobScore) => {
                    const isRelevant = item.relevant_jobs.includes(job.id);
                    return (
                      <div key={job.id} style={{
                        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                        padding: '8px 12px', borderRadius: 8,
                        background: isRelevant ? '#f4f4f5' : '#f9fafb',
                        border: isRelevant ? '1px solid #d4d4d8' : '1px solid transparent',
                      }}>
                        <span style={{ fontSize: 13, fontWeight: 500, display: 'flex', alignItems: 'center', gap: 6 }}>
                          {job.title}
                          {isRelevant && <span style={{ color: '#18181b', fontSize: 14 }}>✓</span>}
                        </span>
                        <span style={{ fontSize: 12, fontWeight: 700, color: '#18181b', fontFamily: 'monospace' }}>{(job.score * 100).toFixed(0)}%</span>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </Page>
  );
};

// ──────────────────────────────
// Graph View
// ──────────────────────────────
const GraphView = ({ data }: { data: GraphData }) => {
  return (
    <Page>
      <div style={{ marginBottom: 24 }}>
        <h2 style={{ fontSize: 24, fontWeight: 800, letterSpacing: '-0.03em' }}>Skill Ontology Graph</h2>
        <p style={{ color: '#6b7280', fontSize: 14, marginTop: 4 }}>
          Interactive visualization of <em>SUBSET_OF</em> and <em>RELATED_TO</em> skill relationships stored in Neo4j
        </p>
      </div>

      {/* Legend */}
      <div style={{ display: 'flex', gap: 24, marginBottom: 16 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <div style={{ width: 24, height: 2, background: '#18181b', borderRadius: 2 }} />
          <span style={{ fontSize: 12, color: '#71717a', fontWeight: 500 }}>SUBSET_OF</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <div style={{ width: 24, height: 2, background: '#d4d4d8', borderRadius: 2 }} />
          <span style={{ fontSize: 12, color: '#71717a', fontWeight: 500 }}>RELATED_TO</span>
        </div>
      </div>

      <div className="card-flush" style={{ minHeight: 560 }}>
        <ForceGraph2D
          graphData={{
            nodes: data.nodes,
            links: data.links.map(l => ({ ...l, source: l.source, target: l.target }))
          }}
          nodeLabel="id"
          nodeColor={() => '#18181b'}
          linkColor={(link: GraphLink) => link.type === 'SUBSET_OF' ? 'rgba(24, 24, 27, 0.4)' : 'rgba(161, 161, 170, 0.4)'}
          linkDirectionalArrowLength={3.5}
          linkDirectionalArrowRelPos={1}
          nodeCanvasObject={(node: GraphNode, ctx: CanvasRenderingContext2D, globalScale: number) => {
            const label = node.id || '';
            const fontSize = 11 / globalScale;
            ctx.font = `600 ${fontSize}px Inter, system-ui, sans-serif`;
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';

            // Node circle
            ctx.beginPath();
            ctx.arc(node.x || 0, node.y || 0, 5, 0, 2 * Math.PI, false);
            ctx.fillStyle = '#18181b';
            ctx.fill();
            ctx.strokeStyle = '#fff';
            ctx.lineWidth = 1.5 / globalScale;
            ctx.stroke();

            // Label
            ctx.fillStyle = '#71717a';
            ctx.fillText(label, node.x || 0, (node.y || 0) + 10 / globalScale);
          }}
          backgroundColor="#ffffff"
          height={560}
          width={Math.min(1072, window.innerWidth - 48)}
        />
      </div>
    </Page>
  );
};

export default App;
