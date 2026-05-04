import { useState, useEffect } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import ForceGraph2D from 'react-force-graph-2d';
import LiveDemo from './LiveDemo';
import Research from './Research';

const API_BASE = 'http://localhost:8000/api';

// ──────────────────────────────
// Types
// ──────────────────────────────
interface GraphNode {
  id: string; label: string; type: string; x?: number; y?: number;
}
interface GraphLink {
  source: string; target: string; type: string;
}
interface GraphData {
  nodes: GraphNode[]; links: GraphLink[];
}

// Shared result types
export interface GraphPath {
  req: string; via: string; type: string; label: string; score: number;
}
export interface KwJob {
  id: string; title: string; score: number; required_skills: string[];
  matched: string[]; missing: string[]; match_ratio: string; explanation: string;
}
export interface GrJob {
  id: string; title: string; score: number; required_skills: string[];
  paths: GraphPath[]; direct_matches: string[]; graph_matches: string[];
  unmatched: string[]; explanation: string;
}
export interface DemoResult {
  extracted_skills: string[];
  keyword_recommendations: KwJob[];
  graph_recommendations: GrJob[];
  total_jobs_scored: number;
  error?: string;
}

// ──────────────────────────────
// Main App
// ──────────────────────────────
const App = () => {
  const [graphData, setGraphData] = useState<GraphData | null>(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('demo');
  // Lifted state: current resume analysis result (shared between Section 1 & 2)
  const [currentResult, setCurrentResult] = useState<DemoResult | null>(null);

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
    { key: 'demo', label: 'Recommendations', icon: '⬡' },
    { key: 'research', label: 'Research', icon: '◈' },
    { key: 'graph', label: 'Ontology', icon: '◎' },
  ];

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-primary)' }}>
      {/* Background gradient orbs */}
      <div style={{ position: 'fixed', inset: 0, overflow: 'hidden', pointerEvents: 'none', zIndex: 0 }}>
        <div style={{
          position: 'absolute', top: '-20%', left: '-10%', width: 600, height: 600,
          borderRadius: '50%', background: 'radial-gradient(circle, rgba(0, 212, 255, 0.04) 0%, transparent 70%)',
          filter: 'blur(80px)',
        }} />
        <div style={{
          position: 'absolute', bottom: '-20%', right: '-10%', width: 500, height: 500,
          borderRadius: '50%', background: 'radial-gradient(circle, rgba(168, 85, 247, 0.04) 0%, transparent 70%)',
          filter: 'blur(80px)',
        }} />
      </div>

      {/* Header */}
      <header style={{
        borderBottom: '1px solid var(--border-subtle)', background: 'rgba(10, 10, 15, 0.85)',
        backdropFilter: 'blur(20px)', position: 'sticky', top: 0, zIndex: 50,
      }}>
        <div style={{
          maxWidth: 1200, margin: '0 auto', padding: '0 32px',
          height: 64, display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
            <div style={{
              width: 36, height: 36, background: 'var(--gradient-primary)', borderRadius: 10,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              boxShadow: '0 0 20px rgba(0, 212, 255, 0.2)',
            }}>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#000" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="5" r="3"/><circle cx="5" cy="19" r="3"/><circle cx="19" cy="19" r="3"/>
                <line x1="12" y1="8" x2="5" y2="16"/><line x1="12" y1="8" x2="19" y2="16"/>
              </svg>
            </div>
            <div>
              <h1 style={{ fontSize: 16, fontWeight: 800, letterSpacing: '-0.03em', lineHeight: 1.2, color: 'var(--text-primary)' }}>
                GraphRec
              </h1>
              <p style={{ fontSize: 10, fontWeight: 500, letterSpacing: '0.08em', color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                Graph Traversal & AI
              </p>
            </div>
          </div>
          <nav className="tab-nav">
            {tabs.map(tab => (
              <button key={tab.key} onClick={() => setActiveTab(tab.key)}
                className={`tab-btn ${activeTab === tab.key ? 'active' : ''}`}>
                <span style={{ marginRight: 6, fontSize: 11 }}>{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </nav>
        </div>
      </header>

      {/* Content */}
      <main style={{ maxWidth: 1200, margin: '0 auto', padding: '36px 32px 80px', position: 'relative', zIndex: 1 }}>
        <AnimatePresence mode="wait">
          {activeTab === 'demo' && (
            <motion.div key="demo" initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -16 }} transition={{ duration: 0.25 }}>
              <LiveDemo onResultReady={setCurrentResult} />
            </motion.div>
          )}
          {activeTab === 'research' && (
            <motion.div key="research" initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -16 }} transition={{ duration: 0.25 }}>
              <Research currentResult={currentResult} />
            </motion.div>
          )}
          {activeTab === 'graph' && (loading ? (
            <div style={{ textAlign: 'center', padding: '100px 0', color: 'var(--text-muted)', fontSize: 13 }}>
              <div className="spinner" style={{ margin: '0 auto 16px' }} />
              Loading skill ontology graph...
            </div>
          ) : graphData ? (
            <motion.div key="graph" initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3 }}>
              <GraphView data={graphData} />
            </motion.div>
          ) : (
            <div style={{ textAlign: 'center', padding: '100px 0', color: 'var(--text-muted)', fontSize: 13 }}>Failed to load graph data</div>
          ))}
        </AnimatePresence>
      </main>

      <footer style={{ borderTop: '1px solid var(--border-subtle)', padding: '24px 32px', textAlign: 'center' }}>
        <p style={{ fontSize: 12, color: 'var(--text-dim)' }}>
          Recommendation System Based on Graph Traversal and Artificial Intelligence
        </p>
      </footer>
    </div>
  );
};

