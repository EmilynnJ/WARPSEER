<script lang="ts">
  import { api } from '$lib/api';
  import { onMount } from 'svelte';
  let upcoming: any[] = [];
  let error: string | null = null;
  async function load() {
    try { const { data } = await api.get('/appointments/reader'); upcoming = data.upcoming; }
    catch (e: any) { error = e?.response?.data?.detail || e.message; }
  }
  onMount(load);
</script>

<section class="mx-auto max-w-5xl px-4 py-10">
  <h2 class="font-script text-4xl text-mystic-pink mb-6">Reader Appointments</h2>
  {#if error}<p class="text-red-400">{error}</p>{/if}
  {#if upcoming.length === 0}
    <p class="text-white/70">No upcoming bookings.</p>
  {/if}
  <div class="space-y-3">
    {#each upcoming as a}
      <div class="p-4 bg-black/40 rounded border border-white/10">
        <div class="font-display">{a.mode} • {a.length_minutes} min</div>
        <div class="text-white/70 text-sm">{new Date(a.start_time).toLocaleString()}</div>
        <div class="text-white/70 text-sm">Client #{a.client_id}</div>
      </div>
    {/each}
  </div>
</section>