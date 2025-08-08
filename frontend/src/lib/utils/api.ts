// src/lib/utils/api.ts
import { browser } from '$app/environment';
import { authStore, trackActivity } from '$lib/auth/stores';
import { get } from 'svelte/store';

class ApiClient {
  private baseUrl = '/api/v1';
  private csrfToken: string | null = null;

  constructor() {
    // Initialize CSRF token if we're in browser
    if (browser) {
      this.initializeCsrfToken();
    }
  }

  private async initializeCsrfToken() {
    try {
      // For now, we'll skip CSRF token initialization
      // It can be added later when backend implements it
      console.debug('CSRF token initialization skipped - not implemented in backend');
    } catch (error) {
      console.warn('Failed to get CSRF token:', error);
    }
  }

  private getAuthHeaders(): Record<string, string> {
    const auth = get(authStore);
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      'X-Requested-With': 'XMLHttpRequest', // CSRF protection
    };

    if (auth.accessToken) {
      headers.Authorization = `Bearer ${auth.accessToken}`;
    }

    if (this.csrfToken) {
      headers['X-CSRF-Token'] = this.csrfToken;
    }

    return headers;
  }

  private async handleResponse<T>(response: Response): Promise<T> {
    // Track activity for session management
    if (browser) {
      trackActivity();
    }
    
    if (!response.ok) {
      // Handle token expiration
      if (response.status === 401) {
        authStore.update(state => ({
          ...state,
          isAuthenticated: false,
          user: null,
          accessToken: null,
          error: 'Session expired'
        }));
        // Clear any stored tokens
        this.clearTokens();
        throw new Error('Session expired');
      }
      
      const errorData = await response.json().catch(() => ({ 
        error: { message: `HTTP ${response.status}` } 
      }));
      
      const errorMessage = errorData.detail || errorData.error?.message || `HTTP ${response.status}`;
      throw new Error(errorMessage);
    }
    
    return response.json();
  }

  private clearTokens() {
    if (!browser) return;
    
    // Clear httpOnly cookies (when implemented)
    document.cookie = 'refresh_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/; Secure; HttpOnly; SameSite=Strict';
    // Clear any localStorage tokens (legacy)
    localStorage.removeItem('auth_token');
    localStorage.removeItem('refresh_token');
  }

  async get<T>(endpoint: string): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'GET',
      headers: this.getAuthHeaders(),
    });
    return this.handleResponse<T>(response);
  }

  async post<T>(endpoint: string, data?: unknown): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: data ? JSON.stringify(data) : undefined,
    });
    return this.handleResponse<T>(response);
  }

  async put<T>(endpoint: string, data: unknown): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'PUT',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(data),
    });
    return this.handleResponse<T>(response);
  }

  async delete<T>(endpoint: string): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'DELETE',
      headers: this.getAuthHeaders(),
    });
    return this.handleResponse<T>(response);
  }
}

export const apiClient = new ApiClient();