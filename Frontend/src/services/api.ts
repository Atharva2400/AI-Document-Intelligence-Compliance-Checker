/**
 * API client service for AI Document Intelligence FastAPI backend.
 * Base URL defaults to http://127.0.0.1:8000
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

export interface ExtractedInfoItem {
  label: string;
  value: string;
  status: string;
}

export interface ClauseItem {
  name: string;
  status: string; // 'pass' | 'warning' | 'fail'
  clause: string;
  detail: string;
}

export interface ComplianceRuleItem {
  id: string;
  rule: string;
  category: string;
  status: string; // 'pass' | 'warning' | 'fail'
  severity: string; // 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW'
  evidence: string;
  recommendation: string;
}

export interface ClauseRef {
  id: string;
  title: string;
  text: string;
}

export interface ContradictionItem {
  id: string;
  title: string;
  confidence: number;
  risk: string;
  severity: string;
  clause1: ClauseRef;
  clause2: ClauseRef;
  evidence: string;
  impact: string;
  recommendation: string;
}

export interface RecommendationItem {
  priority: number;
  severity: string;
  title: string;
  action: string;
}

export interface AnalysisResponse {
  document_name: string;
  document_type: string;
  confidence: number;
  tags: string[];
  extracted_information: ExtractedInfoItem[];
  clauses: ClauseItem[];
  compliance_score: number;
  compliance_rules: ComplianceRuleItem[];
  contradictions: ContradictionItem[];
  risk_level: string;
  risk_score: number;
  total_issues: number;
  critical_issues: number;
  recommendations: RecommendationItem[];
  processing_time_ms: number;
  analyzed_at: string;
}

export interface HealthResponse {
  status: string;
  version: string;
  message: string;
}

/**
 * Health check GET /api/health
 */
export async function checkHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_BASE_URL}/api/health`);
  if (!response.ok) {
    throw new Error(`Health check failed with status ${response.status}`);
  }
  return response.json();
}

/**
 * Upload and analyze document POST /api/analyze
 */
export async function analyzeDocument(file: File): Promise<AnalysisResponse> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE_URL}/api/analyze`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    let errorMsg = `Analysis failed with status ${response.status}`;
    try {
      const errJson = await response.json();
      if (errJson.detail) {
        errorMsg = errJson.detail;
      } else if (errJson.error) {
        errorMsg = errJson.error;
      }
    } catch {
      // ignore json parse error
    }
    throw new Error(errorMsg);
  }

  return response.json();
}

/**
 * Get pre-built demo analysis GET /api/demo/{document_type}
 * document_type can be 'employment', 'nda', or 'vendor'
 */
export async function getDemoAnalysis(documentType: string): Promise<AnalysisResponse> {
  const response = await fetch(`${API_BASE_URL}/api/demo/${encodeURIComponent(documentType)}`);

  if (!response.ok) {
    let errorMsg = `Demo analysis failed with status ${response.status}`;
    try {
      const errJson = await response.json();
      if (errJson.detail) {
        errorMsg = errJson.detail;
      } else if (errJson.error) {
        errorMsg = errJson.error;
      }
    } catch {
      // ignore json parse error
    }
    throw new Error(errorMsg);
  }

  return response.json();
}
