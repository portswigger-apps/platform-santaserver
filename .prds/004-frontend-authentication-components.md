# PRD 004 - Frontend Authentication Components (MVP)

**Document Version:** 2.0  
**Created:** 2025-08-07  
**Status:** Draft  
**Related:** PRD 003 - Authentication and RBAC System

## Executive Summary

This PRD defines the essential frontend authentication components for SantaServer's MVP, focusing on local user authentication, basic user management, and role-based navigation using SvelteKit.

## Frontend Architecture

### Technology Stack
- **Framework**: SvelteKit with static adapter
- **Language**: TypeScript
- **State Management**: Svelte stores
- **API Client**: Fetch with authentication wrapper
- **Styling**: CSS with modern design system

### Component Structure
```
src/
├── lib/
│   ├── auth/
│   │   ├── stores.ts        # Authentication state
│   │   ├── api.ts           # API client
│   │   └── types.ts         # TypeScript interfaces
│   ├── components/
│   │   ├── auth/
│   │   │   ├── LoginForm.svelte
│   │   │   └── LogoutButton.svelte
│   │   └── layout/
│   │       ├── Navigation.svelte
│   │       └── AuthGuard.svelte
│   └── utils/
│       └── api.ts           # Base API client
└── routes/
    ├── (auth)/
    │   └── login/+page.svelte
    └── (dashboard)/
        └── +layout.svelte   # Protected routes
```

## Authentication State Management

### Core Types
```typescript
// src/lib/auth/types.ts
export interface User {
  id: string;
  username: string;
  email: string;
  roles: Role[];
  groups: Group[];
  is_active: boolean;
}

export interface Role {
  id: string;
  name: string;
  display_name: string;
  permissions: Record<string, string[]>;
}

export interface Group {
  id: string;
  name: string;
  display_name: string;
  roles: Role[];
}

export interface LoginRequest {
  username: string;
  password: string;
  remember_me?: boolean;
}
```

### Authentication Store
```typescript
// src/lib/auth/stores.ts
import { writable, derived } from 'svelte/store';

interface AuthState {
  user: User | null;
  accessToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

export const authStore = writable<AuthState>({
  user: null,
  accessToken: null,
  isAuthenticated: false,
  isLoading: true,
  error: null
});

// Derived stores
export const user = derived(authStore, ($auth) => $auth.user);
export const isAuthenticated = derived(authStore, ($auth) => $auth.isAuthenticated);

// Permission checker
export const hasPermission = derived(user, ($user) => 
  (resource: string, action: string) => {
    if (!$user) return false;
    
    // Check direct role permissions
    for (const role of $user.roles) {
      if (role.permissions[resource]?.includes(action)) {
        return true;
      }
    }
    
    // Check group role permissions
    for (const group of $user.groups) {
      for (const role of group.roles) {
        if (role.permissions[resource]?.includes(action)) {
          return true;
        }
      }
    }
    
    return false;
  }
);
```

## Core Components

### Login Form
```svelte
<!-- src/lib/components/auth/LoginForm.svelte -->
<script lang="ts">
  import { authActions, authError, isLoading } from '$lib/auth/stores';
  import type { LoginRequest } from '$lib/auth/types';

  let credentials: LoginRequest = {
    username: '',
    password: '',
    remember_me: false
  };

  let showPassword = false;

  async function handleLogin() {
    try {
      await authActions.login(credentials);
    } catch (error) {
      // Error handled by store
    }
  }
</script>

<div class="login-form">
  <h1>Sign in to SantaServer</h1>
  
  <form on:submit|preventDefault={handleLogin}>
    <div class="field">
      <label for="username">Username</label>
      <input
        id="username"
        type="text"
        bind:value={credentials.username}
        disabled={$isLoading}
        required
      />
    </div>

    <div class="field">
      <label for="password">Password</label>
      <div class="password-input">
        <input
          id="password"
          type={showPassword ? 'text' : 'password'}
          bind:value={credentials.password}
          disabled={$isLoading}
          required
        />
        <button
          type="button"
          class="toggle-password"
          on:click={() => showPassword = !showPassword}
        >
          {showPassword ? '🙈' : '👁️'}
        </button>
      </div>
    </div>

    <label class="checkbox">
      <input
        type="checkbox"
        bind:checked={credentials.remember_me}
        disabled={$isLoading}
      />
      Remember me
    </label>

    {#if $authError}
      <div class="error" role="alert">
        {$authError}
      </div>
    {/if}

    <button type="submit" disabled={$isLoading} class="submit-btn">
      {$isLoading ? 'Signing in...' : 'Sign in'}
    </button>
  </form>
</div>
```

