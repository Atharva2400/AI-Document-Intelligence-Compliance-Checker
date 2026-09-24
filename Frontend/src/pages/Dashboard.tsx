import { useNavigate } from 'react-router-dom';
import {
  TrendingUp,
  ShieldAlert,
  AlertCircle,
  Zap,
  FileText,
  Clock,
  ChevronRight,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Activity,
  BarChart3,
  Brain,
  Lock,
} from 'lucide-react';
import { useAnalysis } from '../context/AnalysisContext';

function ComplianceGauge({ score }: { score: number }) {
  const radius = 80;
  const stroke = 12;
  const normalizedRadius = radius - stroke / 2;
  const circumference = normalizedRadius * 2 * Math.PI;
  const strokeDashoffset = circumference - (score / 100) * circumference;
  const color = score >= 80 ? '#22c55e' : score >= 60 ? '#f59e0b' : '#ef4444';

  return (
    <div className="relative flex items-center justify-center w-48 h-48 mx-auto">
      <svg
        height={radius * 2}
        width={radius * 2}
        className="transform -rotate-90"
      >
        <circle
          stroke="#e2e8f0"
          fill="transparent"
          strokeWidth={stroke}
          r={normalizedRadius}
          cx={radius}
          cy={radius}
        />
        <circle
          stroke={color}
          fill="transparent"
          strokeWidth={stroke}
          strokeDasharray={`${circumference} ${circumference}`}
          style={{
            strokeDashoffset,
            transition: 'stroke-dashoffset 1s ease-in-out',
          }}
          strokeLinecap="round"
          r={normalizedRadius}
          cx={radius}
          cy={radius}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-4xl font-bold text-slate-900">{score}</span>
        <span className="text-sm text-slate-500 font-medium">/ 100</span>
        <span className="text-xs font-semibold text-green-600 mt-1">
          {score >= 80 ? 'Good' : score >= 60 ? 'Moderate' : 'Poor'}
        </span>
      </div>
    </div>
  );
}

function StatCard({
  label,
  value,
  icon: Icon,
  color,
  subtitle,
}: {
  label: string;
  value: string | number;
  icon: React.ElementType;
  color: string;
  subtitle?: string;
}) {
  return (
    <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm hover:shadow-md transition-shadow duration-200">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">{label}</p>
          <p className={`text-3xl font-bold mt-1 ${color}`}>{value}</p>
          {subtitle && <p className="text-xs text-slate-400 mt-1">{subtitle}</p>}
        </div>
        <div className="p-2.5 rounded-xl bg-slate-50">
          <Icon className={`w-5 h-5 ${color}`} />
        </div>
      </div>
    </div>
  );
}

