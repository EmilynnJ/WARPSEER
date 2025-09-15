<script lang="ts">
  import { api } from '$lib/api';
  let readers: any[] = [];
  let error: string | null = null;
  async function loadReaders() {
    try {
      const { data } = await api.get('/readers');
      readers = data.items;
    } catch (e: any) {
      error = e?.response?.data?.detail || e.message;
    }
  }
  loadReaders();
</script>

<section class="mx-auto max-w-6xl px-4 py-10">
  <h2 class="font-script text-4xl text-mystic-pink mb-6">Find a Reader</h2>
  <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
    {#if error}
      <p class="text-red-400">{error}</p>
    {/if}
    {#each readers as r}
      <div class="p-6 rounded-xl bg-white/5 ring-1 ring-white/10 hover:ring-mystic-pink transition">
        <div class="flex items-center gap-3">
          <img src={r.avatar_url || 'https://placehold.co/80x80?text=SS'} alt={r.display_name} class="w-16 h-16 rounded-full object-cover ring-2 ring-mystic-gold/50" />
          <div>
            <h3 class="font-display text-lg">{r.display_name}</h3>
            <p class="text-white/70 text-sm">Chat ${r.rate_chat_ppm/100}/min • Voice ${r.rate_voice_ppm/100}/min • Video ${r.rate_video_ppm/100}/min</p>
          </div>
        </div>
        <div class="mt-4 flex gap-2">
          <a class="px-3 py-2 bg-mystic-pink text-black rounded" href={`/session/request?reader_id=${r.user_id}&mode=chat`}>Chat</a>
          <a class="px-3 py-2 bg-mystic-gold text-black rounded" href={`/session/request?reader_id=${r.user_id}&mode=voice`}>Voice</a>
          <a class="px-3 py-2 bg-white text-black rounded" href={`/session/request?reader_id=${r.user_id}&mode=video`}>Video</a>
          <a class="px-3 py-2 bg-white/80 text-black rounded" href={`/schedule/${r.user_id}`}>Schedule</a>
        </div>
      </div>
    {/each}
  </div>
</section>