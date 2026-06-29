import { useState, useEffect, useCallback } from 'react';
import { AnalyticsService } from '../services/analytics.service';
import type {
  AnalyticsOverviewResponse,
  TrendResponse,
  CategoryDistributionResponse,
  SentimentDistributionResponse,
  TopIssuesResponse,
  LocationInsightsResponse,
  AIAnalyticsInsightsResponse,
} from '../services/analytics.service';

export function useAnalytics(
  timeFilter: string,
  startDate?: string,
  endDate?: string
) {
  const [overview, setOverview] = useState<{ data: AnalyticsOverviewResponse | null; isLoading: boolean; error: string | null }>({
    data: null,
    isLoading: true,
    error: null,
  });

  const [trends, setTrends] = useState<{ data: TrendResponse | null; isLoading: boolean; error: string | null }>({
    data: null,
    isLoading: true,
    error: null,
  });

  const [categories, setCategories] = useState<{ data: CategoryDistributionResponse | null; isLoading: boolean; error: string | null }>({
    data: null,
    isLoading: true,
    error: null,
  });

  const [sentiment, setSentiment] = useState<{ data: SentimentDistributionResponse | null; isLoading: boolean; error: string | null }>({
    data: null,
    isLoading: true,
    error: null,
  });

  const [topIssues, setTopIssues] = useState<{ data: TopIssuesResponse | null; isLoading: boolean; error: string | null }>({
    data: null,
    isLoading: true,
    error: null,
  });

  const [locations, setLocations] = useState<{ data: LocationInsightsResponse | null; isLoading: boolean; error: string | null }>({
    data: null,
    isLoading: true,
    error: null,
  });

  const [aiInsights, setAiInsights] = useState<{ data: AIAnalyticsInsightsResponse | null; isLoading: boolean; error: string | null }>({
    data: null,
    isLoading: true,
    error: null,
  });

  const getParams = useCallback(() => {
    const params: Record<string, string> = { time_range: timeFilter };
    if (timeFilter === 'custom') {
      if (startDate) params.start_date = startDate;
      if (endDate) params.end_date = endDate;
    }
    return params;
  }, [timeFilter, startDate, endDate]);

  const fetchOverview = useCallback(async () => {
    setOverview((prev) => ({ ...prev, isLoading: true, error: null }));
    try {
      const data = await AnalyticsService.getOverview(getParams());
      setOverview({ data, isLoading: false, error: null });
    } catch (err: any) {
      setOverview({
        data: null,
        isLoading: false,
        error: err.response?.data?.detail || err.message || 'Failed to load overview',
      });
    }
  }, [getParams]);

  const fetchTrends = useCallback(async () => {
    setTrends((prev) => ({ ...prev, isLoading: true, error: null }));
    try {
      const data = await AnalyticsService.getTrends(getParams());
      setTrends({ data, isLoading: false, error: null });
    } catch (err: any) {
      setTrends({
        data: null,
        isLoading: false,
        error: err.response?.data?.detail || err.message || 'Failed to load trends',
      });
    }
  }, [getParams]);

  const fetchCategories = useCallback(async () => {
    setCategories((prev) => ({ ...prev, isLoading: true, error: null }));
    try {
      const data = await AnalyticsService.getCategories(getParams());
      setCategories({ data, isLoading: false, error: null });
    } catch (err: any) {
      setCategories({
        data: null,
        isLoading: false,
        error: err.response?.data?.detail || err.message || 'Failed to load categories',
      });
    }
  }, [getParams]);

  const fetchSentiment = useCallback(async () => {
    setSentiment((prev) => ({ ...prev, isLoading: true, error: null }));
    try {
      const data = await AnalyticsService.getSentiment(getParams());
      setSentiment({ data, isLoading: false, error: null });
    } catch (err: any) {
      setSentiment({
        data: null,
        isLoading: false,
        error: err.response?.data?.detail || err.message || 'Failed to load sentiment',
      });
    }
  }, [getParams]);

  const fetchTopIssues = useCallback(async () => {
    setTopIssues((prev) => ({ ...prev, isLoading: true, error: null }));
    try {
      const data = await AnalyticsService.getTopIssues(getParams());
      setTopIssues({ data, isLoading: false, error: null });
    } catch (err: any) {
      setTopIssues({
        data: null,
        isLoading: false,
        error: err.response?.data?.detail || err.message || 'Failed to load top issues',
      });
    }
  }, [getParams]);

  const fetchLocations = useCallback(async () => {
    setLocations((prev) => ({ ...prev, isLoading: true, error: null }));
    try {
      const data = await AnalyticsService.getLocationInsights();
      setLocations({ data, isLoading: false, error: null });
    } catch (err: any) {
      setLocations({
        data: null,
        isLoading: false,
        error: err.response?.data?.detail || err.message || 'Failed to load location insights',
      });
    }
  }, []);

  const fetchAiInsights = useCallback(async () => {
    setAiInsights((prev) => ({ ...prev, isLoading: true, error: null }));
    try {
      const data = await AnalyticsService.getAIInsights(getParams());
      setAiInsights({ data, isLoading: false, error: null });
    } catch (err: any) {
      setAiInsights({
        data: null,
        isLoading: false,
        error: err.response?.data?.detail || err.message || 'Failed to load AI insights',
      });
    }
  }, [getParams]);

  const refetchAll = useCallback(() => {
    fetchOverview();
    fetchTrends();
    fetchCategories();
    fetchSentiment();
    fetchTopIssues();
    fetchLocations();
    fetchAiInsights();
  }, [
    fetchOverview,
    fetchTrends,
    fetchCategories,
    fetchSentiment,
    fetchTopIssues,
    fetchLocations,
    fetchAiInsights,
  ]);

  useEffect(() => {
    refetchAll();
  }, [refetchAll]);

  return {
    overview: { ...overview, refetch: fetchOverview },
    trends: { ...trends, refetch: fetchTrends },
    categories: { ...categories, refetch: fetchCategories },
    sentiment: { ...sentiment, refetch: fetchSentiment },
    topIssues: { ...topIssues, refetch: fetchTopIssues },
    locations: { ...locations, refetch: fetchLocations },
    aiInsights: { ...aiInsights, refetch: fetchAiInsights },
    refetchAll,
  };
}
