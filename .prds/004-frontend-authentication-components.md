# PRD 004 - Frontend Authentication Components (MVP)

**Document Version:** 2.0  
**Created:** 2025-08-07  
**Status:** Draft  
**Related:** PRD 003 - Authentication and RBAC System

## Executive Summary

This PRD defines the essential frontend authentication components for SantaServer's MVP, focusing on local user authentication, basic user management, and role-based navigation using SvelteKit. Designed with extensible architecture to support future SSO and SCIM user types with visible indicators in the admin UI.

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
│   │   └── types.ts         # TypeScript interfaces with user types
│   ├── components/
│   │   ├── auth/
│   │   │   ├── LoginForm.svelte
│   │   │   └── LogoutButton.svelte
│   │   ├── admin/
│   │   │   ├── UserList.svelte        # User management with type display
│   │   │   ├── UserTypeIndicator.svelte  # Visual user type indicators
│   │   │   ├── UserActions.svelte     # Type-aware user actions
│   │   │   └── ProviderSelector.svelte  # Provider filtering
│   │   └── layout/
│   │       ├── Navigation.svelte
│   │       └── AuthGuard.svelte
│   └── utils/
│       └── api.ts           # Base API client
└── routes/
    ├── (auth)/
    │   └── login/+page.svelte
    ├── (admin)/
    │   ├── users/+page.svelte        # Enhanced user management
    │   └── providers/+page.svelte    # Future provider configuration
    └── (dashboard)/
        └── +layout.svelte   # Protected routes
```

## Authentication State Management

### Core Types
```typescript
// src/lib/auth/types.ts

// User authentication types enum
export enum UserType {
  LOCAL = 'local',
  SSO = 'sso', 
  SCIM = 'scim'
}

export enum ProviderType {
  SAML2 = 'saml2',
  OIDC = 'oidc',
  SCIM_V2 = 'scim_v2'
}

export interface User {
  id: string;
  username: string;
  email: string;
  user_type: UserType;
  
  // Enhanced profile (SCIM-compatible)
  first_name?: string;
  last_name?: string;
  display_name?: string;
  department?: string;
  title?: string;
  phone?: string;
  
  // External identity info (admin view only)
  external_id?: string;
  provider_name?: string;
  provider_display_name?: string;
  
  // Status
  is_active: boolean;
  is_provisioned: boolean;
  last_login?: Date;
  last_sync?: Date;
  
  // Relationships
  roles: Role[];
  groups: Group[];
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
  description?: string;
  source_type: 'local' | 'scim' | 'sso';
  external_id?: string;
  provider_name?: string;
  provider_display_name?: string;
  last_sync?: Date;
  roles: Role[];
}

