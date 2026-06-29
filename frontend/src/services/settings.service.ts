import apiClient from './api.client';

export interface SettingItem {
  setting_key: string;
  setting_value: any;
  description?: string;
}

export interface SettingsBulkUpdateRequest {
  settings: SettingItem[];
}

export const SettingsService = {
  async getSettings(signal?: AbortSignal) {
    const response = await apiClient.get('/settings', { signal });
    return response.data;
  },

  async updateSettings(payload: SettingsBulkUpdateRequest, signal?: AbortSignal) {
    const response = await apiClient.put('/settings', payload, { signal });
    return response.data;
  },
};
