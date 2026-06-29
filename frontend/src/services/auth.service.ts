import apiClient from './api.client';
import { TokenService } from './token.service';

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface UserProfile {
  id: string;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
  created_at: string;
}

export const AuthService = {
  async login(email: string, password: string): Promise<LoginResponse> {
    const response = await apiClient.post('/auth/login', { email, password });
    const data = response.data.data;
    TokenService.setTokens(data.access_token, data.refresh_token);
    return data;
  },

  async getProfile(): Promise<UserProfile> {
    const response = await apiClient.get('/auth/me');
    return response.data.data;
  },

  async refreshToken(): Promise<LoginResponse> {
    const refreshToken = TokenService.getRefreshToken();
    const response = await apiClient.post('/auth/refresh', {
      refresh_token: refreshToken,
    });
    const data = response.data.data;
    TokenService.setTokens(data.access_token, data.refresh_token);
    return data;
  },

  logout(): void {
    TokenService.clearTokens();
    window.location.href = '/login';
  },
};
