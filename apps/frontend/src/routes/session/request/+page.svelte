<script lang="ts">
  import { page } from '$app/stores';
  import { api } from '$lib/api';
  import { goto } from '$app/navigation';
  let error: string | null = null;
  $: reader_id = Number(new URL($page.url).searchParams.get('reader_id'));
  $: mode = new URL($page.url).searchParams.get('mode') || 'chat';
  async function start() {
    try {
      const { data } = await api.post('/sessions/request', { reader_id, mode });
      await goto(`/session/${data.session_uid}`);
    } catch (e: any) {
      error = e?.response?.data?.detail || e.message;
    }
  }
  start();
</script>

<section class="mx-auto max-w-xl px-4 py-10">
  <h2 class="font-script text-4xl text-mystic-pink mb-4">Creating session…</h2>
  {#if error}<p class="text-red-400">{error}</p>{/if}
</section>