export interface AuthProvider {
  id: string;
  name: string;
  display_name: string;
  provider_type: ProviderType;
  is_enabled: boolean;
  created_at: Date;
  updated_at: Date;
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

## User Type Management Components

### UserTypeIndicator Component
Visual indicator component that displays user authentication type with appropriate styling and icons.

```svelte
<!-- src/lib/components/admin/UserTypeIndicator.svelte -->
<script lang="ts">
  import { UserType } from '$lib/auth/types';
  
  export let userType: UserType;
  
  const typeConfig = {
    [UserType.LOCAL]: {
      label: 'Local',
      icon: '🔑',
      class: 'local',
      description: 'Local username/password authentication'
    },
    [UserType.SSO]: {
      label: 'SSO',
      icon: '🔐',
      class: 'sso',
      description: 'Single Sign-On authentication'
    },
    [UserType.SCIM]: {
      label: 'SCIM',
      icon: '⚡',
      class: 'scim',
      description: 'SCIM-provisioned from identity provider'
    }
  };
  
  $: config = typeConfig[userType];
</script>

<span 
  class="user-type-indicator {config.class}"
  title={config.description}
>
  <span class="type-icon">{config.icon}</span>
  <span class="type-label">{config.label}</span>
</span>

<style>
  .user-type-indicator {
    display: inline-flex;
    align-items: center;
    gap: 0.25rem;
    padding: 0.25rem 0.5rem;
    border-radius: 0.375rem;
    font-size: 0.875rem;
    font-weight: 500;
  }
  
  .local {
    background-color: #dbeafe;
    color: #1e40af;
  }
  
  .sso {
    background-color: #dcfce7;
    color: #166534;
  }
  
  .scim {
    background-color: #fef3c7;
    color: #92400e;
  }
</style>
```

### Enhanced UserList Component
User management interface with type filtering and visual indicators for different authentication types.

```svelte
<!-- src/lib/components/admin/UserList.svelte -->
<script lang="ts">
  import { onMount } from 'svelte';
  import { UserType, type User, type AuthProvider } from '$lib/auth/types';
  import UserTypeIndicator from './UserTypeIndicator.svelte';
  import UserActions from './UserActions.svelte';
  
  let users: User[] = [];
  let providers: AuthProvider[] = [];
  let loading = true;
  let selectedUserType: UserType | 'all' = 'all';
  let selectedProvider: string | 'all' = 'all';
  
  async function loadUsers() {
    loading = true;
    const params = new URLSearchParams();
    if (selectedUserType !== 'all') params.set('user_type', selectedUserType);
    if (selectedProvider !== 'all') params.set('provider_name', selectedProvider);
    
    users = await apiClient.get(`/users?${params.toString()}`);
    loading = false;
  }
  
  onMount(async () => {
    providers = await apiClient.get('/auth/providers');
    await loadUsers();
  });
</script>

<div class="user-management">
  <div class="filters">
    <select bind:value={selectedUserType} on:change={loadUsers}>
      <option value="all">All User Types</option>
      <option value={UserType.LOCAL}>Local Users</option>
      <option value={UserType.SSO}>SSO Users</option>
      <option value={UserType.SCIM}>SCIM Users</option>
    </select>
    
    <select bind:value={selectedProvider} on:change={loadUsers}>
      <option value="all">All Providers</option>
      {#each providers as provider}
        <option value={provider.name}>{provider.display_name}</option>
      {/each}
    </select>
  </div>
  
  <div class="user-table">
    <table>
      <thead>
        <tr>
          <th>User</th>
          <th>Type</th>
          <th>Provider</th>
          <th>Status</th>
          <th>Last Login</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        {#each users as user}
          <tr>
            <td>
              <div class="user-info">
                <div class="user-name">
                  {user.display_name || `${user.first_name} ${user.last_name}` || user.username}
                </div>
                <div class="user-email">{user.email}</div>
                {#if user.department}
                  <div class="user-dept">{user.department}</div>
                {/if}
              </div>
            </td>
            <td>
              <UserTypeIndicator userType={user.user_type} />
            </td>
            <td>
              {#if user.provider_display_name}
                <span class="provider-name">{user.provider_display_name}</span>
              {:else}
                <span class="no-provider">Local</span>
              {/if}
            </td>
            <td>
              <div class="status-indicators">
                <span class="status {user.is_active ? 'active' : 'inactive'}">
                  {user.is_active ? 'Active' : 'Inactive'}
                </span>
                {#if user.user_type === UserType.SCIM}
                  <span class="provisioned {user.is_provisioned ? 'yes' : 'no'}">
                    {user.is_provisioned ? 'Provisioned' : 'Pending'}
                  </span>
                {/if}
              </div>
            </td>
            <td>
              {#if user.last_login}
                {new Date(user.last_login).toLocaleDateString()}
              {:else}
                <span class="never">Never</span>
              {/if}
            </td>
            <td>
              <UserActions {user} on:userUpdated={loadUsers} />
            </td>
          </tr>
        {/each}
      </tbody>
    </table>
  </div>
</div>
```

### Type-Aware User Actions
User action component that provides different actions based on user type (local users can change passwords, SSO users cannot, etc.).

```svelte
<!-- src/lib/components/admin/UserActions.svelte -->
<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { UserType, type User } from '$lib/auth/types';
  
  export let user: User;
  
  const dispatch = createEventDispatcher();
  
  async function toggleUserStatus() {
    await apiClient.put(`/users/${user.id}`, {
      is_active: !user.is_active
    });
    dispatch('userUpdated');
  }
  
  async function resetPassword() {
    // Only available for local users
    if (user.user_type === UserType.LOCAL) {
      // Implementation for password reset
      dispatch('userUpdated');
    }
  }
  
  async function syncUser() {
    // Only available for SCIM users
    if (user.user_type === UserType.SCIM) {
      await apiClient.post(`/users/${user.id}/sync`);
      dispatch('userUpdated');
    }
  }
</script>

<div class="user-actions">
  <button 
    class="action-btn {user.is_active ? 'deactivate' : 'activate'}"
    on:click={toggleUserStatus}
  >
    {user.is_active ? 'Deactivate' : 'Activate'}
  </button>
  
  {#if user.user_type === UserType.LOCAL}
    <button class="action-btn reset" on:click={resetPassword}>
      Reset Password
    </button>
  {/if}
  
  {#if user.user_type === UserType.SCIM}
    <button class="action-btn sync" on:click={syncUser}>
      Sync Now
    </button>
  {/if}
</div>
```

## API Integration Updates

### Enhanced Authentication API with User Types
```typescript
// src/lib/auth/api.ts
import type { LoginRequest, User, UserType } from './types';
import { apiClient } from '$lib/utils/api';

export const authApi = {
  async login(credentials: LoginRequest) {
    return apiClient.post('/auth/login', credentials);
  },

  async logout() {
    return apiClient.post('/auth/logout');
  },

  async getProfile(): Promise<User> {
    return apiClient.get('/auth/profile');
  },

  // Enhanced user management with type filtering
  async getUsers(filters?: {
    user_type?: UserType;
    provider_name?: string;
    is_active?: boolean;
    skip?: number;
    limit?: number;
  }): Promise<User[]> {
    const params = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          params.set(key, String(value));
        }
      });
    }
    return apiClient.get(`/users?${params.toString()}`);
  },

  async getAuthProviders() {
    return apiClient.get('/auth/providers');
  },

  async syncScimUser(userId: string) {
    return apiClient.post(`/users/${userId}/sync`);
  }
};
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