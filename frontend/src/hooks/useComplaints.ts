import { useState, useEffect, useCallback, useRef } from 'react';
import { ComplaintsService } from '../services/complaints.service';
import { useDebounce } from './useDebounce';

export interface ComplaintFilters {
  searchQuery: string;
  status?: string;
  priority?: string;
  dateRange?: string; // '7days', '30days', 'all'
}

export function useComplaints() {
  const [data, setData] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [size, setSize] = useState(20);
  
  const [loadingList, setLoadingList] = useState(false);
  const [errorList, setErrorList] = useState<string | null>(null);

  const [filters, setFilters] = useState<ComplaintFilters>({
    searchQuery: '',
  });

  const debouncedSearch = useDebounce(filters.searchQuery, 400);

  const [selectedComplaintId, setSelectedComplaintId] = useState<string | null>(null);
  const [selectedComplaint, setSelectedComplaint] = useState<any | null>(null);
  const [loadingDetail, setLoadingDetail] = useState(false);
  
  const [admins, setAdmins] = useState<any[]>([]);
  
  // Unsaved changes state
  const [internalNotes, setInternalNotes] = useState<string>('');
  const [hasUnsavedNotes, setHasUnsavedNotes] = useState(false);
  const [isSavingWorkflow, setIsSavingWorkflow] = useState(false);
  const [workflowError, setWorkflowError] = useState<string | null>(null);
  const [workflowSuccess, setWorkflowSuccess] = useState<boolean>(false);

  // Dialog states
  const [showUnsavedDialog, setShowUnsavedDialog] = useState(false);
  const [pendingComplaintId, setPendingComplaintId] = useState<string | null>(null);
  const [showCloseConfirmDialog, setShowCloseConfirmDialog] = useState(false);
  const [pendingStatusChange, setPendingStatusChange] = useState<string | null>(null);

  const listAbortControllerRef = useRef<AbortController | null>(null);
  const detailAbortControllerRef = useRef<AbortController | null>(null);

  // Fetch admins
  useEffect(() => {
    const fetchAdmins = async () => {
      try {
        const adminData = await ComplaintsService.getAdmins();
        setAdmins(adminData);
      } catch (err) {
        console.error('Failed to fetch admins', err);
      }
    };
    fetchAdmins();
  }, []);

  const fetchList = useCallback(async () => {
    setLoadingList(true);
    setErrorList(null);
    
    if (listAbortControllerRef.current) {
      listAbortControllerRef.current.abort();
    }
    const abortController = new AbortController();
    listAbortControllerRef.current = abortController;

    try {
      const params: Record<string, any> = { page, size };
      if (debouncedSearch) {
        params.ticket_id = debouncedSearch; // Search by ticket ID
      }
      if (filters.status) {
        params.status = filters.status; // Filter by status
      }
      if (filters.priority) {
        params.internal_status = filters.priority; // Placeholder logic
      }
      
      if (filters.dateRange === '30days') {
        const d = new Date();
        d.setDate(d.getDate() - 30);
        params.start_date = d.toISOString();
      }

      const res = await ComplaintsService.listComplaints(params, abortController.signal);
      setData(res.data.items);
      setTotal(res.data.pagination?.total_items ?? 0);
    } catch (err: any) {
      if (err.name !== 'CanceledError' && err.message !== 'canceled') {
        setErrorList(err.response?.data?.message || err.message || 'Failed to fetch complaints list');
      }
    } finally {
      if (listAbortControllerRef.current === abortController) {
        setLoadingList(false);
      }
    }
  }, [page, size, debouncedSearch, filters.status, filters.priority, filters.dateRange]);

  useEffect(() => {
    fetchList();
  }, [fetchList]);

  // Handle switching selected complaint safely
  const attemptSelectComplaint = (id: string | null) => {
    if (hasUnsavedNotes) {
      setPendingComplaintId(id);
      setShowUnsavedDialog(true);
    } else {
      setSelectedComplaintId(id);
    }
  };

  const confirmSwitchComplaint = (saveCurrent: boolean) => {
    if (saveCurrent && selectedComplaintId) {
      handleSaveWorkflow({ internal_notes: internalNotes }).then(() => {
        setHasUnsavedNotes(false);
        setShowUnsavedDialog(false);
        setSelectedComplaintId(pendingComplaintId);
        setPendingComplaintId(null);
      });
    } else {
      setHasUnsavedNotes(false);
      setShowUnsavedDialog(false);
      setSelectedComplaintId(pendingComplaintId);
      setPendingComplaintId(null);
    }
  };

  const cancelSwitchComplaint = () => {
    setShowUnsavedDialog(false);
    setPendingComplaintId(null);
  };

  const fetchDetail = useCallback(async (id: string) => {
    if (detailAbortControllerRef.current) {
      detailAbortControllerRef.current.abort();
    }
    const abortController = new AbortController();
    detailAbortControllerRef.current = abortController;

    setLoadingDetail(true);
    setWorkflowError(null);
    setWorkflowSuccess(false);

    try {
      const detail = await ComplaintsService.getComplaintById(id, abortController.signal);
      setSelectedComplaint(detail);
      setInternalNotes(detail.workflow?.internal_notes || '');
      setHasUnsavedNotes(false);
    } catch (err: any) {
      if (err.name !== 'CanceledError' && err.message !== 'canceled') {
        console.error('Failed to fetch detail', err);
      }
    } finally {
      if (detailAbortControllerRef.current === abortController) {
        setLoadingDetail(false);
      }
    }
  }, []);

  // Fetch detail when ID changes
  useEffect(() => {
    if (!selectedComplaintId) {
      setSelectedComplaint(null);
      return;
    }
    fetchDetail(selectedComplaintId);
    
    return () => {
      if (detailAbortControllerRef.current) {
        detailAbortControllerRef.current.abort();
      }
    };
  }, [selectedComplaintId, fetchDetail]);

  const handleNotesChange = (val: string) => {
    setInternalNotes(val);
    setHasUnsavedNotes(val !== (selectedComplaint?.workflow?.internal_notes || ''));
  };

  const handleSaveWorkflow = async (updateData: Record<string, any>) => {
    if (!selectedComplaintId) return;
    
    setIsSavingWorkflow(true);
    setWorkflowError(null);
    setWorkflowSuccess(false);

    try {
      await ComplaintsService.updateWorkflow(selectedComplaintId, updateData);
      setWorkflowSuccess(true);
      if (updateData.internal_notes !== undefined) {
        setHasUnsavedNotes(false);
      }
      setTimeout(() => setWorkflowSuccess(false), 3000);
      
      // Refresh list to update status in the main grid
      fetchList();
      // Auto-refresh detail
      fetchDetail(selectedComplaintId);
    } catch (err: any) {
      setWorkflowError(err.response?.data?.message || err.message || 'Failed to update workflow');
    } finally {
      setIsSavingWorkflow(false);
    }
  };

  const handleStatusChangeRequest = (newStatus: string) => {
    if (newStatus === 'resolved') {
      setPendingStatusChange(newStatus);
      setShowCloseConfirmDialog(true);
    } else {
      handleSaveWorkflow({ internal_status: newStatus });
    }
  };

  const confirmStatusChange = () => {
    if (pendingStatusChange) {
      handleSaveWorkflow({ internal_status: pendingStatusChange }).then(() => {
        setShowCloseConfirmDialog(false);
        setPendingStatusChange(null);
      });
    }
  };
  
  const cancelStatusChange = () => {
    setShowCloseConfirmDialog(false);
    setPendingStatusChange(null);
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
    selectedComplaintId,
    attemptSelectComplaint,
    selectedComplaint,
    loadingDetail,
    refreshList: fetchList,
    admins,
    internalNotes,
    handleNotesChange,
    hasUnsavedNotes,
    isSavingWorkflow,
    workflowError,
    workflowSuccess,
    handleSaveWorkflow,
    handleStatusChangeRequest,
    // Dialog exports
    showUnsavedDialog,
    confirmSwitchComplaint,
    cancelSwitchComplaint,
    showCloseConfirmDialog,
    confirmStatusChange,
    cancelStatusChange
  };
}
