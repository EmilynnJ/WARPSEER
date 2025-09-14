<script lang="ts">
  import { locales, locale, setLocale } from '$lib/i18n';
  let open = false;
</script>

<div class="relative">
  <button class="px-3 py-1 rounded bg-white/10 hover:bg-white/20" on:click={() => open = !open}>{$locale?.toUpperCase?.() || 'EN'}</button>
  {#if open}
    <div class="absolute right-0 mt-2 bg-black/70 border border-white/10 rounded shadow-lg">
      {#each $locales as l}
        <button class="block w-full text-left px-4 py-2 hover:bg-white/10" on:click={() => { setLocale(l); open = false; }}>{l.toUpperCase()}</button>
      {/each}
    </div>
  {/if}
</div>