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

<div class="card shadow login-card">
	<div class="card-header bg-primary text-white text-center">
		<h1 class="h3 mb-0">🎅 SantaServer</h1>
		<p class="mb-0 small">Enterprise Santa Management Platform</p>
	</div>
	<div class="card-body p-4">
		<form on:submit|preventDefault={handleLogin}>
			<div class="mb-3">
				<label for="username" class="form-label">Username</label>
				<input
					id="username"
					type="text"
					class="form-control"
					bind:value={credentials.username}
					disabled={$isLoading}
					placeholder="Enter your username or email"
					required
					autocomplete="username"
				/>
			</div>

			<div class="mb-3">
				<label for="password" class="form-label">Password</label>
				<div class="input-group">
					<input
						id="password"
						type={showPassword ? 'text' : 'password'}
						class="form-control"
						bind:value={credentials.password}
						disabled={$isLoading}
						placeholder="Enter your password"
						required
						autocomplete="current-password"
					/>
					<button
						type="button"
						class="btn btn-outline-secondary"
						on:click={() => (showPassword = !showPassword)}
						disabled={$isLoading}
						aria-label={showPassword ? 'Hide password' : 'Show password'}
					>
						{showPassword ? '🙈' : '👁️'}
					</button>
				</div>
			</div>

			<!-- Frontend validation errors -->
			{#if validationErrors.length > 0}
				<div class="alert alert-danger" role="alert">
					{#each validationErrors as error}
						<div class="mb-0">{error}</div>
					{/each}
				</div>
			{/if}

			<!-- Backend authentication errors -->
			{#if $authError}
				<div class="alert alert-danger" role="alert">
					{$authError}
				</div>
			{/if}

			<button type="submit" disabled={$isLoading || validationErrors.length > 0} class="btn btn-primary w-100">
				{#if $isLoading}
					<div class="spinner-border spinner-border-sm me-2" role="status">
						<span class="visually-hidden">Loading...</span>
					</div>
					Signing in...
				{:else}
					Sign in
				{/if}
			</button>
		</form>
	</div>
</div>
