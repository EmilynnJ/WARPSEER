<script lang="ts">
  import { onMount } from 'svelte';
  import { loadClerk } from '$lib/auth';
  let error: string | null = null;
  onMount(async () => {
    try {
      await loadClerk();
      const el = document.getElementById('sign-in');
      // @ts-ignore
      window.Clerk?.mountSignIn(el);
    } catch (e) {
      error = 'Failed to load auth. Check Clerk keys and domain.';
    }
  });
</script>

<section class="mx-auto max-w-md px-4 py-16">
  <h2 class="font-script text-5xl text-mystic-pink mb-6">Login</h2>
  {#if error}
    <p class="text-red-400">{error}</p>
  {/if}
  <div id="sign-in" class="rounded-xl bg-white/5 ring-1 ring-white/10 p-6"></div>
</section>