### Navigation with Role-Based Menu
```svelte
<!-- src/lib/components/layout/Navigation.svelte -->
<script lang="ts">
  import { user, isAuthenticated, hasPermission } from '$lib/auth/stores';
  import LogoutButton from '../auth/LogoutButton.svelte';
  
  interface NavItem {
    label: string;
    href: string;
    permission?: { resource: string; action: string };
    icon: string;
  }
  
  const navItems: NavItem[] = [
    { label: 'Dashboard', href: '/dashboard', icon: '📊' },
    { label: 'Rules', href: '/rules', permission: { resource: 'santa', action: 'read' }, icon: '📝' },
    { label: 'Approvals', href: '/approvals', permission: { resource: 'santa', action: 'approve' }, icon: '✅' },
    { label: 'Users', href: '/users', permission: { resource: 'users', action: 'read' }, icon: '👥' },
    { label: 'Groups', href: '/groups', permission: { resource: 'groups', action: 'read' }, icon: '👫' },
    { label: 'System', href: '/system', permission: { resource: 'system', action: 'configure' }, icon: '⚙️' }
  ];
</script>

{#if $isAuthenticated}
  <nav class="navigation">
    <div class="nav-brand">
      <a href="/dashboard">🎅 SantaServer</a>
    </div>
    
    <ul class="nav-menu">
      {#each navItems as item}
        {#if !item.permission || $hasPermission(item.permission.resource, item.permission.action)}
          <li>
            <a href={item.href} class="nav-link">
              <span class="nav-icon">{item.icon}</span>
              {item.label}
            </a>
          </li>
        {/if}
      {/each}
    </ul>
    
    <div class="user-menu">
      <span class="username">{$user?.username}</span>
      <LogoutButton />
    </div>
  </nav>
{/if}
```

### Route Protection
```svelte
<!-- src/lib/components/layout/AuthGuard.svelte -->
<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { page } from '$app/stores';
  import { isAuthenticated, isLoading, hasPermission, authActions } from '$lib/auth/stores';
  
  export let requiredPermission: { resource: string; action: string } | null = null;
  
  onMount(() => {
    authActions.initializeAuth();
  });
  
  $: {
    if (!$isLoading) {
      if (!$isAuthenticated) {
        const redirectUrl = `/login?redirect=${encodeURIComponent($page.url.pathname)}`;
        goto(redirectUrl);
      } else if (requiredPermission && !$hasPermission(requiredPermission.resource, requiredPermission.action)) {
        goto('/unauthorized');
      }
    }
  }
</script>

{#if $isLoading}
  <div class="loading">
    <div class="spinner"></div>
    <p>Loading...</p>
  </div>
{:else if $isAuthenticated && (!requiredPermission || $hasPermission(requiredPermission.resource, requiredPermission.action))}
  <slot />
{/if}
```

## API Integration

### Authentication API Client
```typescript
// src/lib/auth/api.ts
import type { LoginRequest, User } from './types';
import { apiClient } from '$lib/utils/api';

export const authApi = {
  async login(credentials: LoginRequest) {
    return apiClient.post('/auth/login', credentials);
  },

  async logout() {
    return apiClient.post('/auth/logout');
  },

  async refreshToken(refreshToken: string) {
    return apiClient.post('/auth/refresh', { refresh_token: refreshToken });
  },

  async getProfile(): Promise<User> {
    return apiClient.get('/auth/profile');
  },

  async changePassword(data: {
    current_password: string;
    new_password: string;
    confirm_password: string;
  }) {
    return apiClient.post('/auth/change-password', data);
  }
};
```

