<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { PUBLIC_BACKEND_URL } from '$env/static/public';
  
  interface Stats {
    total_users: number;
    total_readers: number;
    total_clients: number;
    total_sessions: number;
    total_revenue: number;
    active_streams: number;
    pending_appointments: number;
    total_products: number;
  }
  
  let loading = true;
  let stats: Stats | null = null;
  let error = '';
  let userRole = '';
  
  onMount(async () => {
    // Check if user is admin
    userRole = localStorage.getItem('user_role') || '';
    if (userRole !== 'admin') {
      goto('/');
      return;
    }
    
    await loadStats();
  });
  
  async function loadStats() {
    try {
      loading = true;
      const token = localStorage.getItem('auth_token');
      const res = await fetch(`${PUBLIC_BACKEND_URL}/api/admin/stats`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (!res.ok) throw new Error('Failed to load stats');
      
      stats = await res.json();
    } catch (err) {
      error = 'Failed to load admin statistics';
      console.error(err);
    } finally {
      loading = false;
    }
  }
  
  function formatCurrency(cents: number): string {
    return `$${(cents / 100).toFixed(2)}`;
  }
</script>

<svelte:head>
  <title>Admin Dashboard - SoulSeer</title>
</svelte:head>

<div class="min-h-screen bg-mystic-dark text-white p-4">
  <div class="max-w-7xl mx-auto">
    <h1 class="text-4xl font-script text-mystic-pink mb-8">Admin Dashboard</h1>
    
    {#if loading}
      <div class="flex justify-center items-center h-64">
        <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-mystic-pink"></div>
      </div>
    {:else if error}
      <div class="text-center text-red-400 py-8">{error}</div>
    {:else if stats}
      <!-- Stats Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div class="bg-black/50 rounded-lg p-6 border border-mystic-purple">
          <div class="flex items-center justify-between mb-2">
            <h3 class="text-gray-400 text-sm">Total Users</h3>
            <svg class="w-6 h-6 text-mystic-pink" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
          </div>
          <p class="text-3xl font-bold">{stats.total_users}</p>
          <p class="text-sm text-gray-400 mt-1">
            {stats.total_readers} readers, {stats.total_clients} clients
          </p>
        </div>
        
        <div class="bg-black/50 rounded-lg p-6 border border-mystic-purple">
          <div class="flex items-center justify-between mb-2">
            <h3 class="text-gray-400 text-sm">Total Sessions</h3>
            <svg class="w-6 h-6 text-mystic-pink" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
            </svg>
          </div>
          <p class="text-3xl font-bold">{stats.total_sessions}</p>
          <p class="text-sm text-gray-400 mt-1">All-time sessions</p>
        </div>
        
        <div class="bg-black/50 rounded-lg p-6 border border-mystic-purple">
          <div class="flex items-center justify-between mb-2">
            <h3 class="text-gray-400 text-sm">Total Revenue</h3>
            <svg class="w-6 h-6 text-mystic-pink" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <p class="text-3xl font-bold">{formatCurrency(stats.total_revenue)}</p>
          <p class="text-sm text-gray-400 mt-1">Platform earnings</p>
        </div>
        
        <div class="bg-black/50 rounded-lg p-6 border border-mystic-purple">
          <div class="flex items-center justify-between mb-2">
            <h3 class="text-gray-400 text-sm">Active Now</h3>
            <svg class="w-6 h-6 text-mystic-pink" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5.636 18.364a9 9 0 010-12.728m12.728 0a9 9 0 010 12.728m-9.9-2.829a5 5 0 010-7.07m7.072 0a5 5 0 010 7.07M13 12a1 1 0 11-2 0 1 1 0 012 0z" />
            </svg>
          </div>
          <p class="text-3xl font-bold">{stats.active_streams}</p>
          <p class="text-sm text-gray-400 mt-1">Live streams</p>
        </div>
      </div>
      
      <!-- Quick Actions -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <button
          on:click={() => goto('/admin/users')}
          class="bg-gradient-to-r from-mystic-pink to-mystic-purple rounded-lg p-6 hover:opacity-90 transition text-left"
        >
          <svg class="w-8 h-8 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
          </svg>
          <h3 class="text-lg font-semibold">Manage Users</h3>
          <p class="text-sm opacity-80 mt-1">View and manage all users</p>
        </button>
        
        <button
          on:click={() => goto('/admin/readers')}
          class="bg-gradient-to-r from-mystic-purple to-mystic-pink rounded-lg p-6 hover:opacity-90 transition text-left"
        >
          <svg class="w-8 h-8 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <h3 class="text-lg font-semibold">Reader Accounts</h3>
          <p class="text-sm opacity-80 mt-1">Create and manage readers</p>
        </button>
        
        <button
          on:click={() => goto('/admin/products')}
          class="bg-gradient-to-r from-mystic-pink to-mystic-purple rounded-lg p-6 hover:opacity-90 transition text-left"
        >
          <svg class="w-8 h-8 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
          </svg>
          <h3 class="text-lg font-semibold">Products</h3>
          <p class="text-sm opacity-80 mt-1">Manage marketplace products</p>
        </button>
        
        <button
          on:click={() => goto('/admin/analytics')}
          class="bg-gradient-to-r from-mystic-purple to-mystic-pink rounded-lg p-6 hover:opacity-90 transition text-left"
        >
          <svg class="w-8 h-8 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          <h3 class="text-lg font-semibold">Analytics</h3>
          <p class="text-sm opacity-80 mt-1">View platform analytics</p>
        </button>
      </div>
      
      <!-- Recent Activity -->
      <div class="mt-8 bg-black/50 rounded-lg p-6 border border-mystic-purple">
        <h2 class="text-xl font-semibold mb-4">Recent Activity</h2>
        <div class="space-y-3">
          <div class="flex items-center gap-3 text-sm">
            <span class="text-gray-400">5 min ago</span>
            <span>New user registration</span>
          </div>
          <div class="flex items-center gap-3 text-sm">
            <span class="text-gray-400">12 min ago</span>
            <span>Session completed (#1234)</span>
          </div>
          <div class="flex items-center gap-3 text-sm">
            <span class="text-gray-400">25 min ago</span>
            <span>Product order placed</span>
          </div>
          <div class="flex items-center gap-3 text-sm">
            <span class="text-gray-400">1 hour ago</span>
            <span>Stream started by Reader Jane</span>
          </div>
        </div>
      </div>
    {/if}
  </div>
</div>