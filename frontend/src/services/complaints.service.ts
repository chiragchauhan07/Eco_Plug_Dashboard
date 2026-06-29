import apiClient from './api.client';

export const ComplaintsService = {
  async listComplaints(params?: Record<string, any>, signal?: AbortSignal) {
    const response = await apiClient.get('/complaints', { params, signal });
    return response.data;
  },

  async getComplaintById(id: string, signal?: AbortSignal) {
    const response = await apiClient.get(`/complaints/${id}`, { signal });
    return response.data.data;
  },

  async updateWorkflow(id: string, data: Record<string, any>) {
    const response = await apiClient.patch(`/complaints/${id}`, data);
    return response.data.data;
  },

  async getAdmins(signal?: AbortSignal) {
    const response = await apiClient.get('/admins', { signal });
    return response.data.data;
  }
};
