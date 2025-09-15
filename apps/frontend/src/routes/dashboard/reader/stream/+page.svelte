<script lang="ts">
  import { api } from '$lib/api';
  import { goto } from '$app/navigation';
  let loading = false;
  let error: string | null = null;

  async function startStream() {
    loading = true;
    try {
      const { data } = await api.post('/streams/start', {});
      await goto(`/stream/${data.session_uid}`);
    } catch (e: any) {
      error = e?.response?.data?.detail || e.message;
    } finally {
      loading = false;
    }
  }
</script>

<section class="mx-auto max-w-3xl px-4 py-10">
  <h2 class="font-script text-4xl text-mystic-pink mb-6">Start Live Stream</h2>
  {#if error}<p class="text-red-400">{error}</p>{/if}
  <div class="p-6 rounded-xl bg-white/5 ring-1 ring-white/10">
    <p class="text-white/80 mb-4">Go live to connect with viewers. They can send gifts to support you.</p>
    <button 
      class="px-4 py-2 bg-mystic-gold text-black rounded" 
      on:click={startStream}
      disabled={loading}
    >
      {loading ? 'Starting...' : 'Go Live'}
    </button>
  </div>
</section>