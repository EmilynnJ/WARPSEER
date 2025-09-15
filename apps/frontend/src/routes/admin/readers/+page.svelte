<script lang="ts">
  import { onMount } from 'svelte';
  import { PUBLIC_BACKEND_URL } from '$env/static/public';
  
  interface Reader {
    id: number;
    email: string;
    display_name: string;
    bio: string;
    status: string;
    rate_per_min_cents: number;
    total_earnings_cents: number;
    created_at: string;
  }
  
  let readers: Reader[] = [];
  let loading = true;
  let error = '';
  let showCreateModal = false;
  
  // New reader form
  let newReader = {
    email: '',
    password: '',
    display_name: '',
    bio: '',
    rate_per_min_cents: 500
  };
  
  onMount(async () => {
    await loadReaders();
  });
  
  async function loadReaders() {
    try {
      loading = true;
      const token = localStorage.getItem('auth_token');
      const res = await fetch(`${PUBLIC_BACKEND_URL}/api/admin/users?role=reader`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (!res.ok) throw new Error('Failed to load readers');
      
      const data = await res.json();
      readers = data.users;
    } catch (err) {
      error = 'Failed to load readers';
      console.error(err);
    } finally {
      loading = false;
    }
  }
  
  async function createReader() {
    try {
      const token = localStorage.getItem('auth_token');
      const res = await fetch(`${PUBLIC_BACKEND_URL}/api/admin/create-reader`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(newReader)
      });
      
      if (!res.ok) {
        const error = await res.json();
        throw new Error(error.detail || 'Failed to create reader');
      }
      
      // Reset form and reload
      newReader = {
        email: '',
        password: '',
        display_name: '',
        bio: '',
        rate_per_min_cents: 500
      };
      showCreateModal = false;
      await loadReaders();
      
      alert('Reader account created successfully');
    } catch (err: any) {
      alert(err.message || 'Failed to create reader');
    }
  }
  
  async function toggleReaderStatus(readerId: number, currentStatus: string) {
    const newStatus = currentStatus === 'active' ? 'suspended' : 'active';
    
    try {
      const token = localStorage.getItem('auth_token');
      const res = await fetch(`${PUBLIC_BACKEND_URL}/api/admin/users/${readerId}/status`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ status: newStatus })
      });
      
      if (!res.ok) throw new Error('Failed to update status');
      
      await loadReaders();
    } catch (err) {
      alert('Failed to update reader status');
    }
  }
  
  function formatCurrency(cents: number): string {
    return `$${(cents / 100).toFixed(2)}`;
  }
  
  function formatDate(dateStr: string): string {
    return new Date(dateStr).toLocaleDateString();
  }
</script>

<svelte:head>
  <title>Manage Readers - Admin - SoulSeer</title>
</svelte:head>

