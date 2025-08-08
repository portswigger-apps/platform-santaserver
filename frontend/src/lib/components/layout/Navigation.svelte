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
	<nav class="navbar navbar-expand-lg navbar-dark bg-primary">
		<div class="container-fluid">
			<!-- Brand -->
			<a class="navbar-brand" href="/dashboard"> 🎅 SantaServer </a>

			<!-- Mobile toggle button -->
			<button
				class="navbar-toggler"
				type="button"
				data-bs-toggle="collapse"
				data-bs-target="#navbarNav"
				aria-controls="navbarNav"
				aria-expanded="false"
				aria-label="Toggle navigation"
			>
				<span class="navbar-toggler-icon"></span>
			</button>

			<!-- Collapsible navigation content -->
			<div class="collapse navbar-collapse" id="navbarNav">
				<!-- Main navigation links -->
				<ul class="navbar-nav me-auto">
					{#each navItems as item}
						{#if !item.permission || $hasPermission(item.permission.resource, item.permission.action)}
							<li class="nav-item">
								<a href={item.href} class="nav-link">
									<span class="me-1">{item.icon}</span>
									{item.label}
								</a>
							</li>
						{/if}
					{/each}
				</ul>

				<!-- User menu -->
				<div class="d-flex align-items-center">
					<!-- User info -->
					<div class="text-light me-3 d-none d-md-block">
						<div class="fw-semibold">{$user?.display_name || $user?.username || 'User'}</div>
						{#if $user?.email}
							<div class="small opacity-75">{$user.email}</div>
						{/if}
					</div>

					<!-- User dropdown for mobile -->
					<div class="dropdown d-md-none">
						<button
							class="btn btn-outline-light btn-sm dropdown-toggle"
							type="button"
							data-bs-toggle="dropdown"
							aria-expanded="false"
						>
							{$user?.username || 'User'}
						</button>
						<ul class="dropdown-menu dropdown-menu-end">
							<li><h6 class="dropdown-header">{$user?.display_name || $user?.username || 'User'}</h6></li>
							{#if $user?.email}
								<li><span class="dropdown-item-text small text-muted">{$user.email}</span></li>
								<li><hr class="dropdown-divider" /></li>
							{/if}
							<li>
								<div class="dropdown-item p-0">
									<LogoutButton />
								</div>
							</li>
						</ul>
					</div>

					<!-- Logout button for desktop -->
					<div class="d-none d-md-block">
						<LogoutButton />
					</div>
				</div>
			</div>
		</div>
	</nav>
{/if}
