/**
 * Authentication Service
 */
import { apiClient } from './api';
import axios from 'axios';

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface User {
  user_id: string;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

class AuthService {
  private accessToken: string | null = sessionStorage.getItem('access_token');
  private refreshToken: string | null = sessionStorage.getItem('refresh_token');
  private currentUser: User | null = this.loadUserFromStorage();

  constructor() {
    // Initialize API client with stored token if available
    if (this.accessToken) {
      apiClient.setAccessToken(this.accessToken);
    }
  }

  private loadUserFromStorage(): User | null {
    try {
      const userStr = sessionStorage.getItem('current_user');
      if (userStr) {
        return JSON.parse(userStr);
      }
    } catch (error) {
      console.error('[AUTH] Failed to load user from storage', error);
    }
    return null;
  }

  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    try {
      const response = await apiClient.post<AuthResponse>('/auth/login', credentials);
      
      const { access_token, refresh_token, user } = response.data;
      
      this.setTokens(access_token, refresh_token);
      this.setCurrentUser(user);
      
      console.log('[AUTH] Login successful', {
        requestId: response.headers['x-request-id'],
        userId: user.user_id,
        role: user.role,
      });
      
      return response.data;
    } catch (error: any) {
      console.error('[AUTH] Login failed', error);
      throw error;
    }
  }

  async refreshAccessToken(): Promise<string> {
    if (!this.refreshToken) {
      throw new Error('No refresh token available');
    }

    try {
      // Temporarily remove token from apiClient to avoid infinite loop
      const tempClient = axios.create({
        baseURL: `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/v1`,
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      const response = await tempClient.post<AuthResponse>('/auth/refresh', {
        refresh_token: this.refreshToken,
      });
      
      this.setTokens(response.data.access_token, response.data.refresh_token);
      return response.data.access_token;
    } catch (error) {
      console.error('[AUTH] Token refresh failed', error);
      // Don't auto-logout, just throw error
      throw error;
    }
  }

  async getCurrentUser(): Promise<User> {
    try {
      const response = await apiClient.get<User>('/auth/me');
      this.setCurrentUser(response.data);
      return response.data;
    } catch (error) {
      console.error('[AUTH] Get current user failed', error);
      throw error;
    }
  }

  async logout(): Promise<void> {
    try {
      await apiClient.post('/auth/logout');
    } catch (error) {
      console.error('[AUTH] Logout failed', error);
    } finally {
      this.clearAuth();
    }
  }

  private setTokens(accessToken: string, refreshToken: string) {
    this.accessToken = accessToken;
    this.refreshToken = refreshToken;
    apiClient.setAccessToken(accessToken);
    // Store tokens in sessionStorage (cleared on browser close)
    // For production, consider httpOnly cookies
    sessionStorage.setItem('access_token', accessToken);
    sessionStorage.setItem('refresh_token', refreshToken);
  }

  private setCurrentUser(user: User) {
    this.currentUser = user;
    // Store user in sessionStorage for persistence across page refreshes
    try {
      sessionStorage.setItem('current_user', JSON.stringify(user));
    } catch (error) {
      console.error('[AUTH] Failed to store user in storage', error);
    }
  }

  private clearAuth() {
    this.accessToken = null;
    this.refreshToken = null;
    this.currentUser = null;
    apiClient.clearAuth();
    sessionStorage.removeItem('access_token');
    sessionStorage.removeItem('refresh_token');
    sessionStorage.removeItem('current_user');
  }

  isAuthenticated(): boolean {
    return this.accessToken !== null;
  }

  getCurrentUserSync(): User | null {
    return this.currentUser;
  }

  getAccessToken(): string | null {
    return this.accessToken;
  }
}

export const authService = new AuthService();

