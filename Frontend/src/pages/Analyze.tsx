import { useState, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Upload,
  FileText,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  ChevronRight,
  Brain,
  Loader2,
  FileCheck2,
  Sparkles,
  BarChart3,
  Shield,
  Tag,
  User,
  Building,
  Calendar,
  DollarSign,
  Clock,
  Briefcase,
} from 'lucide-react';
import { analysisSteps } from '../data/mockData';
import { useAnalysis } from '../context/AnalysisContext';
import { analyzeDocument, getDemoAnalysis } from '../services/api';

interface Props {
  analysisComplete: boolean;
  setAnalysisComplete: (v: boolean) => void;
}

type AnalysisState = 'idle' | 'running' | 'done';

function StatusIcon({ status }: { status: string }) {
  if (status === 'pass') return <CheckCircle2 className="w-4 h-4 text-green-500" />;
  if (status === 'fail') return <XCircle className="w-4 h-4 text-red-500" />;
  return <AlertTriangle className="w-4 h-4 text-amber-500" />;
}

const infoIcons: Record<string, React.ElementType> = {
  'Employee Name': User,
  'Company Name': Building,
  'Role / Designation': Briefcase,
  'Joining Date': Calendar,
  'Annual Salary (CTC)': DollarSign,
  'Notice Period': Clock,
  'Contract Duration': FileText,
  'Probation Period': Clock,
  'Work Location': Tag,
  'Governing Law': Shield,
};

const demoDocs = [
  {
    name: 'Employment Agreement',
    fileName: 'Employment_Agreement_v2.pdf',
    type: 'employment',
    icon: '📋',
    pages: 12,
    size: '284 KB',
  },
  {
    name: 'Non-Disclosure Agreement',
    fileName: 'NDA_TechCorp_2026.pdf',
    type: 'nda',
    icon: '🔒',
    pages: 5,
    size: '118 KB',
  },
  {
    name: 'Vendor Agreement',
    fileName: 'Vendor_Agreement_Q3.pdf',
    type: 'vendor',
    icon: '🤝',
    pages: 18,
    size: '492 KB',
  },
];

