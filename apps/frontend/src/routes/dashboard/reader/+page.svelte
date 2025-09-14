<script lang="ts">
  import { api } from '$lib/api';
  import { goto } from '$app/navigation';
  import { onMount } from 'svelte';
  let loading = true;
  let error: string | null = null;
  let incoming: any[] = [];
  let balance: any = { balance_cents: 0, stripe: { connected: false } };
  let polling: any;

  async function load() {
    try {
      const [inc, bal] = await Promise.all([
        api.get('/sessions/incoming'),
        api.get('/readers/me/balance')
      ]);
      incoming = inc.data.items;
      balance = bal.data;
    } catch (e: any) {
      error = e?.response?.data?.detail || e.message;
    } finally {
      loading = false;
    }
  }
  onMount(() => {
    load();
    polling = setInterval(load, 5000);
    return () => clearInterval(polling);
  });

  async function accept(uid: string) {
    await api.post(`/sessions/${uid}/accept`, {});
    await goto(`/session/${uid}`);
  }
  async function reject(uid: string) {
    await api.post(`/sessions/${uid}/reject`, {});
    await load();
  }
  async function onboard() {
    const { data } = await api.post('/connect/onboard_link', {});
    window.location.href = data.url;
  }
</script>

<section class="mx-auto max-w-6xl px-4 py-10">
  <h2 class="font-script text-4xl text-mystic-pink mb-6">Reader Dashboard</h2>
  {#if loading}
    <p class="text-white/70">Loading…</p>
  {:else}
    {#if error}
      <p class="text-red-400">{error}</p>
    {/if}
    <div class="grid gap-6 md:grid-cols-3">
      <div class="p-6 rounded-xl bg-white/5 ring-1 ring-white/10">
        <div class="text-white/70 text-sm">Balance</div>
        <div class="text-2xl font-display">${(balance.balance_cents/100).toFixed(2)}</div>
        {#if !balance.stripe.connected}
          <button class="mt-3 px-3 py-2 bg-mystic-pink text-black rounded" on:click={onboard}>Onboard payouts</button>
        {:else}
          <div class="text-white/60 text-sm mt-2">Payouts connected</div>
        {/if}
      </div>
      <div class="md:col-span-2 p-6 rounded-xl bg-white/5 ring-1 ring-white/10">
        <div class="flex items-center justify-between mb-3">
          <div class="font-display text-xl">Incoming requests</div>
          <button class="px-3 py-1 bg-white/10 rounded" on:click={load}>Refresh</button>
        </div>
        {#if incoming.length === 0}
          <p class="text-white/70">No requests right now.</p>
        {/if}
        <div class="space-y-3">
          {#each incoming as s}
            <div class="flex items-center justify-between p-4 bg-black/40 rounded border border-white/10">
              <div>
                <div class="font-display">Session {s.session_uid}</div>
                <div class="text-white/70 text-sm">Mode: {s.mode}</div>
              </div>
              <div class="flex gap-2">
                <button class="px-3 py-2 bg-mystic-gold text-black rounded" on:click={() => accept(s.session_uid)}>Accept</button>
                <button class="px-3 py-2 bg-white text-black rounded" on:click={() => reject(s.session_uid)}>Reject</button>
              </div>
            </div>
          {/each}
        </div>
      </div>
    </div>
  {/if}
</section>

<section class="mx-auto max-w-6xl px-4 py-10">
  <h2 class="font-script text-4xl text-mystic-pink mb-6">Reader Dashboard</h2>
  <div class="grid gap-6 md:grid-cols-3">
    <a class="p-6 rounded-xl bg-white/5 ring-1 ring-white/10 hover:ring-mystic-pink transition" href="/dashboard/reader/availability">Availability</a>
    <a class="p-6 rounded-xl bg-white/5 ring-1 ring-white/10 hover:ring-mystic-pink transition" href="/dashboard/reader/rates">Rates</a>
    <a class="p-6 rounded-xl bg-white/5 ring-1 ring-white/10 hover:ring-mystic-pink transition" href="/dashboard/reader/sessions">Live Sessions</a>
  </div>
</section>