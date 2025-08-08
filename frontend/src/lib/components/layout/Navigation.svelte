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
			<div class="user-info">
				<span class="username">{$user?.display_name || $user?.username || 'User'}</span>
				<span class="user-email">{$user?.email}</span>
			</div>
			<LogoutButton />
		</div>
	</nav>
{/if}

<style>
	.navigation {
		background: #2563eb;
		color: white;
		padding: 1rem 2rem;
		display: flex;
		justify-content: space-between;
		align-items: center;
		box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
	}

	.nav-brand a {
		color: white;
		text-decoration: none;
		font-size: 1.5rem;
		font-weight: bold;
	}

	.nav-menu {
		display: flex;
		gap: 1rem;
		list-style: none;
		margin: 0;
		padding: 0;
	}

	.nav-link {
		color: white;
		text-decoration: none;
		padding: 0.5rem 1rem;
		border-radius: 0.25rem;
		transition: background-color 0.2s;
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}

	.nav-link:hover {
		background-color: rgba(255, 255, 255, 0.1);
	}

	.nav-icon {
		font-size: 1rem;
	}

	.user-menu {
		display: flex;
		align-items: center;
		gap: 1rem;
	}

	.user-info {
		display: flex;
		flex-direction: column;
		align-items: flex-end;
		font-size: 0.875rem;
	}

	.username {
		font-weight: 500;
	}

	.user-email {
		opacity: 0.8;
		font-size: 0.75rem;
	}

	@media (max-width: 768px) {
		.navigation {
			flex-direction: column;
			gap: 1rem;
			padding: 1rem;
		}

		.nav-menu {
			flex-wrap: wrap;
			justify-content: center;
		}

		.user-info {
			align-items: center;
			text-align: center;
		}
	}
</style>
