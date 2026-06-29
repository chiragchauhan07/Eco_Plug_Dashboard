import { useState, useCallback, useEffect } from 'react';
import { AIService } from '../services/ai.service';
import type {
  ExecutiveSummaryResponse,
  AnalyticsInsightsResponse,
} from '../services/ai.service';

export function useAI() {
  const [executiveSummary, setExecutiveSummary] = useState<ExecutiveSummaryResponse | null>(null);
  const [isSummaryLoading, setIsSummaryLoading] = useState<boolean>(true);
  const [summaryError, setSummaryError] = useState<string | null>(null);

  const [analyticsInsights, setAnalyticsInsights] = useState<AnalyticsInsightsResponse | null>(null);
  const [isInsightsLoading, setIsInsightsLoading] = useState<boolean>(true);
  const [insightsError, setInsightsError] = useState<string | null>(null);

  const fetchExecutiveSummary = useCallback(async () => {
    setIsSummaryLoading(true);
    setSummaryError(null);
    try {
      const data = await AIService.getExecutiveSummary();
      setExecutiveSummary(data);
    } catch (err: any) {
      setSummaryError(err.response?.data?.message || err.message || 'Unable to generate AI summary.');
    } finally {
      setIsSummaryLoading(false);
    }
  }, []);

  const fetchAnalyticsInsights = useCallback(async () => {
    setIsInsightsLoading(true);
    setInsightsError(null);
    try {
      const data = await AIService.getAnalyticsInsights();
      setAnalyticsInsights(data);
    } catch (err: any) {
      setInsightsError(err.response?.data?.message || err.message || 'Unable to load AI insights.');
    } finally {
      setIsInsightsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchExecutiveSummary();
    fetchAnalyticsInsights();
  }, [fetchExecutiveSummary, fetchAnalyticsInsights]);

  return {
    executiveSummary,
    isSummaryLoading,
    summaryError,
    refreshExecutiveSummary: fetchExecutiveSummary,
    
    analyticsInsights,
    isInsightsLoading,
    insightsError,
    refreshAnalyticsInsights: fetchAnalyticsInsights,
  };
}