export default function Analyze({ analysisComplete, setAnalysisComplete }: Props) {
  const navigate = useNavigate();
  const { setAnalysisData, currentStats, currentExtractedInfo, currentClauses, analysisData } = useAnalysis();

  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const [selectedFileObj, setSelectedFileObj] = useState<File | null>(null);
  const [selectedDemoType, setSelectedDemoType] = useState<string | null>(null);

  const [dragging, setDragging] = useState(false);
  const [analysisState, setAnalysisState] = useState<AnalysisState>(
    analysisComplete ? 'done' : 'idle'
  );
  const [currentStep, setCurrentStep] = useState(0);
  const [completedSteps, setCompletedSteps] = useState<number[]>([]);
  const [apiError, setApiError] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragging(true);
  }, []);

  const handleDragLeave = useCallback(() => setDragging(false), []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) {
      setSelectedFile(file.name);
      setSelectedFileObj(file);
      setSelectedDemoType(null);
      setApiError(null);
    }
  }, []);

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file.name);
      setSelectedFileObj(file);
      setSelectedDemoType(null);
      setApiError(null);
    }
  };

  const handleSelectDemo = (doc: typeof demoDocs[0]) => {
    setSelectedFile(doc.fileName);
    setSelectedDemoType(doc.type);
    setSelectedFileObj(null);
    setApiError(null);
  };

  const runAnalysis = async () => {
    if (!selectedFile) return;

    setAnalysisState('running');
    setCompletedSteps([]);
    setCurrentStep(1);
    setApiError(null);

    let progressTimer: any;
    let stepIndex = 0;

    progressTimer = setInterval(() => {
      stepIndex++;
      if (stepIndex < analysisSteps.length) {
        setCurrentStep(stepIndex + 1);
        setCompletedSteps((prev) => [...prev, stepIndex]);
      }
    }, 400);

    try {
      let result;
      if (selectedFileObj) {
        // Send file to POST /api/analyze using FormData
        result = await analyzeDocument(selectedFileObj);
      } else if (selectedDemoType) {
        // GET /api/demo/{document_type}
        result = await getDemoAnalysis(selectedDemoType);
      } else {
        // Fallback for filename match
        const matched = demoDocs.find(d => d.fileName === selectedFile);
        result = await getDemoAnalysis(matched ? matched.type : 'employment');
      }

      clearInterval(progressTimer);

      // Complete all steps visually
      setCompletedSteps(analysisSteps.map(s => s.id));
      setCurrentStep(analysisSteps.length);

      // Save backend response in context
      setAnalysisData(result);
      setAnalysisState('done');
      setAnalysisComplete(true);
    } catch (err: any) {
      clearInterval(progressTimer);
      setAnalysisState('idle');
      setApiError(err.message || 'Failed to analyze document. Please ensure the backend is running at http://127.0.0.1:8000.');
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Page header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Document Analyzer</h1>
        <p className="text-slate-500 text-sm mt-1">
          Upload a document and let AI extract, classify, and analyze it for compliance and risk.
        </p>
      </div>

      {/* API Error Notification */}
      {apiError && (
        <div className="p-4 rounded-xl bg-red-50 border border-red-200 text-red-700 flex items-start justify-between gap-3 shadow-sm">
          <div className="flex items-start gap-2.5">
            <AlertTriangle className="w-5 h-5 text-red-500 shrink-0 mt-0.5" />
            <div>
              <p className="text-sm font-bold text-red-800">API Error</p>
              <p className="text-xs text-red-600 mt-0.5">{apiError}</p>
            </div>
          </div>
          <button
            onClick={() => setApiError(null)}
            className="text-xs text-red-500 hover:text-red-700 font-bold px-2 py-1 rounded hover:bg-red-100"
          >
            Dismiss
          </button>
        </div>
      )}

      {analysisState !== 'done' && (
        <>
          {/* Upload area */}
          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            className={`relative border-2 border-dashed rounded-2xl p-12 text-center transition-all duration-200 cursor-pointer ${
              dragging
                ? 'border-blue-500 bg-blue-50'
                : selectedFile
                ? 'border-green-400 bg-green-50'
                : 'border-slate-300 bg-white hover:border-blue-400 hover:bg-slate-50'
            }`}
            onClick={() => fileInputRef.current?.click()}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.docx,.txt"
              className="hidden"
              onChange={handleFileInput}
            />
            <div className="flex flex-col items-center gap-4">
              {selectedFile ? (
                <>
                  <div className="w-16 h-16 rounded-full bg-green-100 flex items-center justify-center">
                    <FileCheck2 className="w-8 h-8 text-green-600" />
                  </div>
                  <div>
                    <p className="text-base font-bold text-green-700">{selectedFile}</p>
                    <p className="text-sm text-green-600 mt-1">
                      {selectedFileObj ? 'File ready for upload & analysis' : 'Demo document selected'}
                    </p>
                  </div>
                  <button
                    className="text-xs text-slate-400 hover:text-slate-600 underline"
                    onClick={(e) => {
                      e.stopPropagation();
                      setSelectedFile(null);
                      setSelectedFileObj(null);
                      setSelectedDemoType(null);
                    }}
                  >
                    Choose a different file
                  </button>
                </>
              ) : (
                <>
                  <div className="w-16 h-16 rounded-full bg-blue-50 flex items-center justify-center">
                    <Upload className="w-8 h-8 text-blue-500" />
                  </div>
                  <div>
                    <p className="text-base font-semibold text-slate-700">
                      Drag & drop your document here
                    </p>
                    <p className="text-sm text-slate-400 mt-1">
                      Supports PDF, DOCX, TXT — up to 50 MB
                    </p>
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      fileInputRef.current?.click();
                    }}
                    className="px-5 py-2.5 rounded-xl bg-blue-600 text-white text-sm font-semibold hover:bg-blue-700 transition-colors shadow-sm"
                  >
                    Choose File
                  </button>
                </>
              )}
            </div>
          </div>

          {/* Demo documents */}
          <div>
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">
              Or try a demo document
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              {demoDocs.map((doc) => (
                <button
                  key={doc.name}
                  onClick={() => handleSelectDemo(doc)}
                  className={`text-left p-4 rounded-xl border-2 transition-all duration-150 hover:shadow-md ${
                    selectedFile === doc.fileName
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-slate-200 bg-white hover:border-blue-300'
                  }`}
                >
                  <div className="text-2xl mb-2">{doc.icon}</div>
                  <p className="text-sm font-bold text-slate-900">{doc.name}</p>
                  <p className="text-xs text-slate-400 mt-0.5">{doc.fileName}</p>
                  <div className="flex items-center gap-3 mt-2 text-xs text-slate-400">
                    <span>{doc.pages} pages</span>
                    <span>·</span>
                    <span>{doc.size}</span>
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Analyze button */}
          <div className="flex items-center gap-4">
            <button
              disabled={!selectedFile || analysisState === 'running'}
              onClick={runAnalysis}
              className="inline-flex items-center gap-2 px-8 py-3.5 rounded-xl bg-gradient-to-r from-blue-600 to-violet-600 text-white text-sm font-bold shadow-md hover:shadow-xl hover:from-blue-700 hover:to-violet-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
            >
              {analysisState === 'running' ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Brain className="w-4 h-4" />
              )}
              {analysisState === 'running' ? 'Analyzing...' : 'Analyze Document'}
            </button>
            {!selectedFile && (
              <p className="text-xs text-slate-400">Select a file or demo document to continue</p>
            )}
          </div>
        </>
      )}

      {/* Analysis progress */}
      {analysisState === 'running' && (
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
          <div className="flex items-center gap-2 mb-6">
            <Sparkles className="w-5 h-5 text-blue-600 animate-pulse" />
            <h2 className="text-base font-bold text-slate-900">AI Analysis in Progress</h2>
          </div>
          <div className="space-y-3">
            {analysisSteps.map((step) => {
              const done = completedSteps.includes(step.id);
              const active = currentStep === step.id && !done;
              return (
                <div
                  key={step.id}
                  className={`flex items-center gap-3 p-3 rounded-xl transition-all ${
                    done
                      ? 'bg-green-50'
                      : active
                      ? 'bg-blue-50 border border-blue-200'
                      : 'bg-slate-50 opacity-50'
                  }`}
                >
                  <div className="shrink-0">
                    {done ? (
                      <CheckCircle2 className="w-5 h-5 text-green-500" />
                    ) : active ? (
                      <Loader2 className="w-5 h-5 text-blue-600 animate-spin" />
                    ) : (
                      <div className="w-5 h-5 rounded-full border-2 border-slate-300" />
                    )}
                  </div>
                  <div className="flex-1">
                    <p
                      className={`text-sm font-semibold ${
                        done ? 'text-green-700' : active ? 'text-blue-700' : 'text-slate-500'
                      }`}
                    >
                      Step {step.id}: {step.label}
                    </p>
                  </div>
                  {done && <span className="text-xs text-green-600 font-medium">Done</span>}
                  {active && (
                    <span className="text-xs text-blue-600 font-medium animate-pulse">
                      Processing...
                    </span>
                  )}
                </div>
              );
            })}
          </div>
          {/* Progress bar */}
          <div className="mt-5">
            <div className="flex items-center justify-between text-xs text-slate-500 mb-1.5">
              <span>Overall Progress</span>
              <span>{Math.round((completedSteps.length / analysisSteps.length) * 100)}%</span>
            </div>
            <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-blue-500 to-violet-500 rounded-full transition-all duration-500"
                style={{ width: `${(completedSteps.length / analysisSteps.length) * 100}%` }}
              />
            </div>
          </div>
        </div>
      )}

      {/* Analysis Results */}
      {analysisState === 'done' && (
        <div className="space-y-6">
          {/* Re-analyze option */}
          <div className="flex items-center justify-between">
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-green-50 border border-green-200 text-sm font-semibold text-green-700">
              <CheckCircle2 className="w-4 h-4" />
              Analysis Complete — {currentStats.documentName}
            </div>
            <button
              onClick={() => {
                setAnalysisState('idle');
                setSelectedFile(null);
                setSelectedFileObj(null);
                setSelectedDemoType(null);
                setAnalysisComplete(false);
              }}
              className="text-xs text-slate-500 hover:text-slate-700 font-medium underline"
            >
              Analyze another document
            </button>
          </div>

          {/* Document Classification */}
          <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
            <div className="flex items-center gap-2 mb-4">
              <Tag className="w-5 h-5 text-blue-600" />
              <h2 className="text-base font-bold text-slate-900">Document Classification</h2>
            </div>
            <div className="flex flex-wrap items-center gap-4">
              <div>
                <p className="text-2xl font-bold text-slate-900">{currentStats.documentType}</p>
                <p className="text-sm text-slate-500 mt-0.5">
                  {currentStats.documentName} · AI Processed
                </p>
              </div>
              <div className="flex items-center gap-2 ml-auto">
                <div className="flex flex-col items-end">
                  <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                    AI Confidence
                  </p>
                  <p className="text-3xl font-bold text-blue-600">{currentStats.aiConfidence}%</p>
                </div>
                <Brain className="w-8 h-8 text-blue-200" />
              </div>
            </div>
            <div className="mt-4 flex flex-wrap gap-2">
              {(analysisData?.tags || ['Legal Document', 'Analyzed', 'Automated Check']).map((tag) => (
                <span
                  key={tag}
                  className="px-2.5 py-1 rounded-full bg-blue-50 text-blue-700 text-xs font-semibold border border-blue-100"
                >
                  {tag}
                </span>
              ))}
            </div>
          </div>

          {/* Extracted Information */}
          <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
            <div className="flex items-center gap-2 mb-4">
              <FileCheck2 className="w-5 h-5 text-blue-600" />
              <h2 className="text-base font-bold text-slate-900">Extracted Information</h2>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {currentExtractedInfo.map((info) => {
                const Icon = infoIcons[info.label] || FileText;
                return (
                  <div key={info.label} className="flex items-center gap-3 p-3 rounded-xl bg-slate-50">
                    <div className="w-8 h-8 rounded-lg bg-white shadow-sm flex items-center justify-center shrink-0">
                      <Icon className="w-4 h-4 text-blue-500" />
                    </div>
                    <div>
                      <p className="text-xs font-medium text-slate-400">{info.label}</p>
                      <p className="text-sm font-bold text-slate-900">{info.value}</p>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Clause Analysis */}
          <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
            <div className="flex items-center gap-2 mb-4">
              <BarChart3 className="w-5 h-5 text-blue-600" />
              <h2 className="text-base font-bold text-slate-900">Clause Analysis</h2>
            </div>
            <div className="space-y-2">
              {currentClauses.map((clause) => (
                <div
                  key={clause.name}
                  className={`flex items-start gap-3 p-3.5 rounded-xl border transition-colors ${
                    clause.status === 'pass'
                      ? 'border-green-100 bg-green-50/50'
                      : clause.status === 'fail'
                      ? 'border-red-100 bg-red-50/50'
                      : 'border-amber-100 bg-amber-50/50'
                  }`}
                >
                  <StatusIcon status={clause.status} />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between gap-2 flex-wrap">
                      <p className="text-sm font-semibold text-slate-800">{clause.name}</p>
                      <span className="text-xs text-slate-400 font-mono">{clause.clause}</span>
                    </div>
                    <p className="text-xs text-slate-500 mt-0.5 leading-relaxed">{clause.detail}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* CTA to compliance / risk */}
          <div className="flex flex-wrap gap-3">
            <button
              onClick={() => navigate('/compliance')}
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-violet-600 text-white text-sm font-bold shadow-md hover:shadow-lg transition-all"
            >
              <Shield className="w-4 h-4" />
              View Compliance Rules
              <ChevronRight className="w-4 h-4" />
            </button>
            <button
              onClick={() => navigate('/risk')}
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl border-2 border-orange-200 text-orange-700 text-sm font-bold hover:bg-orange-50 transition-colors"
            >
              View Risk Analysis
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
