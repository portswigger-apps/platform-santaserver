<script lang="ts">
	import { onMount } from 'svelte';

	let healthStatus = 'checking...';

	onMount(async () => {
		try {
			const response = await fetch('/api/v1/health');
			const data = await response.json();
			healthStatus = data.status;
		} catch (error) {
			healthStatus = 'error';
			console.error('Health check failed:', error);
		}
	});
</script>

<svelte:head>
	<title>Dashboard - SantaServer</title>
</svelte:head>

<div class="dashboard">
	<h2>Dashboard</h2>
	<div class="status-card">
		<h3>System Status</h3>
		<p class="status" class:healthy={healthStatus === 'healthy'} class:error={healthStatus === 'error'}>
			{healthStatus}
		</p>
	</div>

	<div class="grid">
		<div class="card">
			<h3>Pending Approvals</h3>
			<p class="number">0</p>
		</div>

		<div class="card">
			<h3>Active Rules</h3>
			<p class="number">0</p>
		</div>

		<div class="card">
			<h3>Connected Agents</h3>
			<p class="number">0</p>
		</div>
	</div>
</div>

<style>
	.dashboard {
		padding: 2rem;
		max-width: 1200px;
		margin: 0 auto;
	}

	h2 {
		margin: 0 0 2rem 0;
		color: #1f2937;
	}

	.status-card {
		background: white;
		border-radius: 0.5rem;
		padding: 1.5rem;
		box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
		margin-bottom: 2rem;
	}

	.status {
		font-size: 1.25rem;
		font-weight: bold;
		text-transform: capitalize;
	}

	.status.healthy {
		color: #10b981;
	}

	.status.error {
		color: #ef4444;
	}

	.grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
		gap: 1.5rem;
	}

	.card {
		background: white;
		border-radius: 0.5rem;
		padding: 1.5rem;
		box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
		text-align: center;
	}

	.card h3 {
		margin: 0 0 1rem 0;
		color: #6b7280;
		font-weight: 500;
	}

	.number {
		font-size: 2rem;
		font-weight: bold;
		color: #1f2937;
		margin: 0;
	}
</style>
