import { useState } from 'react';
import {
  FileBarChart2,
  Download,
  Printer,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  ChevronDown,
  ChevronUp,
  Brain,
  Shield,
  TrendingUp,
  FileText,
} from 'lucide-react';
import { useAnalysis } from '../context/AnalysisContext';

function ResultBadge({ result }: { result: string }) {
  const map: Record<string, string> = {
    PASS: 'bg-green-100 text-green-700 border-green-200',
    FAIL: 'bg-red-100 text-red-700 border-red-200',
    WARNING: 'bg-amber-100 text-amber-700 border-amber-200',
  };
  return (
    <span className={`inline-flex px-2.5 py-0.5 rounded-full text-xs font-bold border ${map[result] ?? 'bg-slate-100 text-slate-600'}`}>
      {result}
    </span>
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
    <span className={`inline-flex px-2.5 py-0.5 rounded-full text-xs font-bold border ${map[risk] ?? 'bg-slate-100 text-slate-600'}`}>
      {risk}
    </span>
  );
}

function ResultIcon({ result }: { result: string }) {
  if (result === 'PASS') return <CheckCircle2 className="w-5 h-5 text-green-500" />;
  if (result === 'FAIL') return <XCircle className="w-5 h-5 text-red-500" />;
  return <AlertTriangle className="w-5 h-5 text-amber-500" />;
}

