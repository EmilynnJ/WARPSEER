<script lang="ts">
  import '../app.css';
  export let data;
</script>

<nav class="sticky top-0 z-40 backdrop-blur bg-black/40 border-b border-white/10 supports-[backdrop-filter]:bg-black/30">
  <div class="mx-auto max-w-6xl px-4 py-3 flex items-center justify-between">
    <a href="/" class="font-script text-3xl text-mystic-pink">SoulSeer</a>
    <div class="flex items-center gap-4 text-white/90">
      <a href="/readings" class="hover:text-mystic-pink">Readings</a>
      <a href="/live" class="hover:text-mystic-pink">Live</a>
      <a href="/shop" class="hover:text-mystic-pink">Shop</a>
      <a href="/about" class="hover:text-mystic-pink">About</a>
      <a href="/dashboard" class="hover:text-mystic-pink">Dashboard</a>
      <a href="/wallet" class="hover:text-mystic-pink">Add Funds</a>
    </div>
  </div>
</nav>
<div class="min-h-screen bg-black/70">
  <slot />
</div>
