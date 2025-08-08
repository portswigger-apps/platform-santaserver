<script lang="ts">
	import { onMount } from 'svelte';
	import { user } from '$lib/auth/stores';

	let healthStatus = 'checking...';
	let healthStatusClass = 'warning';

	onMount(async () => {
		try {
			const response = await fetch('/api/v1/health');
			const data = await response.json();
			healthStatus = data.status;
			healthStatusClass = data.status === 'healthy' ? 'success' : 'danger';
		} catch (error) {
			healthStatus = 'error';
			healthStatusClass = 'danger';
			console.error('Health check failed:', error);
		}
	});

	// Get greeting based on time of day
	const getGreeting = () => {
		const hour = new Date().getHours();
		if (hour < 12) return 'Good morning';
		if (hour < 18) return 'Good afternoon';
		return 'Good evening';
	};
</script>

<svelte:head>
	<title>Dashboard - SantaServer</title>
</svelte:head>

<div class="container-fluid py-4">
	<!-- Welcome header -->
	<div class="row mb-4">
		<div class="col-12">
			<div class="d-flex justify-content-between align-items-center">
				<div>
					<h1 class="h2 mb-1">
						{getGreeting()}, {$user?.display_name || $user?.username || 'User'}!
					</h1>
					<p class="text-muted mb-0">Welcome to SantaServer Enterprise Management</p>
				</div>
				<div class="text-end">
					<small class="text-muted">
						{new Date().toLocaleDateString('en-US', {
							weekday: 'long',
							year: 'numeric',
							month: 'long',
							day: 'numeric'
						})}
					</small>
				</div>
			</div>
		</div>
	</div>

	<!-- System Status Card -->
	<div class="row mb-4">
		<div class="col-12">
			<div class="card">
				<div class="card-body">
					<div class="d-flex align-items-center">
						<div class="me-3">
							<i class="bi bi-shield-check fs-1 text-{healthStatusClass}"></i>
						</div>
						<div>
							<h5 class="card-title mb-1">System Status</h5>
							<div class="card-text">
								<span class="badge bg-{healthStatusClass} text-capitalize fs-6">
									{#if healthStatus === 'checking...'}
										<div class="spinner-border spinner-border-sm me-1" role="status">
											<span class="visually-hidden">Loading...</span>
										</div>
									{/if}
									{healthStatus}
								</span>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>

	<!-- Statistics Cards -->
	<div class="row g-4 mb-4">
		<div class="col-lg-4 col-md-6">
			<div class="card text-center h-100">
				<div class="card-body d-flex flex-column justify-content-center">
					<div class="mb-3">
						<i class="bi bi-clock-history fs-1 text-warning"></i>
					</div>
					<h5 class="card-title">Pending Approvals</h5>
					<h2 class="display-4 text-warning mb-0">0</h2>
					<small class="text-muted">Awaiting review</small>
				</div>
			</div>
		</div>

		<div class="col-lg-4 col-md-6">
			<div class="card text-center h-100">
				<div class="card-body d-flex flex-column justify-content-center">
					<div class="mb-3">
						<i class="bi bi-shield-check fs-1 text-success"></i>
					</div>
					<h5 class="card-title">Active Rules</h5>
					<h2 class="display-4 text-success mb-0">0</h2>
					<small class="text-muted">Currently enforced</small>
				</div>
			</div>
		</div>

		<div class="col-lg-4 col-md-6">
			<div class="card text-center h-100">
				<div class="card-body d-flex flex-column justify-content-center">
					<div class="mb-3">
						<i class="bi bi-pc-display fs-1 text-primary"></i>
					</div>
					<h5 class="card-title">Connected Agents</h5>
					<h2 class="display-4 text-primary mb-0">0</h2>
					<small class="text-muted">Online endpoints</small>
				</div>
			</div>
		</div>
	</div>

	<!-- Quick Actions -->
	<div class="row">
		<div class="col-12">
			<div class="card">
				<div class="card-header">
					<h5 class="card-title mb-0">Quick Actions</h5>
				</div>
				<div class="card-body">
					<div class="row g-3">
						<div class="col-lg-3 col-md-6">
							<a href="/rules" class="btn btn-outline-primary w-100">
								<i class="bi bi-plus-circle me-2"></i>
								Create Rule
							</a>
						</div>
						<div class="col-lg-3 col-md-6">
							<a href="/approvals" class="btn btn-outline-success w-100">
								<i class="bi bi-check-circle me-2"></i>
								Review Approvals
							</a>
						</div>
						<div class="col-lg-3 col-md-6">
							<a href="/users" class="btn btn-outline-info w-100">
								<i class="bi bi-people me-2"></i>
								Manage Users
							</a>
						</div>
						<div class="col-lg-3 col-md-6">
							<a href="/system" class="btn btn-outline-secondary w-100">
								<i class="bi bi-gear me-2"></i>
								System Settings
							</a>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
</div>
