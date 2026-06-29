import apiClient from './api.client';

export interface ExecutiveSummaryResponse {
  summary: string;
  key_metrics: string[];
  urgent_actions: string[];
}

export interface AnalyticsInsightsResponse {
  trends: string[];
  anomalies: string[];
  recommendations: string[];
}

export interface FeedbackAnalysisResponse {
  sentiment: string;
  key_themes: string[];
  suggested_response: string;
  urgency_level: string;
}

export interface ComplaintAnalysisResponse {
  root_cause: string;
  action_plan: string[];
  risk_assessment: string;
}

export interface ReportGenerationResponse {
  title: string;
  content: string;
}

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

export interface ChatResponse {
  reply: string;
}

export const AIService = {
  async getExecutiveSummary(): Promise<ExecutiveSummaryResponse> {
    const response = await apiClient.get('/ai/executive-summary');
    return response.data;
  },

  async getAnalyticsInsights(): Promise<AnalyticsInsightsResponse> {
    const response = await apiClient.get('/ai/analytics-insights');
    return response.data;
  },

  async analyzeFeedback(title: string, category: string, description: string): Promise<FeedbackAnalysisResponse> {
    const response = await apiClient.post('/ai/analyze-feedback', {
      title,
      category,
      description,
    });
    return response.data;
  },

  async analyzeComplaint(title: string, priority: string, status: string, description: string): Promise<ComplaintAnalysisResponse> {
    const response = await apiClient.post('/ai/analyze-complaint', {
      title,
      priority,
      status,
      description,
    });
    return response.data;
  },

  async generateReport(reportType: string, focusAreas: string[]): Promise<ReportGenerationResponse> {
    const response = await apiClient.post('/ai/generate-report', {
      report_type: reportType,
      focus_areas: focusAreas,
    });
    return response.data.data;
  },

  async chat(messages: ChatMessage[]): Promise<ChatResponse> {
    const response = await apiClient.post('/ai/chat', {
      messages,
    });
    return response.data.data;
  }
};
