import apiClient from './api.client';

export interface DashboardOverviewResponse {
  total_users: number;
  total_charging_sessions: number;
  total_feedback: number;
  total_complaints: number;
  average_feedback_rating: number;
  open_complaints: number;
  closed_complaints: number;
  total_energy_delivered: number;
  total_revenue: number;
  average_session_duration: number;
  users_change?: number;
  sessions_change?: number;
  feedback_change?: number;
  complaints_change?: number;
  revenue_change?: number;
  energy_change?: number;
}

export interface ChartDataset {
  label: string;
  data: number[];
}

export interface ChartResponse {
  labels: string[];
  datasets: ChartDataset[];
}

export interface FeedbackAnalyticsResponse {
  rating_distribution: ChartResponse;
  feedback_over_time: ChartResponse;
  category_distribution: ChartResponse;
  average_rating_trend: ChartResponse;
}

export interface ComplaintAnalyticsResponse {
  status_distribution: ChartResponse;
  category_distribution: ChartResponse;
  complaints_over_time: ChartResponse;
  workflow_status_distribution: ChartResponse;
}

export interface ChargerAnalyticsResponse {
  sessions: ChartResponse;
  ratings: ChartResponse;
  complaints: ChartResponse;
  energy: ChartResponse;
  revenue: ChartResponse;
}

export interface RecentActivityItem {
  type: string;
  id: string;
  title: string;
  description?: string;
  timestamp: string;
  status?: string;
}

export interface RecentActivityResponse {
  activities: RecentActivityItem[];
}

export const DashboardService = {
  async getOverview(params?: Record<string, string>): Promise<DashboardOverviewResponse> {
    const response = await apiClient.get('/dashboard/overview', { params });
    return response.data.data;
  },

  async getFeedbackAnalytics(params?: Record<string, string>): Promise<FeedbackAnalyticsResponse> {
    const response = await apiClient.get('/dashboard/feedback-analytics', { params });
    return response.data.data;
  },

  async getComplaintAnalytics(params?: Record<string, string>): Promise<ComplaintAnalyticsResponse> {
    const response = await apiClient.get('/dashboard/complaint-analytics', { params });
    return response.data.data;
  },

  async getUsageAnalytics(params?: Record<string, string>) {
    const response = await apiClient.get('/dashboard/usage-analytics', { params });
    return response.data.data;
  },

  async getChargerAnalytics(): Promise<ChargerAnalyticsResponse> {
    const response = await apiClient.get('/dashboard/charger-analytics');
    return response.data.data;
  },

  async getRecentActivity(params?: { limit: number }): Promise<RecentActivityResponse> {
    const response = await apiClient.get('/dashboard/recent-activity', { params });
    return response.data.data;
  },
};
