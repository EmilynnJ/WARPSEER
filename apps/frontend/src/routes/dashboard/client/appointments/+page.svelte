<script lang="ts">
  import { api } from '$lib/api';
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  let data: any = { upcoming: [], history: [] };
  let error: string | null = null;

  async function load() {
    try {
      const res = await api.get('/appointments/me');
      data = res.data;
    } catch (e: any) {
      error = e?.response?.data?.detail || e.message;
    }
  }
  onMount(load);

  async function start(booking_uid: string) {
    try {
      const res = await api.post(`/appointments/${booking_uid}/start`, {});
      await goto(`/session/${res.data.session_uid}`);
    } catch (e: any) { error = e?.response?.data?.detail || e.message; }
  }
  async function cancel(booking_uid: string) {
    try {
      await api.post(`/appointments/${booking_uid}/cancel`, {});
      await load();
    } catch (e: any) { error = e?.response?.data?.detail || e.message; }
  }
</script>

<section class="mx-auto max-w-5xl px-4 py-10">
  <h2 class="font-script text-4xl text-mystic-pink mb-6">My Appointments</h2>
  {#if error}<p class="text-red-400">{error}</p>{/if}
  <div class="grid md:grid-cols-2 gap-6">
    <div class="p-6 rounded-xl bg-white/5 ring-1 ring-white/10">
      <div class="font-display text-xl mb-3">Upcoming</div>
      {#if data.upcoming.length === 0}
        <p class="text-white/70">No upcoming bookings.</p>
      {/if}
      <div class="space-y-3">
        {#each data.upcoming as a}
          <div class="p-4 bg-black/40 rounded border border-white/10">
            <div class="font-display">{a.mode} • {a.length_minutes} min</div>
            <div class="text-white/70 text-sm">{new Date(a.start_time).toLocaleString()}</div>
            <div class="mt-2 flex gap-2">
              <button class="px-3 py-2 bg-mystic-gold text-black rounded" on:click={() => start(a.booking_uid)}>Join</button>
              <button class="px-3 py-2 bg-white text-black rounded" on:click={() => cancel(a.booking_uid)}>Cancel</button>
            </div>
          </div>
        {/each}
      </div>
    </div>
    <div class="p-6 rounded-xl bg-white/5 ring-1 ring-white/10">
      <div class="font-display text-xl mb-3">History</div>
      {#if data.history.length === 0}
        <p class="text-white/70">No past bookings.</p>
      {/if}
      <div class="space-y-3">
        {#each data.history as a}
          <div class="p-4 bg-black/40 rounded border border-white/10">
            <div class="font-display">{a.mode} • {a.length_minutes} min</div>
            <div class="text-white/70 text-sm">{new Date(a.start_time).toLocaleString()}</div>
            <div class="text-white/70 text-sm">{a.status}</div>
          </div>
        {/each}
      </div>
    </div>
  </div>
</section>