<script lang="ts">
  import { api } from '$lib/api';
  import { onMount } from 'svelte';
  let start_local = '';
  let end_local = '';
  let timezone = Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC';
  let message: string | null = null;
  let error: string | null = null;

  async function add() {
    try {
      const start_time = new Date(start_local).toISOString();
      const end_time = new Date(end_local).toISOString();
      await api.post('/readers/me/availability', { start_time, end_time, timezone });
      message = 'Availability block added.';
      error = null;
    } catch (e: any) {
      error = e?.response?.data?.detail || e.message; message = null;
    }
  }
</script>

<section class="mx-auto max-w-3xl px-4 py-10">
  <h2 class="font-script text-4xl text-mystic-pink mb-6">Set Availability</h2>
  {#if message}<p class="text-green-400">{message}</p>{/if}
  {#if error}<p class="text-red-400">{error}</p>{/if}
  <div class="space-y-4 p-6 bg-white/5 rounded-xl ring-1 ring-white/10">
    <label class="block">Start
      <input type="datetime-local" bind:value={start_local} class="mt-2 bg-black/40 rounded px-3 py-2" />
    </label>
    <label class="block">End
      <input type="datetime-local" bind:value={end_local} class="mt-2 bg-black/40 rounded px-3 py-2" />
    </label>
    <label class="block">Timezone
      <input type="text" bind:value={timezone} class="mt-2 bg-black/40 rounded px-3 py-2" />
    </label>
    <button class="px-4 py-2 bg-mystic-gold text-black rounded" on:click={add}>Add</button>
  </div>
</section>