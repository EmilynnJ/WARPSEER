<script lang="ts">
  import { t } from '$lib/i18n';
  const hero = 'https://i.postimg.cc/tRLSgCPb/HERO-IMAGE-1.jpg';
</script>

<section class="mx-auto max-w-6xl px-4 py-8">
  <header class="text-center py-8">
    <h1 class="font-script text-6xl md:text-7xl text-mystic-pink">SoulSeer</h1>
    <p class="font-display text-xl md:text-2xl text-white/90">{$t('home.tagline')}</p>
  </header>
  <div class="rounded-2xl overflow-hidden shadow-2xl ring-1 ring-mystic-gold/30">
    <img src={hero} alt="SoulSeer Hero" class="w-full object-cover max-h-[460px]" />
  </div>
  <div class="mt-8 grid gap-6 md:grid-cols-3">
    <a class="block p-6 rounded-xl bg-white/5 ring-1 ring-white/10 hover:ring-mystic-pink transition" href="/readings">Readings</a>
    <a class="block p-6 rounded-xl bg-white/5 ring-1 ring-white/10 hover:ring-mystic-pink transition" href="/live">Live</a>
    <a class="block p-6 rounded-xl bg-white/5 ring-1 ring-white/10 hover:ring-mystic-pink transition" href="/shop">Shop</a>
  </div>
</section>