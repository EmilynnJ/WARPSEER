<script lang="ts">
  import { api } from '$lib/api';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import { onMount } from 'svelte';
  let reader_id = 0;
  let mode: 'chat' | 'voice' | 'video' = 'chat';
  let length = 30;
  let start_local = '';
  let error: string | null = null;
  let availability: any = { blocks: [], booked: [] };

  async function loadAvailability() {
    const now = new Date();
    const start = new Date(now.getTime() - 24*3600*1000).toISOString();
    const end = new Date(now.getTime() + 14*24*3600*1000).toISOString();
    const { data } = await api.get(`/readers/${reader_id}/availability`, { params: { start, end } });
    availability = data;
  }

  onMount(() => {
    reader_id = Number($page.params.reader_id);
    loadAvailability();
  });

  async function book() {
    try {
      const iso = new Date(start_local).toISOString();
      const { data } = await api.post('/appointments/book', { reader_id, mode, length_minutes: length, start_time: iso });
      await goto('/dashboard/client/appointments');
    } catch (e: any) {
      error = e?.response?.data?.detail || e.message;
    }
  }
</script>

<section class="mx-auto max-w-3xl px-4 py-10">
  <h2 class="font-script text-4xl text-mystic-pink mb-6">Schedule Reading</h2>
  {#if error}<p class="text-red-400 mb-4">{error}</p>{/if}
  <div class="space-y-4 p-6 bg-white/5 rounded-xl ring-1 ring-white/10">
    <label class="block">Mode
      <select bind:value={mode} class="mt-2 bg-black/40 rounded px-3 py-2">
        <option value="chat">Chat</option>
        <option value="voice">Voice</option>
        <option value="video">Video</option>
      </select>
    </label>
    <label class="block">Length (minutes)
      <select bind:value={length} class="mt-2 bg-black/40 rounded px-3 py-2">
        <option value="15">15</option>
        <option value="30">30</option>
        <option value="45">45</option>
        <option value="60">60</option>
      </select>
    </label>
    <label class="block">Start time
      <input type="datetime-local" bind:value={start_local} class="mt-2 bg-black/40 rounded px-3 py-2" />
    </label>
    <button class="px-4 py-2 bg-mystic-gold text-black rounded" on:click={book}>Book</button>
  </div>
  <div class="mt-8">
    <h3 class="font-display text-xl mb-2">Reader Availability (next 2 weeks)</h3>
    <ul class="space-y-2">
      {#each availability.blocks as b}
        <li class="text-white/80 text-sm">{new Date(b.start_time).toLocaleString()} - {new Date(b.end_time).toLocaleString()} ({b.timezone})</li>
      {/each}
    </ul>
  </div>
</section>