### Base API Client
```typescript
// src/lib/utils/api.ts
import { browser } from '$app/environment';
import { authStore } from '$lib/auth/stores';
import { get } from 'svelte/store';

class ApiClient {
  private baseUrl = '/api/v1';

  private getAuthHeaders(): Record<string, string> {
    const auth = get(authStore);
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    if (auth.accessToken) {
      headers.Authorization = `Bearer ${auth.accessToken}`;
    }

    return headers;
  }

  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      const error = await response.json().catch(() => ({ error: { message: `HTTP ${response.status}` } }));
      throw new Error(error.error?.message || `HTTP ${response.status}`);
    }
    return response.json();
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
```

## Route Structure

### Login Page
```svelte
<!-- src/routes/(auth)/login/+page.svelte -->
<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { isAuthenticated } from '$lib/auth/stores';
  import LoginForm from '$lib/components/auth/LoginForm.svelte';
  
  onMount(() => {
    if ($isAuthenticated) {
      goto('/dashboard');
    }
  });
</script>

<svelte:head>
  <title>Sign in - SantaServer</title>
</svelte:head>

<div class="login-page">
  <LoginForm />
</div>
```

### Protected Layout
```svelte
<!-- src/routes/(dashboard)/+layout.svelte -->
<script>
  import AuthGuard from '$lib/components/layout/AuthGuard.svelte';
  import Navigation from '$lib/components/layout/Navigation.svelte';
</script>

<AuthGuard>
  <div class="dashboard-layout">
    <Navigation />
    <main class="main-content">
      <slot />
    </main>
  </div>
</AuthGuard>
```

## Styling System

### CSS Variables
```css
/* src/app.css */
:root {
  --color-primary: #2563eb;
  --color-surface: #ffffff;
  --color-background: #f8fafc;
  --color-text-primary: #1e293b;
  --color-text-secondary: #64748b;
  --color-border: #e2e8f0;
  --color-error: #dc2626;
  --color-success: #16a34a;
  
  --border-radius: 0.375rem;
  --shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1);
  --transition: 0.2s ease;
}

/* Base styles */
body {
  font-family: system-ui, sans-serif;
  line-height: 1.5;
  color: var(--color-text-primary);
  background-color: var(--color-background);
  margin: 0;
}

/* Form styles */
.field {
  margin-bottom: 1rem;
}

.field label {
  display: block;
  margin-bottom: 0.25rem;
  font-weight: 500;
}

.field input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius);
  transition: border-color var(--transition);
}

.field input:focus {
  outline: none;
  border-color: var(--color-primary);
}

/* Button styles */
.submit-btn {
  width: 100%;
  padding: 0.75rem;
  background-color: var(--color-primary);
  color: white;
  border: none;
  border-radius: var(--border-radius);
  font-weight: 500;
  cursor: pointer;
  transition: opacity var(--transition);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
```

## Implementation Notes

### Authentication Flow
1. User enters credentials in LoginForm
2. authActions.login() calls API and stores tokens
3. User data stored in authStore
4. Navigation updates based on user permissions
5. Route protection enforced via AuthGuard

### Permission System
- Permissions checked through derived store
- Supports both direct role permissions and group-inherited permissions
- Navigation items shown/hidden based on permissions
- Route access controlled by AuthGuard component

### Token Management
- Access tokens stored in memory only
- Refresh tokens stored in localStorage
- Automatic token refresh on API calls
- Logout clears all stored authentication data

This simplified frontend architecture provides essential authentication functionality for the MVP while maintaining clean separation of concerns and extensibility for future enhancements.