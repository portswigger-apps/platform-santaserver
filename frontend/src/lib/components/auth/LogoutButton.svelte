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

<button class="logout-btn" on:click={handleLogout}>
  Sign out
</button>

<style>
  .logout-btn {
    background: transparent;
    border: 1px solid rgba(255, 255, 255, 0.3);
    color: white;
    padding: 0.5rem 1rem;
    border-radius: 0.25rem;
    cursor: pointer;
    font-size: 0.875rem;
    transition: background-color 0.2s, border-color 0.2s;
  }

  .logout-btn:hover {
    background-color: rgba(255, 255, 255, 0.1);
    border-color: rgba(255, 255, 255, 0.5);
  }
</style>