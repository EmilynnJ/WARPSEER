<script lang="ts">
  import { onMount } from 'svelte';
  
  export let error: Error | null = null;
  export let reset: () => void = () => window.location.reload();
  
  let showDetails = false;
  
  onMount(() => {
    if (error) {
      console.error('Error boundary caught:', error);
      // Send error to monitoring service
      if (typeof window !== 'undefined' && 'Sentry' in window) {
        (window as any).Sentry.captureException(error);
      }
    }
  });
</script>

{#if error}
  <div class="min-h-screen bg-mystic-dark flex items-center justify-center p-4">
    <div class="max-w-md w-full bg-black/50 rounded-lg border border-mystic-purple p-8 text-center">
      <div class="mb-6">
        <svg class="w-20 h-20 mx-auto text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
      </div>
      
      <h1 class="text-2xl font-semibold text-mystic-pink mb-3">
        Oops! Something went wrong
      </h1>
      
      <p class="text-gray-300 mb-6">
        The cosmic energies seem to be misaligned. We've been notified and are working to restore balance.
      </p>
      
      <div class="space-y-3">
        <button
          on:click={reset}
          class="w-full bg-gradient-to-r from-mystic-pink to-mystic-purple py-2 rounded-lg hover:opacity-90 transition"
        >
          Try Again
        </button>
        
        <button
          on:click={() => showDetails = !showDetails}
          class="w-full bg-white/10 hover:bg-white/20 py-2 rounded-lg transition text-sm"
        >
          {showDetails ? 'Hide' : 'Show'} Technical Details
        </button>
      </div>
      
      {#if showDetails}
        <div class="mt-6 p-4 bg-black/50 rounded-lg text-left">
          <p class="text-xs text-gray-400 font-mono break-all">
            {error.message}
          </p>
          {#if error.stack}
            <pre class="text-xs text-gray-500 mt-2 overflow-x-auto">{error.stack}</pre>
          {/if}
        </div>
      {/if}
    </div>
  </div>
{:else}
  <slot />
{/if}