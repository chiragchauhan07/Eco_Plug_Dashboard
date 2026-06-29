import apiClient from './api.client';

export interface AnalyticsOverviewResponse {
  total_feedback: number;
  total_complaints: number;
  average_rating: number;
  complaint_rate: number;
  resolved_complaints: number;
  pending_complaints: number;
  resolution_percentage: number;
  average_response_time: number | null;
  active_users: number;
  total_sessions: number;
  energy_delivered: number;
  energy_saved: number;
}

export interface TrendDataset {
  label: string;
  data: number[];
}

export interface TrendResponse {
  labels: string[];
  datasets: TrendDataset[];
}

export interface CategoryDistributionItem {
  category: string;
  count: number;
  percentage: number;
}

export interface CategoryDistributionResponse {
  categories: CategoryDistributionItem[];
}

export interface SentimentDistributionItem {
  sentiment: string;
  count: number;
  percentage: number;
}

export interface SentimentDistributionResponse {
  distribution: SentimentDistributionItem[];
}

export interface TopIssueItem {
  issue: string;
  count: number;
}

export interface TopIssuesResponse {
  issues: TopIssueItem[];
}

export interface LocationInsightItem {
  location_name: string;
  complaint_count: number;
  average_rating: number;
  session_count: number;
}

export interface LocationInsightsResponse {
  most_complaints_by_location: LocationInsightItem[];
  highest_rated_locations: LocationInsightItem[];
  lowest_rated_locations: LocationInsightItem[];
  most_active_chargers: LocationInsightItem[];
}

export interface AIAnalyticsInsightsResponse {
  trends: string[];
  anomalies: string[];
  recommendations: string[];
}

export const AnalyticsService = {
  async getOverview(params?: Record<string, string>): Promise<AnalyticsOverviewResponse> {
    const response = await apiClient.get('/analytics/overview', { params });
    return response.data.data;
  },

  async getTrends(params?: Record<string, string>): Promise<TrendResponse> {
    const response = await apiClient.get('/analytics/trends', { params });
    return response.data.data;
  },

  async getCategories(params?: Record<string, string>): Promise<CategoryDistributionResponse> {
    const response = await apiClient.get('/analytics/categories', { params });
    return response.data.data;
  },

  async getSentiment(params?: Record<string, string>): Promise<SentimentDistributionResponse> {
    const response = await apiClient.get('/analytics/sentiment', { params });
    return response.data.data;
  },

  async getTopIssues(params?: Record<string, string>): Promise<TopIssuesResponse> {
    const response = await apiClient.get('/analytics/top-issues', { params });
    return response.data.data;
  },

  async getLocationInsights(): Promise<LocationInsightsResponse> {
    const response = await apiClient.get('/analytics/location-insights');
    return response.data.data;
  },

  async getAIInsights(params?: Record<string, string>): Promise<AIAnalyticsInsightsResponse> {
    const response = await apiClient.get('/analytics/ai-insights', { params });
    return response.data.data;
  },
};
