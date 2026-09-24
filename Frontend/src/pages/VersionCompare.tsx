import { useNavigate } from 'react-router-dom';
import {
  GitCompare,
  TrendingUp,
  TrendingDown,
  Minus,
  AlertTriangle,
  Brain,
  ChevronRight,
  ArrowRight,
  Info,
} from 'lucide-react';
import { versionComparison } from '../data/mockData';

function ImpactBadge({ impact }: { impact: string }) {
  const map: Record<string, string> = {
    CRITICAL: 'bg-red-100 text-red-700 border-red-200',
    HIGH: 'bg-orange-100 text-orange-700 border-orange-200',
    MEDIUM: 'bg-amber-100 text-amber-700 border-amber-200',
    LOW: 'bg-green-100 text-green-700 border-green-200',
  };
  return (
    <span className={`inline-flex px-2.5 py-0.5 rounded-full text-xs font-bold border ${map[impact] ?? 'bg-slate-100 text-slate-600'}`}>
      {impact}
    </span>
  );
}

function SignificanceBadge({ sig }: { sig: string }) {
  if (sig === 'Significant')
    return <span className="text-xs font-bold text-blue-700 bg-blue-50 border border-blue-200 px-2 py-0.5 rounded-full">⭐ Significant</span>;
  return <span className="text-xs font-medium text-slate-500 bg-slate-50 border border-slate-200 px-2 py-0.5 rounded-full">{sig}</span>;
}

function DeltaIcon({ v1, v2 }: { v1: string; v2: string }) {
  const extractNumber = (s: string) => {
    const match = s.match(/[\d,.]+/);
    return match ? parseFloat(match[0].replace(/,/g, '')) : null;
  };
  const n1 = extractNumber(v1);
  const n2 = extractNumber(v2);
  if (n1 !== null && n2 !== null) {
    if (n2 > n1) return <TrendingUp className="w-4 h-4 text-green-500" />;
    if (n2 < n1) return <TrendingDown className="w-4 h-4 text-red-500" />;
  }
  return <Minus className="w-4 h-4 text-slate-400" />;
}