export default function Reports() {
  const { currentStats: dashboardStats, currentReportFindings: reportFindings } = useAnalysis();

  const [expanded, setExpanded] = useState<string | null>(null);
  const [printed, setPrinted] = useState(false);
  const [downloaded, setDownloaded] = useState(false);

  const handlePrint = () => {
    setPrinted(true);
    setTimeout(() => setPrinted(false), 2000);
    window.print();
  };

  const handleDownload = () => {
    setDownloaded(true);
    setTimeout(() => setDownloaded(false), 2000);
    const blob = new Blob(
      [`AI Document Intelligence Report\n\nDocument: ${dashboardStats.documentName}\nGenerated: ${dashboardStats.processedAt}\n\nFindings:\n${reportFindings.map(f => `${f.id}: ${f.rule} — ${f.result}`).join('\n')}`],
      { type: 'text/plain' }
    );
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'compliance_report.txt';
    a.click();
    URL.revokeObjectURL(url);
  };

  const passCount = reportFindings.filter(f => f.result === 'PASS').length;
  const failCount = reportFindings.filter(f => f.result === 'FAIL').length;
  const warnCount = reportFindings.filter(f => f.result === 'WARNING').length;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8 print:px-0">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
            <FileBarChart2 className="w-7 h-7 text-blue-600" />
            Explainable Compliance Report
          </h1>
          <p className="text-slate-500 text-sm mt-1">
            {dashboardStats.documentName} · Generated {dashboardStats.processedAt}
          </p>
        </div>
        <div className="flex items-center gap-2 print:hidden">
          <button
            onClick={handlePrint}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-xl border border-slate-200 bg-white text-sm font-semibold text-slate-700 hover:bg-slate-50 shadow-sm transition-colors"
          >
            <Printer className="w-4 h-4" />
            {printed ? 'Printing...' : 'Print Report'}
          </button>
          <button
            onClick={handleDownload}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-blue-600 to-violet-600 text-white text-sm font-semibold shadow-md hover:shadow-lg transition-all"
          >
            <Download className="w-4 h-4" />
            {downloaded ? 'Downloading...' : 'Download Report'}
          </button>
        </div>
      </div>

      {/* Report meta banner */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-blue-700 to-violet-700 text-white p-6 shadow-xl">
        <div className="absolute top-0 right-0 opacity-10 p-4">
          <Brain className="w-32 h-32" />
        </div>
        <div className="relative z-10">
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-6">
            <div>
              <p className="text-xs font-semibold text-blue-200 uppercase tracking-wider">Document</p>
              <p className="text-sm font-bold mt-1">{dashboardStats.documentType}</p>
            </div>
            <div>
              <p className="text-xs font-semibold text-blue-200 uppercase tracking-wider">Compliance Score</p>
              <p className="text-2xl font-bold mt-1">{dashboardStats.complianceScore}/100</p>
            </div>
            <div>
              <p className="text-xs font-semibold text-blue-200 uppercase tracking-wider">Overall Risk</p>
              <p className="text-sm font-bold mt-1 text-orange-300">{dashboardStats.risk}</p>
            </div>
            <div>
              <p className="text-xs font-semibold text-blue-200 uppercase tracking-wider">AI Confidence</p>
              <p className="text-2xl font-bold mt-1">{dashboardStats.aiConfidence}%</p>
            </div>
          </div>
        </div>
      </div>

      {/* Summary */}
      <div className="grid grid-cols-3 gap-4">
        {[
          { label: 'Rules Passed', count: passCount, icon: CheckCircle2, color: 'green' },
          { label: 'Warnings', count: warnCount, icon: AlertTriangle, color: 'amber' },
          { label: 'Rules Failed', count: failCount, icon: XCircle, color: 'red' },
        ].map(({ label, count, icon: Icon, color }) => (
          <div key={label} className={`bg-white rounded-2xl border p-5 text-center shadow-sm ${
            color === 'green' ? 'border-green-200' : color === 'amber' ? 'border-amber-200' : 'border-red-200'
          }`}>
            <Icon className={`w-6 h-6 mx-auto mb-2 ${
              color === 'green' ? 'text-green-500' : color === 'amber' ? 'text-amber-500' : 'text-red-500'
            }`} />
            <p className={`text-3xl font-bold ${
              color === 'green' ? 'text-green-600' : color === 'amber' ? 'text-amber-600' : 'text-red-600'
            }`}>{count}</p>
            <p className="text-xs text-slate-500 font-semibold mt-1">{label}</p>
          </div>
        ))}
      </div>

      {/* Findings */}
      <div>
        <h2 className="text-xl font-bold text-slate-900 mb-4 flex items-center gap-2">
          <Shield className="w-5 h-5 text-blue-600" />
          Detailed Findings
        </h2>
        <div className="space-y-3">
          {reportFindings.map((finding) => (
            <div
              key={finding.id}
              className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden hover:shadow-md transition-shadow"
            >
              {/* Header row */}
              <div
                className="flex items-center justify-between gap-3 px-5 py-4 cursor-pointer hover:bg-slate-50 transition-colors"
                onClick={() => setExpanded(expanded === finding.id ? null : finding.id)}
              >
                <div className="flex items-center gap-3 flex-1 min-w-0 flex-wrap">
                  <ResultIcon result={finding.result} />
                  <div className="min-w-0">
                    <p className="text-sm font-bold text-slate-900 truncate">{finding.rule}</p>
                    <div className="flex items-center gap-2 mt-0.5">
                      <span className="text-xs text-slate-400">{finding.id}</span>
                      <span className="text-xs text-slate-300">·</span>
                      <span className="text-xs font-medium text-slate-500 bg-slate-100 px-1.5 py-0.5 rounded">{finding.category}</span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  <ResultBadge result={finding.result} />
                  <RiskBadge risk={finding.risk} />
                  {expanded === finding.id ? (
                    <ChevronUp className="w-4 h-4 text-slate-400" />
                  ) : (
                    <ChevronDown className="w-4 h-4 text-slate-400" />
                  )}
                </div>
              </div>

              {/* Expanded detail */}
              {expanded === finding.id && (
                <div className="border-t border-slate-100 px-5 py-4 bg-slate-50">
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                    {[
                      { label: 'Rule', value: finding.rule, icon: FileText, colorClass: 'border-blue-200 bg-blue-50' },
                      { label: 'Evidence', value: `"${finding.evidence}"`, icon: TrendingUp, colorClass: 'border-slate-200 bg-white font-mono text-xs' },
                      { label: 'Impact', value: finding.impact, icon: AlertTriangle, colorClass: 'border-orange-200 bg-orange-50' },
                      { label: 'Recommendation', value: finding.recommendation, icon: CheckCircle2, colorClass: 'border-green-200 bg-green-50' },
                    ].map(({ label, value, icon: Icon, colorClass }) => (
                      <div key={label} className={`p-3 rounded-xl border ${colorClass}`}>
                        <div className="flex items-center gap-1.5 mb-1.5">
                          <Icon className="w-3.5 h-3.5 text-slate-400" />
                          <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">{label}</p>
                        </div>
                        <p className="text-xs text-slate-700 leading-relaxed">{value}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Footer note */}
      <div className="bg-slate-100 rounded-2xl p-5 text-center text-xs text-slate-400 leading-relaxed">
        <p>
          This report was generated by <strong className="text-slate-600">AI Document Intelligence</strong> using API analysis.
          <br />
          <span className="text-slate-400">AI Confidence: {dashboardStats.aiConfidence}% · Generated: {dashboardStats.processedAt}</span>
        </p>
      </div>
    </div>
  );
}
