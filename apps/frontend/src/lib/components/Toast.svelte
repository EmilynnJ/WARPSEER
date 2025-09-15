<script lang="ts">
  import { onMount } from 'svelte';
  import { fade, fly } from 'svelte/transition';
  
  export let type: 'success' | 'error' | 'warning' | 'info' = 'info';
  export let message = '';
  export let duration = 5000;
  export let dismissible = true;
  export let onDismiss = () => {};
  
  let visible = true;
  
  const icons = {
    success: `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />`,
    error: `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />`,
    warning: `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />`,
    info: `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />`
  };
  
  const colors = {
    success: 'bg-green-500/20 border-green-500 text-green-400',
    error: 'bg-red-500/20 border-red-500 text-red-400',
    warning: 'bg-yellow-500/20 border-yellow-500 text-yellow-400',
    info: 'bg-mystic-purple/20 border-mystic-purple text-mystic-pink'
  };
  
  onMount(() => {
    if (duration > 0) {
      const timer = setTimeout(() => {
        dismiss();
      }, duration);
      
      return () => clearTimeout(timer);
    }
  });
  
  function dismiss() {
    visible = false;
    setTimeout(onDismiss, 300);
  }
</script>

{#if visible}
  <div
    class="fixed top-4 right-4 max-w-sm z-50"
    in:fly={{ x: 100, duration: 300 }}
    out:fade={{ duration: 300 }}
  >
    <div class="rounded-lg border p-4 shadow-lg bg-black/90 {colors[type]}">
      <div class="flex items-start gap-3">
        <svg class="w-6 h-6 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          {@html icons[type]}
        </svg>
        
        <div class="flex-1">
          <p class="text-white">{message}</p>
        </div>
        
        {#if dismissible}
          <button
            on:click={dismiss}
            class="text-gray-400 hover:text-white transition"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        {/if}
      </div>
    </div>
  </div>
{/if}