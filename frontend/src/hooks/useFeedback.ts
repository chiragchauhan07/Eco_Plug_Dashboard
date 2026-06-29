import { useState, useEffect, useCallback, useRef } from 'react';
import { FeedbackService } from '../services/feedback.service';
import { useDebounce } from './useDebounce';
import type { FeedbackListItem, FeedbackDetail } from '../services/feedback.service';

export interface FeedbackFilters {
  searchQuery: string;
  rating?: number;
  issueCategory?: string;
  dateRange?: string; // '7days', '30days', 'all'
}

export function useFeedback() {
  const [data, setData] = useState<FeedbackListItem[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [size, setSize] = useState(20);
  
  const [loadingList, setLoadingList] = useState(false);
  const [errorList, setErrorList] = useState<string | null>(null);

  const [filters, setFilters] = useState<FeedbackFilters>({
    searchQuery: '',
  });

  const debouncedSearch = useDebounce(filters.searchQuery, 400);

  const [selectedFeedbackId, setSelectedFeedbackId] = useState<string | null>(null);
  const [selectedFeedback, setSelectedFeedback] = useState<FeedbackDetail | null>(null);
  const [loadingDetail, setLoadingDetail] = useState(false);

  const [loadingAI, setLoadingAI] = useState(false);
  const [aiError, setAiError] = useState<string | null>(null);

  const abortControllerRef = useRef<AbortController | null>(null);

  const fetchList = useCallback(async () => {
    setLoadingList(true);
    setErrorList(null);
    try {
      const params: Record<string, any> = { page, size };
      if (debouncedSearch) {
        params.user_phone = debouncedSearch;
      }
      if (filters.rating) {
        params.rating = filters.rating;
      }
      if (filters.issueCategory) {
        params.issue_category = filters.issueCategory;
      }
      
      // Calculate dates if needed
      if (filters.dateRange === '30days') {
        const d = new Date();
        d.setDate(d.getDate() - 30);
        params.start_date = d.toISOString();
      }

      const res = await FeedbackService.listFeedback(params);
      setData(res.data.items);
      setTotal(res.data.pagination?.total_items ?? 0);
    } catch (err: any) {
      setErrorList(err.response?.data?.message || err.message || 'Failed to fetch feedback list');
    } finally {
      setLoadingList(false);
    }
  }, [page, size, debouncedSearch, filters.rating, filters.issueCategory, filters.dateRange]);

  useEffect(() => {
    fetchList();
  }, [fetchList]);

  // When filters or search or page change, clear selection
  useEffect(() => {
    setSelectedFeedbackId(null);
    setSelectedFeedback(null);
    setAiError(null);
  }, [debouncedSearch, filters.rating, filters.issueCategory, filters.dateRange, page]);

  // Fetch detail when ID changes
  useEffect(() => {
    if (!selectedFeedbackId) {
      setSelectedFeedback(null);
      setAiError(null);
      return;
    }

    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    const abortController = new AbortController();
    abortControllerRef.current = abortController;

    const fetchDetail = async () => {
      setLoadingDetail(true);
      setAiError(null);
      try {
        const detail = await FeedbackService.getFeedbackById(selectedFeedbackId, abortController.signal);
        setSelectedFeedback(detail);
      } catch (err: any) {
        if (err.name === 'CanceledError' || err.message === 'canceled') {
          // Ignore canceled request
        } else {
          console.error('Failed to fetch detail', err);
        }
      } finally {
        if (abortControllerRef.current === abortController) {
          setLoadingDetail(false);
        }
      }
    };

    fetchDetail();

    return () => {
      abortController.abort();
    };
  }, [selectedFeedbackId]);

  const analyzeFeedbackItem = async (force: boolean = false) => {
    if (!selectedFeedbackId) return;
    setLoadingAI(true);
    setAiError(null);
    try {
      const analysis = await FeedbackService.analyzeFeedback(selectedFeedbackId, force);
      setSelectedFeedback((prev) => {
        if (!prev) return null;
        return { ...prev, ai_analysis: analysis };
      });
      // Also update in list data so sentiment badge refreshes in the list row!
      setData((prevList) =>
        prevList.map((item) =>
          item.id === selectedFeedbackId ? { ...item, ai_analysis: analysis } : item
        )
      );
    } catch (err: any) {
      setAiError(err.response?.data?.detail || err.message || 'Failed to analyze feedback');
    } finally {
      setLoadingAI(false);
    }
  };

  return {
    data,
    total,
    page,
    setPage,
    size,
    setSize,
    loadingList,
    errorList,
    filters,
    setFilters,
    selectedFeedbackId,
    setSelectedFeedbackId,
    selectedFeedback,
    loadingDetail,
    loadingAI,
    aiError,
    analyzeFeedbackItem,
    refresh: fetchList,
  };
}
