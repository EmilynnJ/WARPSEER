<script lang="ts">
  import '../app.css';
  import { t } from '$lib/i18n';
  import LangSwitcher from '$lib/components/LangSwitcher.svelte';
  
  export let data;
</script>

<nav class="sticky top-0 z-40 backdrop-blur bg-black/40 border-b border-white/10 supports-[backdrop-filter]:bg-black/30">
  <div class="mx-auto max-w-6xl px-4 py-3 flex items-center justify-between">
    <a href="/" class="font-script text-3xl text-mystic-pink">SoulSeer</a>
    <div class="flex items-center gap-4 text-white/90">
      <a href="/readings" class="hover:text-mystic-pink">{$t('nav.readings')}</a>
      <a href="/live" class="hover:text-mystic-pink">{$t('nav.live')}</a>
      <a href="/shop" class="hover:text-mystic-pink">{$t('nav.shop')}</a>
      <a href="/about" class="hover:text-mystic-pink">{$t('nav.about')}</a>
      <a href="/dashboard" class="hover:text-mystic-pink">{$t('nav.dashboard')}</a>
      <a href="/wallet" class="hover:text-mystic-pink">{$t('nav.wallet')}</a>
      <LangSwitcher />
    </div>
  </div>
</nav>
<div class="min-h-screen bg-black/70">
  <slot />
</div>
