/**
 * API Client Service
 */
import axios, { AxiosInstance, AxiosRequestConfig, InternalAxiosRequestConfig } from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class ApiClient {
  private client: AxiosInstance;
  private accessToken: string | null = null;
  private isRefreshing: boolean = false;
  private failedQueue: Array<{
    resolve: (value?: any) => void;
    reject: (reason?: any) => void;
  }> = [];

  constructor() {
    this.client = axios.create({
      baseURL: `${API_URL}/api/v1`,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 30000, // 30 second timeout to prevent hanging
    });

    // Request interceptor to add auth token
    this.client.interceptors.request.use(
      (config: InternalAxiosRequestConfig) => {
        if (this.accessToken) {
          config.headers.Authorization = `Bearer ${this.accessToken}`;
        }
        // Add request ID for logging
        config.headers['X-Request-ID'] = this.generateRequestId();
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => {
        return response;
      },
      async (error) => {
        const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };
        
        // If error is 401 and we haven't already retried, try to refresh token
        if (error.response?.status === 401 && !originalRequest._retry) {
          if (this.isRefreshing) {
            // If already refreshing, queue this request
            return new Promise((resolve, reject) => {
              this.failedQueue.push({ resolve, reject });
            })
              .then(() => {
                return this.client(originalRequest);
              })
              .catch((err) => {
                return Promise.reject(err);
              });
          }

          originalRequest._retry = true;
          this.isRefreshing = true;

          try {
            // Try to refresh the token using refresh token from sessionStorage
            const refreshToken = sessionStorage.getItem('refresh_token');
            if (!refreshToken) {
              throw new Error('No refresh token available');
            }
            
            // Use a separate axios instance to avoid circular dependency
            const refreshClient = axios.create({
              baseURL: `${API_URL}/api/v1`,
              headers: {
                'Content-Type': 'application/json',
              },
            });
            
            const refreshResponse = await refreshClient.post<{
              access_token: string;
              refresh_token: string;
            }>('/auth/refresh', {
              refresh_token: refreshToken,
            });
            
            const newAccessToken = refreshResponse.data.access_token;
            const newRefreshToken = refreshResponse.data.refresh_token;
            
            // Update tokens in sessionStorage and apiClient
            this.setAccessToken(newAccessToken);
            sessionStorage.setItem('access_token', newAccessToken);
            sessionStorage.setItem('refresh_token', newRefreshToken);
            
            // Retry the original request with new token
            originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
            
            // Process queued requests
            this.processQueue(null);
            
            return this.client(originalRequest);
          } catch (refreshError) {
            // Refresh failed - clear auth but don't auto-logout
            // Let the user continue working until they manually logout or close browser
            this.processQueue(refreshError);
            this.clearAuth();
            // Don't redirect to login automatically
            return Promise.reject(error);
          } finally {
            this.isRefreshing = false;
          }
        }
        
        return Promise.reject(error);
      }
    );
  }

  private processQueue(error: any) {
    this.failedQueue.forEach((prom) => {
      if (error) {
        prom.reject(error);
      } else {
        prom.resolve();
      }
    });
    this.failedQueue = [];
  }

  private generateRequestId(): string {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  setAccessToken(token: string | null) {
    this.accessToken = token;
  }

  clearAuth() {
    this.accessToken = null;
  }

  async get<T>(url: string, config?: AxiosRequestConfig) {
    return this.client.get<T>(url, config);
  }

  async post<T>(url: string, data?: any, config?: AxiosRequestConfig) {
    return this.client.post<T>(url, data, config);
  }

  async put<T>(url: string, data?: any, config?: AxiosRequestConfig) {
    return this.client.put<T>(url, data, config);
  }

  async delete<T>(url: string, config?: AxiosRequestConfig) {
    return this.client.delete<T>(url, config);
  }
}

export const apiClient = new ApiClient();