// ──────────────────────────────
// Graph View — Full Ontology (Section 3)
// ──────────────────────────────
const GraphView = ({ data }: { data: { nodes: GraphNode[]; links: GraphLink[] } }) => (
  <div>
    <div style={{ marginBottom: 28 }}>
      <h2 style={{ fontSize: 28, fontWeight: 800, letterSpacing: '-0.04em' }}>
        <span className="gradient-text">Skill Ontology</span> Graph
      </h2>
      <p style={{ color: 'var(--text-secondary)', fontSize: 14, marginTop: 8 }}>
        Interactive visualization of <span style={{ color: 'var(--accent-cyan)', fontWeight: 600 }}>SUBSET_OF</span> and{' '}
        <span style={{ color: 'var(--accent-amber)', fontWeight: 600 }}>RELATED_TO</span> skill relationships in Neo4j
      </p>
    </div>
    <div className="graph-legend" style={{ marginBottom: 20 }}>
      <div className="legend-item"><div className="legend-line" style={{ background: 'var(--accent-cyan)' }} /><span>SUBSET_OF</span></div>
      <div className="legend-item"><div className="legend-line" style={{ background: 'var(--accent-amber)', opacity: 0.6 }} /><span>RELATED_TO</span></div>
    </div>
    <div className="graph-viz-container" style={{ minHeight: 560 }}>
      <ForceGraph2D
        graphData={{ nodes: data.nodes, links: data.links.map(l => ({ ...l })) }}
        nodeLabel="id"
        nodeColor={() => '#00d4ff'}
        linkColor={(link: GraphLink) => link.type === 'SUBSET_OF' ? 'rgba(0, 212, 255, 0.35)' : 'rgba(245, 158, 11, 0.25)'}
        linkDirectionalArrowLength={3.5}
        linkDirectionalArrowRelPos={1}
        nodeCanvasObject={(node: GraphNode, ctx: CanvasRenderingContext2D, globalScale: number) => {
          const label = node.id || '';
          const fontSize = 11 / globalScale;
          ctx.font = `600 ${fontSize}px Inter, system-ui, sans-serif`;
          ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
          ctx.beginPath(); ctx.arc(node.x || 0, node.y || 0, 8, 0, 2 * Math.PI);
          ctx.fillStyle = 'rgba(0, 212, 255, 0.08)'; ctx.fill();
          ctx.beginPath(); ctx.arc(node.x || 0, node.y || 0, 4, 0, 2 * Math.PI);
          ctx.fillStyle = '#00d4ff'; ctx.fill();
          ctx.fillStyle = 'rgba(152, 152, 176, 0.9)';
          ctx.fillText(label, node.x || 0, (node.y || 0) + 12 / globalScale);
        }}
        backgroundColor="#0a0a0f"
        height={560}
        width={Math.min(1136, window.innerWidth - 64)}
      />
    </div>
  </div>
);

export default App;
