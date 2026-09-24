import React, { createContext, useContext, useState, useEffect } from 'react';
import {
  type AnalysisResponse,
  checkHealth,
} from '../services/api';
import {
  dashboardStats,
  extractedInfo,
  clauses,
  complianceRules,
  contradictions,
  riskIssues,
  reportFindings,
} from '../data/mockData';

export interface DerivedRiskIssue {
  id: string;
  title: string;
  severity: string;
  priority: number;
  category: string;
  impact: string;
  clause: string;
  recommendation: string;
  status: string;
}

export interface DerivedReportFinding {
  id: string;
  rule: string;
  evidence: string;
  result: string;
  risk: string;
  impact: string;
  recommendation: string;
  category: string;
}

interface AnalysisContextType {
  analysisData: AnalysisResponse | null;
  setAnalysisData: (data: AnalysisResponse | null) => void;
  isBackendConnected: boolean;
  backendError: string | null;
  checkBackendHealth: () => Promise<void>;
  // Derived data
  currentStats: {
    complianceScore: number;
    aiConfidence: number;
    risk: string;
    riskScore: number;
    totalIssues: number;
    criticalIssues: number;
    documentName: string;
    documentType: string;
    processedAt: string;
    pageCount: number;
    wordCount: number;
  };
  currentExtractedInfo: typeof extractedInfo;
  currentClauses: typeof clauses;
  currentComplianceRules: typeof complianceRules;
  currentContradictions: typeof contradictions;
  currentRiskIssues: DerivedRiskIssue[];
  currentReportFindings: DerivedReportFinding[];
  currentRecommendations: AnalysisResponse['recommendations'];
}

const AnalysisContext = createContext<AnalysisContextType | undefined>(undefined);

function deriveRiskIssues(data: AnalysisResponse): DerivedRiskIssue[] {
  if (!data || !data.recommendations || data.recommendations.length === 0) {
    return riskIssues;
  }
  return data.recommendations.map((rec, idx) => {
    const matchingRule = data.compliance_rules?.find(
      r => r.rule.toLowerCase().includes(rec.title.toLowerCase()) || r.severity === rec.severity
    );
    return {
      id: `RISK-00${idx + 1}`,
      title: rec.title,
      severity: rec.severity,
      priority: rec.priority,
      category: matchingRule ? matchingRule.category : 'Remediation',
      impact: rec.action,
      clause: matchingRule ? matchingRule.id : `Rec #${rec.priority}`,
      recommendation: rec.action,
      status: rec.severity === 'CRITICAL' || rec.severity === 'HIGH' ? 'Open' : 'Review',
    };
  });
}

function deriveReportFindings(data: AnalysisResponse): DerivedReportFinding[] {
  if (!data || !data.compliance_rules || data.compliance_rules.length === 0) {
    return reportFindings;
  }
  return data.compliance_rules.map((rule, idx) => ({
    id: rule.id || `RPT-00${idx + 1}`,
    rule: rule.rule,
    evidence: rule.evidence,
    result: rule.status ? rule.status.toUpperCase() : 'PASS',
    risk: rule.severity || 'LOW',
    impact: rule.evidence || rule.recommendation,
    recommendation: rule.recommendation,
    category: rule.category,
  }));
}

export const AnalysisProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [analysisData, setAnalysisData] = useState<AnalysisResponse | null>(null);
  const [isBackendConnected, setIsBackendConnected] = useState<boolean>(false);
  const [backendError, setBackendError] = useState<string | null>(null);

  const checkBackendHealth = async () => {
    try {
      await checkHealth();
      setIsBackendConnected(true);
      setBackendError(null);
    } catch (err: any) {
      setIsBackendConnected(false);
      setBackendError(err.message || 'Could not connect to backend server');
    }
  };

  useEffect(() => {
    checkBackendHealth();
  }, []);

  const currentStats = {
    complianceScore: analysisData ? analysisData.compliance_score : dashboardStats.complianceScore,
    aiConfidence: analysisData ? analysisData.confidence : dashboardStats.aiConfidence,
    risk: analysisData ? analysisData.risk_level : dashboardStats.risk,
    riskScore: analysisData ? analysisData.risk_score : 78,
    totalIssues: analysisData ? analysisData.total_issues : dashboardStats.totalIssues,
    criticalIssues: analysisData ? analysisData.critical_issues : dashboardStats.criticalIssues,
    documentName: analysisData ? analysisData.document_name : dashboardStats.documentName,
    documentType: analysisData ? analysisData.document_type : dashboardStats.documentType,
    processedAt: analysisData ? analysisData.analyzed_at : dashboardStats.processedAt,
    pageCount: dashboardStats.pageCount,
    wordCount: dashboardStats.wordCount,
  };

  const currentExtractedInfo = analysisData
    ? (analysisData.extracted_information as typeof extractedInfo)
    : extractedInfo;

  const currentClauses = analysisData
    ? (analysisData.clauses as typeof clauses)
    : clauses;

  const currentComplianceRules = analysisData
    ? (analysisData.compliance_rules as typeof complianceRules)
    : complianceRules;

  const currentContradictions = analysisData
    ? (analysisData.contradictions as typeof contradictions)
    : contradictions;

  const currentRiskIssues = analysisData ? deriveRiskIssues(analysisData) : riskIssues;
  const currentReportFindings = analysisData ? deriveReportFindings(analysisData) : reportFindings;

  return (
    <AnalysisContext.Provider
      value={{
        analysisData,
        setAnalysisData,
        isBackendConnected,
        backendError,
        checkBackendHealth,
        currentStats,
        currentExtractedInfo,
        currentClauses,
        currentComplianceRules,
        currentContradictions,
        currentRiskIssues,
        currentReportFindings,
        currentRecommendations: analysisData ? analysisData.recommendations : [],
      }}
    >
      {children}
    </AnalysisContext.Provider>
  );
};

export function useAnalysis() {
  const context = useContext(AnalysisContext);
  if (!context) {
    throw new Error('useAnalysis must be used within an AnalysisProvider');
  }
  return context;
}
