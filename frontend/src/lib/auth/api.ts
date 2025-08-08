// src/lib/auth/api.ts - CONFIRMED BACKEND ENDPOINTS
import type { LoginRequest, LoginResponse, User, RefreshRequest, TokenResponse, ChangePasswordRequest } from './types';
import { apiClient } from '$lib/utils/api';
import { authStore, trackActivity } from './stores';
import { goto } from '$app/navigation';

// All endpoints confirmed in app/api/api_v1/endpoints/auth.py
export const authApi = {
	// POST /api/v1/auth/login - Returns LoginResponse
	async login(credentials: LoginRequest): Promise<LoginResponse> {
		return apiClient.post('/auth/login', credentials);
	},

	// POST /api/v1/auth/logout - Requires Bearer token
	async logout(): Promise<void> {
		return apiClient.post('/auth/logout');
	},

	// POST /api/v1/auth/logout-all - Revoke all sessions
	async logoutAll(): Promise<void> {
		return apiClient.post('/auth/logout-all');
	},

	// POST /api/v1/auth/refresh - RefreshRequest -> TokenResponse
	async refreshToken(refreshToken: string): Promise<TokenResponse> {
		return apiClient.post('/auth/refresh', { refresh_token: refreshToken });
	},

	// GET /api/v1/auth/profile - Returns UserProfile
	async getProfile(): Promise<User> {
		return apiClient.get('/auth/profile');
	},

	// PUT /api/v1/auth/profile - Update user profile (limited fields)
	async updateProfile(data: Partial<User>): Promise<User> {
		return apiClient.put('/auth/profile', data);
	},

	// POST /api/v1/auth/change-password - ChangePasswordRequest
	async changePassword(data: ChangePasswordRequest): Promise<void> {
		return apiClient.post('/auth/change-password', data);
	},

	// GET /api/v1/auth/verify - Verify token validity
	async verifyToken(): Promise<User> {
		return apiClient.get('/auth/verify');
	}
};

// Authentication actions for the store
export const authActions = {
	async login(credentials: LoginRequest): Promise<void> {
		authStore.update((state) => ({ ...state, isLoading: true, error: null }));

		try {
			const response = await authApi.login(credentials);

			// Calculate session expiry
			const sessionExpiry = new Date(Date.now() + response.expires_in * 1000);

			authStore.update((state) => ({
				...state,
				user: response.user,
				accessToken: response.access_token,
				isAuthenticated: true,
				isLoading: false,
				error: null,
				sessionExpiry,
				lastActivity: new Date()
			}));

			// Store refresh token in localStorage for now (httpOnly cookie would be better)
			if (response.refresh_token) {
				localStorage.setItem('refresh_token', response.refresh_token);
			}

			// Redirect to dashboard
			goto('/dashboard');
		} catch (error) {
			const errorMessage = error instanceof Error ? error.message : 'Login failed';
			authStore.update((state) => ({
				...state,
				isLoading: false,
				error: errorMessage
			}));
			throw error;
		}
	},

	async logout(): Promise<void> {
		try {
			await authApi.logout();
		} catch (error) {
			// Continue with logout even if API call fails
			console.warn('Logout API call failed:', error);
		} finally {
			// Clear local state
			authStore.update((state) => ({
				...state,
				user: null,
				accessToken: null,
				isAuthenticated: false,
				isLoading: false,
				error: null,
				sessionExpiry: null,
				lastActivity: null
			}));

			// Clear stored tokens
			localStorage.removeItem('refresh_token');

			// Redirect to login
			goto('/login');
		}
	},

	async initializeAuth(): Promise<void> {
		authStore.update((state) => ({ ...state, isLoading: true }));

		try {
			// Try to get current user profile to check if we have a valid session
			const user = await authApi.getProfile();

			authStore.update((state) => ({
				...state,
				user,
				isAuthenticated: true,
				isLoading: false,
				lastActivity: new Date()
			}));
		} catch (error) {
			// No valid session, user needs to login
			authStore.update((state) => ({
				...state,
				user: null,
				accessToken: null,
				isAuthenticated: false,
				isLoading: false,
				error: null
			}));
		}
	},

	async refreshSession(): Promise<boolean> {
		const refreshToken = localStorage.getItem('refresh_token');
		if (!refreshToken) return false;

		try {
			const response = await authApi.refreshToken(refreshToken);

			// Calculate new session expiry
			const sessionExpiry = new Date(Date.now() + response.expires_in * 1000);

			authStore.update((state) => ({
				...state,
				accessToken: response.access_token,
				sessionExpiry,
				lastActivity: new Date()
			}));

			return true;
		} catch (error) {
			// Refresh failed, clear session
			localStorage.removeItem('refresh_token');
			authStore.update((state) => ({
				...state,
				user: null,
				accessToken: null,
				isAuthenticated: false,
				error: 'Session expired'
			}));
			return false;
		}
	}
};
