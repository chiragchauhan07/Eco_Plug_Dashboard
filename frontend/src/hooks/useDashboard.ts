import { useState, useEffect } from 'react';
import { DashboardService } from '../services/dashboard.service';
import type {
  DashboardOverviewResponse,
  FeedbackAnalyticsResponse,
  ComplaintAnalyticsResponse,
  ChargerAnalyticsResponse,
  RecentActivityResponse
} from '../services/dashboard.service';

export interface DashboardData {
  overview: DashboardOverviewResponse | null;
  feedbackAnalytics: FeedbackAnalyticsResponse | null;
  complaintAnalytics: ComplaintAnalyticsResponse | null;
  chargerAnalytics: ChargerAnalyticsResponse | null;
  recentActivity: RecentActivityResponse | null;
}

export function useDashboard() {
  const [data, setData] = useState<DashboardData>({
    overview: null,
    feedbackAnalytics: null,
    complaintAnalytics: null,
    chargerAnalytics: null,
    recentActivity: null,
  });
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchDashboardData() {
      setIsLoading(true);
      setError(null);
      try {
        const [
          overview,
          feedbackAnalytics,
          complaintAnalytics,
          chargerAnalytics,
          recentActivity
        ] = await Promise.all([
          DashboardService.getOverview(),
          DashboardService.getFeedbackAnalytics(),
          DashboardService.getComplaintAnalytics(),
          DashboardService.getChargerAnalytics(),
          DashboardService.getRecentActivity({ limit: 5 })
        ]);

        setData({
          overview,
          feedbackAnalytics,
          complaintAnalytics,
          chargerAnalytics,
          recentActivity
        });
      } catch (err: any) {
        setError(err.response?.data?.message || err.message || 'Failed to load dashboard data');
      } finally {
        setIsLoading(false);
      }
    }

    fetchDashboardData();
  }, []);

  return { ...data, isLoading, error };
}
