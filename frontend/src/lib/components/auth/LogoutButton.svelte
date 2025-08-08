<!-- src/lib/components/auth/LogoutButton.svelte -->
<script lang="ts">
	import { authActions } from '$lib/auth/api';

	async function handleLogout() {
		try {
			await authActions.logout();
		} catch (error) {
			// Error handling is done in authActions.logout
			console.error('Logout error:', error);
		}
	}
</script>

<button class="btn btn-outline-light btn-sm" on:click={handleLogout}> Sign out </button>
