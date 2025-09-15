<script lang="ts">
  import { api } from '$lib/api';
  let streams: any[] = [];
  let error: string | null = null;
  async function loadStreams() {
    try {
      const { data } = await api.get('/streams');
      streams = data.items;
    } catch (e: any) {
      error = e?.response?.data?.detail || e.message;
    }
  }
  loadStreams();
</script>

<section class="mx-auto max-w-6xl px-4 py-10">
  <h2 class="font-script text-4xl text-mystic-pink mb-6">Live Streams</h2>
  {#if error}
    <p class="text-red-400">{error}</p>
  {/if}
  {#if streams.length === 0}
    <p class="text-white/80">No active streams right now.</p>
  {/if}
  <div class="grid md:grid-cols-3 gap-6 mt-4">
    {#each streams as s}
      <a class="p-6 rounded-xl bg-white/5 ring-1 ring-white/10 hover:ring-mystic-pink transition" href={`/stream/${s.session_uid}`}>
        <div class="font-display text-lg">Live with Reader #{s.reader_id}</div>
        <div class="text-white/70 text-sm">Started: {new Date(s.started_at).toLocaleString()}</div>
      </a>
    {/each}
  </div>
</section>