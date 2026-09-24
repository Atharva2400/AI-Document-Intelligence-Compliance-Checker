import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  ShieldCheck,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  ChevronDown,
  ChevronUp,
  Filter,
  Download,
} from 'lucide-react';
import { useAnalysis } from '../context/AnalysisContext';

type FilterType = 'all' | 'pass' | 'warning' | 'fail';

function SeverityBadge({ severity }: { severity: string }) {
  const map: Record<string, string> = {
    CRITICAL: 'bg-red-100 text-red-700 border-red-200',
    HIGH: 'bg-orange-100 text-orange-700 border-orange-200',
    MEDIUM: 'bg-amber-100 text-amber-700 border-amber-200',
    LOW: 'bg-green-100 text-green-700 border-green-200',
  };
  return (
    <span className={`inline-flex px-2.5 py-0.5 rounded-full text-xs font-bold border ${map[severity] ?? 'bg-slate-100 text-slate-600'}`}>
      {severity}
    </span>
  );
}

function StatusIcon({ status }: { status: string }) {
  if (status === 'pass') return <CheckCircle2 className="w-5 h-5 text-green-500" />;
  if (status === 'fail') return <XCircle className="w-5 h-5 text-red-500" />;
  return <AlertTriangle className="w-5 h-5 text-amber-500" />;
}

