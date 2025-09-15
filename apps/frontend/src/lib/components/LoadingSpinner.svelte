<script lang="ts">
  export let size: 'sm' | 'md' | 'lg' | 'xl' = 'md';
  export let color = 'mystic-pink';
  
  const sizeClasses = {
    sm: 'w-6 h-6',
    md: 'w-12 h-12',
    lg: 'w-16 h-16',
    xl: 'w-24 h-24'
  };
</script>

<div class="flex justify-center items-center">
  <div class="relative {sizeClasses[size]}">
    <div class="absolute inset-0 rounded-full border-4 border-{color}/20"></div>
    <div class="absolute inset-0 rounded-full border-4 border-transparent border-t-{color} animate-spin"></div>
  </div>
</div>

<style>
  @keyframes spin {
    to { transform: rotate(360deg); }
  }
  
  .animate-spin {
    animation: spin 1s linear infinite;
  }
</style>