import apiClient from './api.client';

export interface FeedbackAIAnalysis {
  sentiment: string;
  summary: string;
  category: string;
  priority: string;
  suggested_action: string;
  confidence_score: number;
  model_name?: string;
  model_version?: string;
  analyzed_at?: string;
}

export interface ChargingSession {
  id: string;
  session_code: string;
  energy_kwh?: number;
  duration_minutes?: number;
  amount_paid?: number;
  payment_status?: string;
  session_date?: string;
  connector_type: string;
  status?: string;
  start_time?: string;
  end_time?: string;
}

export interface FeedbackListItem {
  id: string;
  user_phone: string;
  user_name?: string;
  charger_name: string;
  rating: number;
  issue_category?: string;
  feedback_comment?: string;
  created_at?: string;
  ai_analysis?: FeedbackAIAnalysis;
}

export interface FeedbackDetail {
  id: string;
  user_phone: string;
  user_name?: string;
  session_id: string;
  charger_name: string;
  rating: number;
  feedback_comment?: string;
  created_at?: string;
  connector_name?: string;
  issue_category?: string;
  support_agent_contacted?: boolean;
  support_agent_phone?: string;
  support_agent_name?: string;
  charger_issue_type?: string;
  charging_session?: ChargingSession;
  ai_analysis?: FeedbackAIAnalysis;
}

export const FeedbackService = {
  async listFeedback(params?: Record<string, any>, signal?: AbortSignal) {
    const response = await apiClient.get('/feedback', { params, signal });
    return response.data;
  },

  async getFeedbackById(id: string, signal?: AbortSignal): Promise<FeedbackDetail> {
    const response = await apiClient.get(`/feedback/${id}`, { signal });
    return response.data.data;
  },

  async analyzeFeedback(id: string, force: boolean = false): Promise<FeedbackAIAnalysis> {
    const response = await apiClient.post(`/feedback/${id}/analyze`, null, { params: { force } });
    return response.data.data;
  },
};
