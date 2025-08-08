<!-- src/lib/components/auth/LoginForm.svelte -->
<script lang="ts">
  import { authActions } from '$lib/auth/api';
  import { authError, isLoading } from '$lib/auth/stores';
  import type { LoginRequest } from '$lib/auth/types';

  let credentials: LoginRequest = {
    username: '',
    password: ''
    // remember_me removed - not implemented in backend v1
  };

  let showPassword = false;
  let validationErrors: string[] = [];

  // Frontend validation before API call
  function validateForm(): boolean {
    validationErrors = [];
    
    if (!credentials.username.trim()) {
      validationErrors.push('Username or email is required');
    }
    
    if (!credentials.password) {
      validationErrors.push('Password is required');
    } else if (credentials.password.length < 8) {
      validationErrors.push('Password must be at least 8 characters');
    }
    
    return validationErrors.length === 0;
  }

  async function handleLogin() {
    if (!validateForm()) return;
    
    try {
      await authActions.login(credentials);
      // Success handled by store - redirects to dashboard
    } catch (error) {
      // Backend errors:
      // - "Incorrect username or password" (401)
      // - "Account inactive" / "Account locked" (401)
      // Error displayed by store
    }
  }

</script>

<div class="login-form">
  <div class="login-header">
    <h1>Sign in to SantaServer</h1>
    <p class="subtitle">Enterprise Santa Management Platform</p>
  </div>
  
  <form on:submit|preventDefault={handleLogin}>
    <div class="field">
      <label for="username">Username</label>
      <input
        id="username"
        type="text"
        bind:value={credentials.username}
        disabled={$isLoading}
        placeholder="Enter your username or email"
        required
        autocomplete="username"
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
          placeholder="Enter your password"
          required
          autocomplete="current-password"
        />
        <button
          type="button"
          class="toggle-password"
          on:click={() => showPassword = !showPassword}
          disabled={$isLoading}
          aria-label={showPassword ? 'Hide password' : 'Show password'}
        >
          {showPassword ? '🙈' : '👁️'}
        </button>
      </div>
    </div>

    <!-- Remember me removed - not implemented in backend v1 -->

    <!-- Frontend validation errors -->
    {#if validationErrors.length > 0}
      <div class="validation-errors" role="alert">
        {#each validationErrors as error}
          <p class="error">{error}</p>
        {/each}
      </div>
    {/if}
    
    <!-- Backend authentication errors -->
    {#if $authError}
      <div class="auth-error" role="alert">
        {$authError}
      </div>
    {/if}

    <button type="submit" disabled={$isLoading || validationErrors.length > 0} class="submit-btn">
      {$isLoading ? 'Signing in...' : 'Sign in'}
    </button>
  </form>
</div>

<style>
  .login-form {
    max-width: 400px;
    margin: 2rem auto;
    padding: 2rem;
    background: white;
    border-radius: 0.5rem;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  }

  .login-header {
    text-align: center;
    margin-bottom: 2rem;
  }

  .login-header h1 {
    margin: 0 0 0.5rem 0;
    color: #1f2937;
    font-size: 1.75rem;
  }

  .subtitle {
    margin: 0;
    color: #6b7280;
    font-size: 0.875rem;
  }

  .field {
    margin-bottom: 1rem;
  }

  .field label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
    color: #374151;
  }

  .field input {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid #d1d5db;
    border-radius: 0.375rem;
    font-size: 1rem;
    transition: border-color 0.2s;
    box-sizing: border-box;
  }

  .field input:focus {
    outline: none;
    border-color: #2563eb;
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
  }

  .field input:disabled {
    background-color: #f9fafb;
    cursor: not-allowed;
  }

  .password-input {
    position: relative;
    display: flex;
    align-items: center;
  }

  .toggle-password {
    position: absolute;
    right: 0.75rem;
    background: none;
    border: none;
    cursor: pointer;
    padding: 0.25rem;
    color: #6b7280;
    transition: color 0.2s;
  }

  .toggle-password:hover {
    color: #374151;
  }

  .toggle-password:disabled {
    cursor: not-allowed;
    opacity: 0.5;
  }

  .validation-errors,
  .auth-error {
    margin-bottom: 1rem;
    padding: 0.75rem;
    background-color: #fef2f2;
    border: 1px solid #fecaca;
    border-radius: 0.375rem;
  }

  .error {
    margin: 0;
    color: #dc2626;
    font-size: 0.875rem;
  }

  .submit-btn {
    width: 100%;
    padding: 0.75rem;
    background-color: #2563eb;
    color: white;
    border: none;
    border-radius: 0.375rem;
    font-weight: 500;
    font-size: 1rem;
    cursor: pointer;
    transition: background-color 0.2s, opacity 0.2s;
  }

  .submit-btn:hover:not(:disabled) {
    background-color: #1d4ed8;
  }

  .submit-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    background-color: #6b7280;
  }

  @media (max-width: 640px) {
    .login-form {
      margin: 1rem;
      padding: 1.5rem;
    }
  }
</style>