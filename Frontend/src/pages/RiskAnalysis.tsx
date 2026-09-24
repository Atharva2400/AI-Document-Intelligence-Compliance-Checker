import { useNavigate } from 'react-router-dom';
import {
  AlertTriangle,
  Zap,
  TrendingUp,
  Info,
  ChevronRight,
  Target,
  BarChart3,
  Shield,
} from 'lucide-react';
import { useAnalysis } from '../context/AnalysisContext';

function SeverityBadge({ severity }: { severity: string }) {
  const map: Record<string, { bg: string; text: string; border: string; dot: string }> = {
    CRITICAL: { bg: 'bg-red-100', text: 'text-red-700', border: 'border-red-200', dot: 'bg-red-500' },
    HIGH: { bg: 'bg-orange-100', text: 'text-orange-700', border: 'border-orange-200', dot: 'bg-orange-500' },
    MEDIUM: { bg: 'bg-amber-100', text: 'text-amber-700', border: 'border-amber-200', dot: 'bg-amber-500' },
    LOW: { bg: 'bg-green-100', text: 'text-green-700', border: 'border-green-200', dot: 'bg-green-500' },
  };
  const s = map[severity] ?? { bg: 'bg-slate-100', text: 'text-slate-700', border: 'border-slate-200', dot: 'bg-slate-400' };
  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-bold border ${s.bg} ${s.text} ${s.border}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${s.dot}`} />
      {severity}
    </span>
  );
}

function RiskMeter({ score }: { score: number }) {
  const markers = [
    { label: 'Low', range: '0-40', color: 'bg-green-400' },
    { label: 'Medium', range: '40-70', color: 'bg-amber-400' },
    { label: 'High', range: '70-85', color: 'bg-orange-400' },
    { label: 'Critical', range: '85-100', color: 'bg-red-500' },
  ];

  return (
    <div className="space-y-2">
      <div className="relative h-4 rounded-full overflow-hidden flex">
        <div className="flex-1 bg-gradient-to-r from-green-400 to-amber-400" style={{ flexBasis: '40%' }} />
        <div className="flex-1 bg-gradient-to-r from-amber-400 to-orange-400" style={{ flexBasis: '30%' }} />
        <div className="flex-1 bg-gradient-to-r from-orange-400 to-red-500" style={{ flexBasis: '30%' }} />
        {/* Needle */}
        <div
          className="absolute top-0 bottom-0 w-0.5 bg-slate-900 shadow-md transition-all duration-500"
          style={{ left: `${Math.min(100, Math.max(0, score))}%` }}
        >
          <div className="absolute -top-1 left-1/2 -translate-x-1/2 w-3 h-3 rounded-full bg-slate-900 border-2 border-white shadow" />
        </div>
      </div>
      <div className="flex justify-between text-xs text-slate-400 font-medium">
        {markers.map(m => <span key={m.label}>{m.label}</span>)}
      </div>
    </div>
  );
}

const categoryIcons: Record<string, React.ElementType> = {
  'Structural Defect': BarChart3,
  'Legal Compliance': Shield,
  'Employment Terms': AlertTriangle,
  'Restrictive Covenants': Target,
  'Process Gap': Info,
};

export default function RiskAnalysis() {
  const navigate = useNavigate();
  const { currentStats: dashboardStats, currentRiskIssues: riskIssues } = useAnalysis();
  const riskScore = dashboardStats.riskScore;

  const criticalCount = riskIssues.filter(r => r.severity === 'CRITICAL').length;
  const highCount = riskIssues.filter(r => r.severity === 'HIGH').length;
  const mediumCount = riskIssues.filter(r => r.severity === 'MEDIUM').length;
  const lowCount = riskIssues.filter(r => r.severity === 'LOW').length;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Risk Analysis</h1>
        <p className="text-slate-500 text-sm mt-1">
          AI-driven risk scoring and prioritized issue remediation for {dashboardStats.documentName}.
        </p>
      </div>

      {/* Overall risk + breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Risk Score */}
        <div className="lg:col-span-1 bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
          <h2 className="text-base font-bold text-slate-900 mb-5 flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-orange-500" />
            Overall Risk Score
          </h2>
          <div className="text-center mb-6">
            <div className="text-6xl font-bold text-orange-500">{riskScore}</div>
            <div className="text-slate-400 text-sm mt-1">out of 100</div>
            <div className="mt-3 inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-orange-100 border border-orange-200 text-orange-700 text-xs font-bold uppercase">
              <AlertTriangle className="w-3.5 h-3.5" />
              {dashboardStats.risk} RISK
            </div>
          </div>
          <RiskMeter score={riskScore} />
          <div className="mt-6 text-xs text-slate-400 text-center">
            Score based on {riskIssues.length} identified issues across all categories
          </div>
        </div>

        {/* Issue breakdown */}
        <div className="lg:col-span-2 bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
          <h2 className="text-base font-bold text-slate-900 mb-5 flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-blue-600" />
            Issue Breakdown
          </h2>
          <div className="space-y-3">
            {[
              { label: 'Critical', count: criticalCount, color: 'red', bar: 'bg-red-500' },
              { label: 'High', count: highCount, color: 'orange', bar: 'bg-orange-500' },
              { label: 'Medium', count: mediumCount, color: 'amber', bar: 'bg-amber-500' },
              { label: 'Low', count: lowCount, color: 'green', bar: 'bg-green-500' },
            ].map(({ label, count, color, bar }) => (
              <div key={label} className="flex items-center gap-4">
                <span className={`w-16 text-xs font-bold text-right ${
                  color === 'red' ? 'text-red-600' :
                  color === 'orange' ? 'text-orange-600' :
                  color === 'amber' ? 'text-amber-600' : 'text-green-600'
                }`}>{label}</span>
                <div className="flex-1 h-7 bg-slate-100 rounded-lg overflow-hidden">
                  <div
                    className={`h-full ${bar} rounded-lg flex items-center justify-end pr-2 transition-all duration-700`}
                    style={{ width: `${riskIssues.length ? (count / riskIssues.length) * 100 : 0}%`, minWidth: count > 0 ? '2rem' : '0' }}
                  >
                    {count > 0 && <span className="text-white text-xs font-bold">{count}</span>}
                  </div>
                </div>
                <span className="w-4 text-xs font-semibold text-slate-500 text-right">{count}</span>
              </div>
            ))}
          </div>

          {/* Quick stats */}
          <div className="mt-6 grid grid-cols-2 gap-3">
            <div className="p-3 rounded-xl bg-slate-50 border border-slate-100">
              <p className="text-xs text-slate-500 font-medium">AI Confidence</p>
              <p className="text-2xl font-bold text-blue-600 mt-0.5">{dashboardStats.aiConfidence}%</p>
            </div>
            <div className="p-3 rounded-xl bg-slate-50 border border-slate-100">
              <p className="text-xs text-slate-500 font-medium">Total Issues</p>
              <p className="text-2xl font-bold text-slate-900 mt-0.5">{riskIssues.length}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Prioritized issues list */}
      <div>
        <h2 className="text-xl font-bold text-slate-900 mb-4 flex items-center gap-2">
          <Zap className="w-5 h-5 text-orange-500" />
          Prioritized Issues — Action Required
        </h2>
        <div className="space-y-4">
          {riskIssues.map((issue, idx) => {
            const CategoryIcon = categoryIcons[issue.category] || Info;
            return (
              <div
                key={issue.id}
                className={`bg-white rounded-2xl border-l-4 border shadow-sm hover:shadow-md transition-shadow overflow-hidden ${
                  issue.severity === 'CRITICAL'
                    ? 'border-l-red-500 border-slate-200'
                    : issue.severity === 'HIGH'
                    ? 'border-l-orange-500 border-slate-200'
                    : issue.severity === 'MEDIUM'
                    ? 'border-l-amber-500 border-slate-200'
                    : 'border-l-green-400 border-slate-200'
                }`}
              >
                <div className="p-5">
                  <div className="flex items-start justify-between gap-4 flex-wrap">
                    <div className="flex items-start gap-4">
                      <div className="flex items-center justify-center w-8 h-8 rounded-full bg-slate-100 text-slate-500 text-sm font-bold shrink-0">
                        {idx + 1}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 flex-wrap mb-1">
                          <h3 className="text-base font-bold text-slate-900">{issue.title}</h3>
                          <SeverityBadge severity={issue.severity} />
                          <span className="text-xs font-mono text-slate-400">{issue.id}</span>
                        </div>
                        <div className="flex items-center gap-2 text-xs text-slate-400 mb-3">
                          <CategoryIcon className="w-3.5 h-3.5" />
                          <span>{issue.category}</span>
                          <span>·</span>
                          <span className="font-mono">{issue.clause}</span>
                        </div>
                      </div>
                    </div>
                    <span className={`shrink-0 text-xs font-bold px-2.5 py-1 rounded-lg ${
                      issue.status === 'Open'
                        ? 'bg-red-50 text-red-600 border border-red-200'
                        : issue.status === 'Review'
                        ? 'bg-amber-50 text-amber-600 border border-amber-200'
                        : 'bg-slate-50 text-slate-500 border border-slate-200'
                    }`}>
                      {issue.status}
                    </span>
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-2">
                    <div className="p-3 rounded-xl bg-red-50 border border-red-100">
                      <p className="text-xs font-bold text-red-400 uppercase tracking-wider mb-1">Impact / Action</p>
                      <p className="text-sm text-red-800 leading-relaxed">{issue.impact}</p>
                    </div>
                    <div className="p-3 rounded-xl bg-blue-50 border border-blue-100">
                      <p className="text-xs font-bold text-blue-400 uppercase tracking-wider mb-1">Recommendation</p>
                      <p className="text-sm text-blue-800 leading-relaxed">{issue.recommendation}</p>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Bottom CTA */}
      <div className="flex justify-end gap-3">
        <button
          onClick={() => navigate('/reports')}
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-violet-600 text-white text-sm font-bold shadow-md hover:shadow-lg transition-all"
        >
          Generate Full Report
          <ChevronRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}