<div class="min-h-screen bg-mystic-dark text-white p-4">
  <div class="max-w-7xl mx-auto">
    <div class="flex justify-between items-center mb-8">
      <h1 class="text-4xl font-script text-mystic-pink">Manage Readers</h1>
      <button
        on:click={() => showCreateModal = true}
        class="bg-gradient-to-r from-mystic-pink to-mystic-purple px-6 py-2 rounded-lg hover:opacity-90 transition"
      >
        + Create Reader Account
      </button>
    </div>
    
    {#if loading}
      <div class="flex justify-center items-center h-64">
        <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-mystic-pink"></div>
      </div>
    {:else if error}
      <div class="text-center text-red-400 py-8">{error}</div>
    {:else}
      <!-- Readers Table -->
      <div class="bg-black/50 rounded-lg border border-mystic-purple overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead class="bg-black/50 border-b border-mystic-purple">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                  Reader
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                  Rate
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                  Total Earnings
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                  Status
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                  Joined
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-800">
              {#each readers as reader}
                <tr class="hover:bg-black/30 transition">
                  <td class="px-6 py-4">
                    <div>
                      <div class="text-sm font-medium">{reader.display_name}</div>
                      <div class="text-xs text-gray-400">{reader.email}</div>
                    </div>
                  </td>
                  <td class="px-6 py-4 text-sm">
                    {formatCurrency(reader.rate_per_min_cents)}/min
                  </td>
                  <td class="px-6 py-4 text-sm">
                    {formatCurrency(reader.total_earnings_cents)}
                  </td>
                  <td class="px-6 py-4">
                    <span class="px-2 py-1 text-xs rounded-full {reader.status === 'active' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}">
                      {reader.status}
                    </span>
                  </td>
                  <td class="px-6 py-4 text-sm text-gray-400">
                    {formatDate(reader.created_at)}
                  </td>
                  <td class="px-6 py-4 text-sm">
                    <div class="flex gap-2">
                      <button
                        on:click={() => toggleReaderStatus(reader.id, reader.status)}
                        class="text-mystic-pink hover:underline"
                      >
                        {reader.status === 'active' ? 'Suspend' : 'Activate'}
                      </button>
                      <a
                        href="/admin/readers/{reader.id}"
                        class="text-mystic-purple hover:underline"
                      >
                        Edit
                      </a>
                    </div>
                  </td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
      </div>
    {/if}
  </div>
  
  <!-- Create Reader Modal -->
  {#if showCreateModal}
    <div class="fixed inset-0 bg-black/70 flex items-center justify-center p-4 z-50">
      <div class="bg-mystic-dark border border-mystic-purple rounded-lg p-6 max-w-md w-full">
        <h2 class="text-2xl font-semibold text-mystic-pink mb-4">Create Reader Account</h2>
        
        <div class="space-y-4">
          <div>
            <label class="block text-sm mb-1">Email *</label>
            <input
              type="email"
              bind:value={newReader.email}
              class="w-full bg-black/50 border border-mystic-purple rounded-lg px-3 py-2 focus:outline-none focus:border-mystic-pink"
              required
            />
          </div>
          
          <div>
            <label class="block text-sm mb-1">Password *</label>
            <input
              type="password"
              bind:value={newReader.password}
              class="w-full bg-black/50 border border-mystic-purple rounded-lg px-3 py-2 focus:outline-none focus:border-mystic-pink"
              required
            />
          </div>
          
          <div>
            <label class="block text-sm mb-1">Display Name *</label>
            <input
              type="text"
              bind:value={newReader.display_name}
              class="w-full bg-black/50 border border-mystic-purple rounded-lg px-3 py-2 focus:outline-none focus:border-mystic-pink"
              required
            />
          </div>
          
          <div>
            <label class="block text-sm mb-1">Bio</label>
            <textarea
              bind:value={newReader.bio}
              rows="3"
              class="w-full bg-black/50 border border-mystic-purple rounded-lg px-3 py-2 focus:outline-none focus:border-mystic-pink"
            ></textarea>
          </div>
          
          <div>
            <label class="block text-sm mb-1">Rate per Minute (cents) *</label>
            <input
              type="number"
              bind:value={newReader.rate_per_min_cents}
              min="100"
              class="w-full bg-black/50 border border-mystic-purple rounded-lg px-3 py-2 focus:outline-none focus:border-mystic-pink"
              required
            />
            <p class="text-xs text-gray-400 mt-1">
              Current: {formatCurrency(newReader.rate_per_min_cents)}/min
            </p>
          </div>
        </div>
        
        <div class="flex gap-3 mt-6">
          <button
            on:click={createReader}
            class="flex-1 bg-gradient-to-r from-mystic-pink to-mystic-purple py-2 rounded-lg hover:opacity-90 transition"
          >
            Create Reader
          </button>
          <button
            on:click={() => showCreateModal = false}
            class="flex-1 bg-white/10 hover:bg-white/20 py-2 rounded-lg transition"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  {/if}
</div>