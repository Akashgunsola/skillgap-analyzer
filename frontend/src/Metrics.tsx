import { useState, useEffect } from 'react';
import axios from 'axios';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  Cell
} from 'recharts';

const API_BASE = 'http://localhost:8000/api';

interface MetricsData {
  k: number;
  candidates: number;
  total_jobs: number;
  precision: { keyword: number; graph: number };
  recall: { keyword: number; graph: number };
  diversity: { keyword: number; graph: number };
  novelty: { graph_only_count: number; description: string };
}

const Metrics = () => {
  const [data, setData] = useState<MetricsData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get(`${API_BASE}/metrics`)
      .then(res => { setData(res.data); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);

  if (loading) return (
    <div style={{ textAlign: 'center', padding: '80px 0', color: '#a1a1aa', fontSize: 13 }}>
      <div style={{ width: 20, height: 20, border: '2px solid #e4e4e7', borderTopColor: '#18181b', borderRadius: '50%', animation: 'spin 0.8s linear infinite', margin: '0 auto 12px' }} />
      Computing metrics across all candidates...
    </div>
  );

  if (!data) return (
    <div style={{ textAlign: 'center', padding: '80px 0', color: '#a1a1aa' }}>
      Failed to load metrics. Is the backend running?
    </div>
  );

  const precisionData = [
    { name: 'Keyword', value: data.precision.keyword },
    { name: 'Graph', value: data.precision.graph },
  ];
  const recallData = [
    { name: 'Keyword', value: data.recall.keyword },
    { name: 'Graph', value: data.recall.graph },
  ];
  const diversityData = [
    { name: 'Keyword', value: data.diversity.keyword },
    { name: 'Graph', value: data.diversity.graph },
  ];

  const colors = ['#a1a1aa', '#18181b'];

  const MiniChart = ({ title, chartData, unit = '%', subtitle }: {
    title: string; chartData: { name: string; value: number }[]; unit?: string; subtitle?: string;
  }) => (
    <div className="card">
      <p className="section-title">{title}</p>
      {subtitle && <p style={{ fontSize: 12, color: '#a1a1aa', marginBottom: 16, marginTop: -8 }}>{subtitle}</p>}
      <div style={{ height: 200 }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} margin={{ top: 8, right: 8, left: -20, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f4f4f5" />
            <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fill: '#71717a', fontSize: 12, fontWeight: 600 }} />
            <YAxis unit={unit} axisLine={false} tickLine={false} tick={{ fill: '#a1a1aa', fontSize: 11 }} />
            <Tooltip
              cursor={{ fill: 'rgba(0,0,0,0.02)' }}
              contentStyle={{ background: '#fff', border: '1px solid #e4e4e7', borderRadius: 8, fontSize: 13 }}
            />
            <Bar dataKey="value" radius={[4, 4, 0, 0]} barSize={48}>
              {chartData.map((_entry, i) => (
                <Cell key={i} fill={colors[i]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 12, padding: '0 4px' }}>
        {chartData.map((d, i) => (
          <div key={d.name} style={{ textAlign: i === 0 ? 'left' : 'right' }}>
            <span style={{ fontSize: 20, fontWeight: 800, color: colors[i] }}>{d.value}{unit}</span>
          </div>
        ))}
      </div>
    </div>
  );

  return (
    <div>
      <div style={{ marginBottom: 32 }}>
        <h2 style={{ fontSize: 28, fontWeight: 800, letterSpacing: '-0.04em' }}>Performance Comparison</h2>
        <p style={{ color: '#a1a1aa', fontSize: 14, marginTop: 6 }}>
          Evaluated across {data.candidates} candidates and {data.total_jobs} jobs at K={data.k}
        </p>
      </div>

      {/* Stat row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12, marginBottom: 28 }}>
        <div className="card" style={{ textAlign: 'center' }}>
          <p style={{ fontSize: 11, fontWeight: 600, color: '#a1a1aa', textTransform: 'uppercase', letterSpacing: '0.08em' }}>Candidates</p>
          <p style={{ fontSize: 28, fontWeight: 800, marginTop: 4 }}>{data.candidates}</p>
        </div>
        <div className="card" style={{ textAlign: 'center' }}>
          <p style={{ fontSize: 11, fontWeight: 600, color: '#a1a1aa', textTransform: 'uppercase', letterSpacing: '0.08em' }}>Jobs Scored</p>
          <p style={{ fontSize: 28, fontWeight: 800, marginTop: 4 }}>{data.total_jobs}</p>
        </div>
        <div className="card" style={{ textAlign: 'center' }}>
          <p style={{ fontSize: 11, fontWeight: 600, color: '#a1a1aa', textTransform: 'uppercase', letterSpacing: '0.08em' }}>K Value</p>
          <p style={{ fontSize: 28, fontWeight: 800, marginTop: 4 }}>{data.k}</p>
        </div>
        <div className="card" style={{ textAlign: 'center', border: '1.5px solid #18181b' }}>
          <p style={{ fontSize: 11, fontWeight: 600, color: '#a1a1aa', textTransform: 'uppercase', letterSpacing: '0.08em' }}>Novel Discoveries</p>
          <p style={{ fontSize: 28, fontWeight: 800, marginTop: 4 }}>{data.novelty.graph_only_count}</p>
        </div>
      </div>

      {/* Charts grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 24 }}>
        <MiniChart title={`Precision @${data.k}`} chartData={precisionData} subtitle="% of top-K recommendations that are relevant" />
        <MiniChart title={`Recall @${data.k}`} chartData={recallData} subtitle="% of relevant jobs found in top-K" />
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
        <MiniChart title="Diversity" chartData={diversityData} unit="" subtitle="Unique jobs recommended across all candidates" />
        <div className="card">
          <p className="section-title">Novelty</p>
          <p style={{ fontSize: 12, color: '#a1a1aa', marginBottom: 20, marginTop: -8 }}>Jobs found by Graph that Keyword missed</p>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: 160 }}>
            <div style={{ textAlign: 'center' }}>
              <p style={{ fontSize: 56, fontWeight: 800, lineHeight: 1 }}>{data.novelty.graph_only_count}</p>
              <p style={{ fontSize: 13, color: '#71717a', marginTop: 8, maxWidth: 260 }}>
                unique job recommendations discovered exclusively through graph traversal
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Legend */}
      <div style={{ display: 'flex', gap: 20, justifyContent: 'center', marginTop: 24 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <div style={{ width: 12, height: 12, borderRadius: 3, background: '#a1a1aa' }} />
          <span style={{ fontSize: 12, color: '#71717a', fontWeight: 500 }}>Keyword Matching</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <div style={{ width: 12, height: 12, borderRadius: 3, background: '#18181b' }} />
          <span style={{ fontSize: 12, color: '#71717a', fontWeight: 500 }}>Graph Matching</span>
        </div>
      </div>
    </div>
  );
};

export default Metrics;