function RiskBadge({ risk }: { risk: string }) {
  const map: Record<string, string> = {
    CRITICAL: 'bg-red-100 text-red-700 border-red-200',
    HIGH: 'bg-orange-100 text-orange-700 border-orange-200',
    MEDIUM: 'bg-amber-100 text-amber-700 border-amber-200',
    LOW: 'bg-green-100 text-green-700 border-green-200',
  };
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-bold border ${map[risk] ?? 'bg-slate-100 text-slate-600'}`}>
      {risk}
    </span>
  );
}

function StatusIcon({ status }: { status: string }) {
  if (status === 'pass') return <CheckCircle2 className="w-4 h-4 text-green-500" />;
  if (status === 'fail') return <XCircle className="w-4 h-4 text-red-500" />;
  return <AlertTriangle className="w-4 h-4 text-amber-500" />;
}

export default function Dashboard() {
  const navigate = useNavigate();
  const {
    currentStats: stats,
    currentClauses: clauses,
    currentComplianceRules: complianceRules,
    currentRiskIssues: riskIssues,
  } = useAnalysis();

  const passCount = complianceRules.filter(r => r.status === 'pass').length;
  const failCount = complianceRules.filter(r => r.status === 'fail').length;
  const warnCount = complianceRules.filter(r => r.status === 'warning').length;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Hero banner */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-blue-700 via-blue-600 to-violet-600 p-8 text-white shadow-xl">
        <div className="absolute top-0 right-0 w-64 h-64 opacity-10">
          <Brain className="w-full h-full" />
        </div>
        <div className="relative z-10 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-white/20 text-xs font-semibold mb-3">
              <Activity className="w-3.5 h-3.5" />
              Analysis Complete
            </div>
            <h1 className="text-2xl font-bold">{stats.documentName}</h1>
            <p className="text-blue-100 text-sm mt-1">
              {stats.documentType} · {stats.pageCount} pages · {stats.wordCount.toLocaleString()} words
            </p>
            <p className="text-blue-200 text-xs mt-2 flex items-center gap-1">
              <Clock className="w-3.5 h-3.5" />
              Processed: {stats.processedAt}
            </p>
          </div>
          <button
            onClick={() => navigate('/analyze')}
            className="shrink-0 inline-flex items-center gap-2 px-5 py-3 rounded-xl bg-white text-blue-700 text-sm font-bold shadow-md hover:shadow-lg hover:bg-blue-50 transition-all duration-200"
          >
            <FileText className="w-4 h-4" />
            Analyze New Document
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* KPI cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          label="AI Confidence"
          value={`${stats.aiConfidence}%`}
          icon={Brain}
          color="text-blue-600"
          subtitle="High confidence"
        />
        <StatCard
          label="Overall Risk"
          value={stats.risk}
          icon={ShieldAlert}
          color="text-orange-600"
          subtitle="Requires attention"
        />
        <StatCard
          label="Total Issues"
          value={stats.totalIssues}
          icon={AlertCircle}
          color="text-amber-600"
          subtitle="Across all categories"
        />
        <StatCard
          label="Critical Issues"
          value={stats.criticalIssues}
          icon={Zap}
          color="text-red-600"
          subtitle="Immediate action needed"
        />
      </div>

      {/* Compliance score + summary */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Compliance gauge */}
        <div className="lg:col-span-1 bg-white rounded-2xl border border-slate-200 p-6 shadow-sm flex flex-col items-center">
          <div className="flex items-center gap-2 mb-4 self-start">
            <ShieldAlert className="w-5 h-5 text-blue-600" />
            <h2 className="text-base font-bold text-slate-900">Compliance Score</h2>
          </div>
          <ComplianceGauge score={stats.complianceScore} />
          <div className="mt-6 grid grid-cols-3 gap-3 w-full">
            <div className="text-center">
              <p className="text-xl font-bold text-green-600">{passCount}</p>
              <p className="text-xs text-slate-500 font-medium">Pass</p>
            </div>
            <div className="text-center border-x border-slate-100">
              <p className="text-xl font-bold text-amber-500">{warnCount}</p>
              <p className="text-xs text-slate-500 font-medium">Warning</p>
            </div>
            <div className="text-center">
              <p className="text-xl font-bold text-red-500">{failCount}</p>
              <p className="text-xs text-slate-500 font-medium">Fail</p>
            </div>
          </div>
        </div>

        {/* Clause status */}
        <div className="lg:col-span-2 bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <FileText className="w-5 h-5 text-blue-600" />
              <h2 className="text-base font-bold text-slate-900">Clause Analysis</h2>
            </div>
            <button
              onClick={() => navigate('/compliance')}
              className="text-xs text-blue-600 hover:text-blue-700 font-semibold flex items-center gap-1"
            >
              View all <ChevronRight className="w-3.5 h-3.5" />
            </button>
          </div>
          <div className="space-y-2.5">
            {clauses.map((clause) => (
              <div
                key={clause.name}
                className="flex items-center justify-between py-2 px-3 rounded-xl hover:bg-slate-50 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <StatusIcon status={clause.status} />
                  <div>
                    <p className="text-sm font-semibold text-slate-800">{clause.name}</p>
                    <p className="text-xs text-slate-400">{clause.clause}</p>
                  </div>
                </div>
                <span
                  className={`text-xs font-bold px-2.5 py-0.5 rounded-full ${
                    clause.status === 'pass'
                      ? 'bg-green-50 text-green-700'
                      : clause.status === 'fail'
                      ? 'bg-red-50 text-red-700'
                      : 'bg-amber-50 text-amber-700'
                  }`}
                >
                  {clause.status.toUpperCase()}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Risk issues preview */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
        <div className="flex items-center justify-between mb-5">
          <div className="flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-blue-600" />
            <h2 className="text-base font-bold text-slate-900">Risk Issues — Prioritized</h2>
          </div>
          <button
            onClick={() => navigate('/risk')}
            className="text-xs text-blue-600 hover:text-blue-700 font-semibold flex items-center gap-1"
          >
            Full Risk Report <ChevronRight className="w-3.5 h-3.5" />
          </button>
        </div>
        <div className="space-y-3">
          {riskIssues.map((issue, idx) => (
            <div
              key={issue.id}
              className="flex items-start gap-4 p-4 rounded-xl border border-slate-100 hover:border-slate-200 hover:shadow-sm transition-all"
            >
              <div className="flex items-center justify-center w-7 h-7 rounded-full bg-slate-100 text-slate-500 text-xs font-bold shrink-0 mt-0.5">
                {idx + 1}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 flex-wrap">
                  <p className="text-sm font-semibold text-slate-900">{issue.title}</p>
                  <RiskBadge risk={issue.severity} />
                </div>
                <p className="text-xs text-slate-500 mt-1 leading-relaxed">{issue.impact}</p>
              </div>
              <span className="shrink-0 text-xs font-medium text-slate-400 bg-slate-50 px-2 py-1 rounded-lg">
                {issue.clause}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Quick action footer */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {[
          { label: 'View Compliance Report', icon: ShieldAlert, to: '/compliance', color: 'blue' },
          { label: 'Compare Versions', icon: TrendingUp, to: '/compare', color: 'violet' },
          { label: 'Download Report', icon: Lock, to: '/reports', color: 'emerald' },
        ].map(({ label, icon: Icon, to, color }) => (
          <button
            key={label}
            onClick={() => navigate(to)}
            className={`flex items-center justify-center gap-2 px-5 py-3.5 rounded-xl border-2 text-sm font-semibold transition-all duration-200 ${
              color === 'blue'
                ? 'border-blue-200 text-blue-700 hover:bg-blue-50'
                : color === 'violet'
                ? 'border-violet-200 text-violet-700 hover:bg-violet-50'
                : 'border-emerald-200 text-emerald-700 hover:bg-emerald-50'
            }`}
          >
            <Icon className="w-4 h-4" />
            {label}
          </button>
        ))}
      </div>
    </div>
  );
}
