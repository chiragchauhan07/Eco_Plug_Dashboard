import { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import { SettingsService, type SettingsBulkUpdateRequest, type SettingItem } from '../services/settings.service';

export function useSettings() {
  const [settings, setSettings] = useState<SettingItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Convert list to dictionary for easy access in UI components
  const settingsMap = useMemo(() => {
    return settings.reduce((acc, curr) => {
      acc[curr.setting_key] = curr.setting_value;
      return acc;
    }, {} as Record<string, any>);
  }, [settings]);

  const abortControllerRef = useRef<AbortController | null>(null);

  const fetchSettings = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    const abortController = new AbortController();
    abortControllerRef.current = abortController;

    try {
      const response = await SettingsService.getSettings(abortController.signal);
      setSettings(response.data);
    } catch (err: any) {
      if (err.name === 'CanceledError' || err.message === 'canceled') return;
      setError(err.response?.data?.message || err.message || 'Failed to fetch settings');
    } finally {
      if (abortControllerRef.current === abortController) {
        setLoading(false);
      }
    }
  }, []);

  useEffect(() => {
    fetchSettings();
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, [fetchSettings]);

  const updateSettings = async (payload: SettingsBulkUpdateRequest) => {
    setLoading(true);
    setError(null);
    try {
      const response = await SettingsService.updateSettings(payload);
      setSettings(response.data);
      return true;
    } catch (err: any) {
      setError(err.response?.data?.message || err.message || 'Failed to update settings');
      return false;
    } finally {
      setLoading(false);
    }
  };

  return {
    settings,
    settingsMap,
    loading,
    error,
    updateSettings,
    refresh: fetchSettings,
  };
}
