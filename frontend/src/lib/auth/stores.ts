// src/lib/auth/stores.ts
import { writable, derived, get } from 'svelte/store';
import type { User } from './types';

interface AuthState {
	user: User | null;
	accessToken: string | null;
	isAuthenticated: boolean;
	isLoading: boolean;
	error: string | null;
	sessionExpiry: Date | null;
	lastActivity: Date | null;
}

export const authStore = writable<AuthState>({
	user: null,
	accessToken: null,
	isAuthenticated: false,
	isLoading: true,
	error: null,
	sessionExpiry: null,
	lastActivity: null
});

// Derived stores
export const user = derived(authStore, ($auth) => $auth.user);
export const isAuthenticated = derived(authStore, ($auth) => $auth.isAuthenticated);
export const isLoading = derived(authStore, ($auth) => $auth.isLoading);
export const authError = derived(authStore, ($auth) => $auth.error);

// Memoized permission checker for performance
const permissionCache = new Map<string, boolean>();
const CACHE_EXPIRY = 5 * 60 * 1000; // 5 minutes
let lastCacheUpdate = 0;

export const hasPermission = derived(user, ($user) => (resource: string, action: string) => {
	if (!$user) return false;

	const cacheKey = `${$user.id}:${resource}:${action}`;
	const now = Date.now();

	// Check cache validity and clear if expired
	if (now - lastCacheUpdate > CACHE_EXPIRY) {
		permissionCache.clear();
		lastCacheUpdate = now;
	}

	// Return cached result if available
	if (permissionCache.has(cacheKey)) {
		return permissionCache.get(cacheKey)!;
	}

	// For now, simple admin/user logic since backend doesn't include roles in user object
	// This will be enhanced when roles are available
	let hasAccess = false;

	// Basic permission logic - will be enhanced with actual roles
	if ($user.username === 'admin' || $user.email?.includes('admin')) {
		hasAccess = true;
	} else if (resource === 'dashboard' && action === 'read') {
		hasAccess = true; // All authenticated users can access dashboard
	}

	// Cache the result
	permissionCache.set(cacheKey, hasAccess);
	return hasAccess;
});

// Session monitoring
export const isSessionExpired = derived(authStore, ($auth) => {
	if (!$auth.sessionExpiry || !$auth.isAuthenticated) return false;
	return new Date() > $auth.sessionExpiry;
});

// Activity tracking for session timeout
export const trackActivity = () => {
	authStore.update((state) => ({
		...state,
		lastActivity: new Date()
	}));
};

// Session manager
const SESSION_TIMEOUT = 30 * 60 * 1000; // 30 minutes

export const sessionManager = {
	checkSessionValidity(): boolean {
		const auth = get(authStore);
		if (!auth.isAuthenticated || !auth.lastActivity) return false;

		const now = new Date();
		const timeSinceActivity = now.getTime() - auth.lastActivity.getTime();

		return timeSinceActivity < SESSION_TIMEOUT;
	},

	extendSession(): void {
		if (this.checkSessionValidity()) {
			trackActivity();
		} else {
			this.endSession();
		}
	},

	endSession(): void {
		authStore.update((state) => ({
			...state,
			isAuthenticated: false,
			user: null,
			accessToken: null,
			sessionExpiry: null,
			error: 'Session expired due to inactivity'
		}));
	}
};