export default function VersionCompare() {
  const navigate = useNavigate();
  const { v1, v2, summary, changes, aiSummary } = versionComparison;

  const significantChanges = changes.filter(c => c.significance === 'Significant');

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Version Comparison</h1>
        <p className="text-slate-500 text-sm mt-1">
          AI-powered diff analysis highlighting what changed and what matters.
        </p>
      </div>

      {/* Version header cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {[
          { ver: 'Version 1', doc: v1, color: 'blue' },
          { ver: 'Version 2', doc: v2, color: 'violet' },
        ].map(({ ver, doc, color }) => (
          <div
            key={ver}
            className={`bg-white rounded-2xl border-2 p-5 shadow-sm ${
              color === 'blue' ? 'border-blue-200' : 'border-violet-200'
            }`}
          >
            <div className="flex items-center gap-2 mb-3">
              <span
                className={`text-xs font-bold px-2.5 py-1 rounded-lg ${
                  color === 'blue' ? 'bg-blue-100 text-blue-700' : 'bg-violet-100 text-violet-700'
                }`}
              >
                {ver}
              </span>
              {color === 'violet' && (
                <span className="text-xs font-semibold text-green-700 bg-green-50 border border-green-200 px-2 py-0.5 rounded-full">
                  Latest
                </span>
              )}
            </div>
            <p className="text-base font-bold text-slate-900">{doc.name}</p>
            <div className="flex items-center gap-4 mt-2 text-xs text-slate-400">
              <span>📅 {doc.date}</span>
              <span>👤 {doc.author}</span>
            </div>
          </div>
        ))}
      </div>

      {/* Summary stats */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {[
          { label: 'Total Changes', value: summary.totalChanges, color: 'text-blue-600' },
          { label: 'Significant', value: summary.significantChanges, color: 'text-orange-600' },
          { label: 'Added Clauses', value: summary.addedClauses, color: 'text-green-600' },
          { label: 'Modified', value: summary.modifiedClauses, color: 'text-violet-600' },
        ].map(({ label, value, color }) => (
          <div key={label} className="bg-white rounded-2xl border border-slate-200 p-5 text-center shadow-sm">
            <p className={`text-3xl font-bold ${color}`}>{value}</p>
            <p className="text-xs text-slate-500 font-semibold mt-1">{label}</p>
          </div>
        ))}
      </div>

      {/* AI Summary banner */}
      <div className="bg-gradient-to-r from-slate-800 to-slate-900 rounded-2xl p-6 text-white shadow-xl">
        <div className="flex items-start gap-4">
          <div className="shrink-0 w-10 h-10 rounded-xl bg-blue-500/20 border border-blue-400/30 flex items-center justify-center">
            <Brain className="w-5 h-5 text-blue-300" />
          </div>
          <div>
            <div className="flex items-center gap-2 mb-2">
              <p className="text-xs font-bold text-blue-300 uppercase tracking-wider">AI Summary</p>
              <span className="text-xs text-slate-400">What Changed + What Matters</span>
            </div>
            <p className="text-sm text-slate-200 leading-relaxed">{aiSummary}</p>
          </div>
        </div>
      </div>

      {/* Significant changes */}
      <div>
        <h2 className="text-lg font-bold text-slate-900 mb-4 flex items-center gap-2">
          <AlertTriangle className="w-5 h-5 text-orange-500" />
          Significant Changes — Require Review
        </h2>
        <div className="space-y-3">
          {significantChanges.map((change) => (
            <div
              key={change.id}
              className="bg-white rounded-2xl border border-slate-200 shadow-sm hover:shadow-md transition-shadow overflow-hidden"
            >
              <div className="flex items-stretch">
                {/* Left accent bar */}
                <div
                  className={`w-1.5 shrink-0 ${
                    change.impact === 'CRITICAL' ? 'bg-red-500' :
                    change.impact === 'HIGH' ? 'bg-orange-500' :
                    change.impact === 'MEDIUM' ? 'bg-amber-500' : 'bg-green-400'
                  }`}
                />
                <div className="flex-1 p-5">
                  <div className="flex items-center justify-between gap-3 flex-wrap mb-3">
                    <div className="flex items-center gap-2">
                      <DeltaIcon v1={change.v1Value} v2={change.v2Value} />
                      <span className="text-sm font-bold text-slate-900">{change.field}</span>
                      <span className="text-xs font-mono text-slate-400">{change.clause}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <ImpactBadge impact={change.impact} />
                      <SignificanceBadge sig={change.significance} />
                    </div>
                  </div>
                  {/* Before → After */}
                  <div className="flex items-center gap-3 mb-3">
                    <div className="flex-1 px-4 py-2.5 rounded-xl bg-red-50 border border-red-100 text-center">
                      <p className="text-xs font-semibold text-red-400 mb-0.5">Before (v1)</p>
                      <p className="text-base font-bold text-red-700">{change.v1Value}</p>
                    </div>
                    <ArrowRight className="w-5 h-5 text-slate-400 shrink-0" />
                    <div className="flex-1 px-4 py-2.5 rounded-xl bg-green-50 border border-green-100 text-center">
                      <p className="text-xs font-semibold text-green-400 mb-0.5">After (v2)</p>
                      <p className="text-base font-bold text-green-700">{change.v2Value}</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-2 p-3 bg-amber-50 border border-amber-100 rounded-xl">
                    <Info className="w-4 h-4 text-amber-500 shrink-0 mt-0.5" />
                    <p className="text-xs text-amber-800 leading-relaxed">{change.detail}</p>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* All other changes table */}
      <div>
        <h2 className="text-lg font-bold text-slate-900 mb-4 flex items-center gap-2">
          <GitCompare className="w-5 h-5 text-blue-600" />
          All Changes
        </h2>
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200">
                  <th className="text-left text-xs font-bold text-slate-500 uppercase tracking-wider px-5 py-3.5">Field</th>
                  <th className="text-left text-xs font-bold text-slate-500 uppercase tracking-wider px-4 py-3.5 hidden sm:table-cell">Clause</th>
                  <th className="text-left text-xs font-bold text-slate-500 uppercase tracking-wider px-4 py-3.5">Before</th>
                  <th className="w-8"></th>
                  <th className="text-left text-xs font-bold text-slate-500 uppercase tracking-wider px-4 py-3.5">After</th>
                  <th className="text-left text-xs font-bold text-slate-500 uppercase tracking-wider px-4 py-3.5">Impact</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {changes.map((change) => (
                  <tr key={change.id} className="hover:bg-slate-50 transition-colors">
                    <td className="px-5 py-3.5">
                      <div className="flex items-center gap-2">
                        <DeltaIcon v1={change.v1Value} v2={change.v2Value} />
                        <p className="text-sm font-semibold text-slate-900">{change.field}</p>
                      </div>
                    </td>
                    <td className="px-4 py-3.5 hidden sm:table-cell">
                      <span className="text-xs font-mono text-slate-400">{change.clause}</span>
                    </td>
                    <td className="px-4 py-3.5">
                      <span className="text-sm text-red-600 font-medium line-through decoration-red-300">{change.v1Value}</span>
                    </td>
                    <td className="px-2 py-3.5 text-slate-300">→</td>
                    <td className="px-4 py-3.5">
                      <span className="text-sm text-green-700 font-semibold">{change.v2Value}</span>
                    </td>
                    <td className="px-4 py-3.5">
                      <ImpactBadge impact={change.impact} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div className="flex justify-end">
        <button
          onClick={() => navigate('/reports')}
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-violet-600 text-white text-sm font-bold shadow-md hover:shadow-lg transition-all"
        >
          View Full Report
          <ChevronRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}