export default function Compliance() {
  const navigate = useNavigate();
  const { currentComplianceRules: complianceRules, currentContradictions: contradictions } = useAnalysis();

  const [filter, setFilter] = useState<FilterType>('all');
  const [expanded, setExpanded] = useState<string | null>(null);

  const filtered = complianceRules.filter(
    (r) => filter === 'all' || r.status === filter
  );
  const passCount = complianceRules.filter(r => r.status === 'pass').length;
  const warnCount = complianceRules.filter(r => r.status === 'warning').length;
  const failCount = complianceRules.filter(r => r.status === 'fail').length;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Compliance Checker</h1>
          <p className="text-slate-500 text-sm mt-1">
            Automated rule-based compliance analysis with evidence and recommendations.
          </p>
        </div>
        <button className="inline-flex items-center gap-2 px-4 py-2 rounded-xl border border-slate-200 bg-white text-sm font-semibold text-slate-600 hover:bg-slate-50 shadow-sm">
          <Download className="w-4 h-4" />
          Export CSV
        </button>
      </div>

      {/* Summary cards */}
      <div className="grid grid-cols-3 gap-4">
        {[
          { label: 'Passed', count: passCount, color: 'green', icon: CheckCircle2 },
          { label: 'Warnings', count: warnCount, color: 'amber', icon: AlertTriangle },
          { label: 'Failed', count: failCount, color: 'red', icon: XCircle },
        ].map(({ label, count, color, icon: Icon }) => (
          <div
            key={label}
            className={`bg-white rounded-2xl border p-5 shadow-sm text-center cursor-pointer hover:shadow-md transition-shadow ${
              color === 'green'
                ? 'border-green-200 hover:border-green-300'
                : color === 'amber'
                ? 'border-amber-200 hover:border-amber-300'
                : 'border-red-200 hover:border-red-300'
            }`}
            onClick={() =>
              setFilter(
                label === 'Passed' ? 'pass' : label === 'Warnings' ? 'warning' : 'fail'
              )
            }
          >
            <Icon
              className={`w-6 h-6 mx-auto mb-2 ${
                color === 'green' ? 'text-green-500' : color === 'amber' ? 'text-amber-500' : 'text-red-500'
              }`}
            />
            <p
              className={`text-3xl font-bold ${
                color === 'green' ? 'text-green-600' : color === 'amber' ? 'text-amber-600' : 'text-red-600'
              }`}
            >
              {count}
            </p>
            <p className="text-xs font-semibold text-slate-500 mt-1">{label}</p>
          </div>
        ))}
      </div>

      {/* Filter row */}
      <div className="flex items-center gap-2 flex-wrap">
        <Filter className="w-4 h-4 text-slate-400" />
        <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Filter:</span>
        {(['all', 'pass', 'warning', 'fail'] as FilterType[]).map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold capitalize transition-colors ${
              filter === f
                ? 'bg-blue-600 text-white'
                : 'bg-white border border-slate-200 text-slate-600 hover:border-blue-300'
            }`}
          >
            {f === 'all' ? 'All Rules' : f}
          </button>
        ))}
        <span className="ml-auto text-xs text-slate-400">{filtered.length} rules shown</span>
      </div>

      {/* Rules table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200">
                <th className="text-left text-xs font-bold text-slate-500 uppercase tracking-wider px-5 py-3.5 w-8">#</th>
                <th className="text-left text-xs font-bold text-slate-500 uppercase tracking-wider px-4 py-3.5">Rule</th>
                <th className="text-left text-xs font-bold text-slate-500 uppercase tracking-wider px-4 py-3.5 hidden sm:table-cell">Category</th>
                <th className="text-left text-xs font-bold text-slate-500 uppercase tracking-wider px-4 py-3.5">Status</th>
                <th className="text-left text-xs font-bold text-slate-500 uppercase tracking-wider px-4 py-3.5 hidden md:table-cell">Severity</th>
                <th className="w-10"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filtered.map((rule) => (
                <tbody key={rule.id}>
                  <tr
                    className={`hover:bg-slate-50 transition-colors cursor-pointer ${
                      expanded === rule.id ? 'bg-slate-50' : ''
                    }`}
                    onClick={() => setExpanded(expanded === rule.id ? null : rule.id)}
                  >
                    <td className="px-5 py-4 text-xs font-mono text-slate-400">{rule.id}</td>
                    <td className="px-4 py-4">
                      <p className="text-sm font-semibold text-slate-900">{rule.rule}</p>
                    </td>
                    <td className="px-4 py-4 hidden sm:table-cell">
                      <span className="text-xs font-medium text-slate-500 bg-slate-100 px-2 py-0.5 rounded-md">
                        {rule.category}
                      </span>
                    </td>
                    <td className="px-4 py-4">
                      <div className="flex items-center gap-2">
                        <StatusIcon status={rule.status} />
                        <span
                          className={`text-xs font-bold ${
                            rule.status === 'pass'
                              ? 'text-green-600'
                              : rule.status === 'fail'
                              ? 'text-red-600'
                              : 'text-amber-600'
                          }`}
                        >
                          {rule.status.toUpperCase()}
                        </span>
                      </div>
                    </td>
                    <td className="px-4 py-4 hidden md:table-cell">
                      <SeverityBadge severity={rule.severity} />
                    </td>
                    <td className="px-4 py-4 text-slate-400">
                      {expanded === rule.id ? (
                        <ChevronUp className="w-4 h-4" />
                      ) : (
                        <ChevronDown className="w-4 h-4" />
                      )}
                    </td>
                  </tr>
                  {expanded === rule.id && (
                    <tr className="bg-slate-50">
                      <td colSpan={6} className="px-5 py-4">
                        <div className="space-y-3 pl-4 border-l-4 border-blue-200 ml-2">
                          <div>
                            <p className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Evidence</p>
                            <p className="text-sm text-slate-700 font-mono bg-white rounded-lg px-3 py-2 border border-slate-200">
                              "{rule.evidence}"
                            </p>
                          </div>
                          <div>
                            <p className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Recommendation</p>
                            <p className="text-sm text-slate-700">{rule.recommendation}</p>
                          </div>
                        </div>
                      </td>
                    </tr>
                  )}
                </tbody>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Contradiction Detection */}
      {contradictions && contradictions.length > 0 && (
        <div>
          <h2 className="text-xl font-bold text-slate-900 mb-4 flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-red-500" />
            Contradiction Detection
          </h2>
          <div className="space-y-4">
            {contradictions.map((c) => (
              <div
                key={c.id}
                className="bg-white rounded-2xl border-2 border-red-200 shadow-sm overflow-hidden"
              >
                {/* Header */}
                <div className="flex items-center justify-between px-6 py-4 bg-red-50 border-b border-red-100">
                  <div className="flex items-center gap-3">
                    <div className="flex items-center justify-center w-8 h-8 rounded-full bg-red-100">
                      <AlertTriangle className="w-4 h-4 text-red-600" />
                    </div>
                    <div>
                      <p className="text-sm font-bold text-red-800">Contradiction Detected</p>
                      <p className="text-xs text-red-500">{c.id} · {c.title}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-semibold text-slate-600">Confidence: <strong className="text-blue-700">{c.confidence}%</strong></span>
                    <SeverityBadge severity={c.severity} />
                  </div>
                </div>

                <div className="p-6 space-y-5">
                  {/* Clauses side-by-side */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    {[c.clause1, c.clause2].map((clause) => (
                      <div key={clause.id} className="p-4 rounded-xl bg-slate-50 border border-slate-200">
                        <div className="flex items-center gap-2 mb-2">
                          <span className="text-xs font-bold text-blue-700 bg-blue-100 px-2 py-0.5 rounded">
                            {clause.id}
                          </span>
                          <span className="text-xs font-semibold text-slate-600">{clause.title}</span>
                        </div>
                        <p className="text-sm text-slate-700 italic leading-relaxed">{clause.text}</p>
                      </div>
                    ))}
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-sm">
                    <div>
                      <p className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Evidence</p>
                      <p className="text-slate-700 leading-relaxed">{c.evidence}</p>
                    </div>
                    <div>
                      <p className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Impact</p>
                      <p className="text-slate-700 leading-relaxed">{c.impact}</p>
                    </div>
                    <div>
                      <p className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Recommendation</p>
                      <p className="text-slate-700 leading-relaxed">{c.recommendation}</p>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Navigate to reports */}
      <div className="flex justify-end">
        <button
          onClick={() => navigate('/reports')}
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-slate-900 text-white text-sm font-semibold hover:bg-slate-800 transition-colors"
        >
          View Full Report
          <ChevronDown className="w-4 h-4 rotate-[-90deg]" />
        </button>
      </div>
    </div>
  );
}
