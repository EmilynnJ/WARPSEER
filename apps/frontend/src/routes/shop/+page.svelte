<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { page } from '$app/stores';
  import { PUBLIC_BACKEND_URL } from '$env/static/public';
  
  interface Product {
    id: number;
    stripe_product_id: string;
    name: string;
    description: string;
    price_cents: number;
    image_url: string;
    kind: 'digital' | 'physical' | 'service';
    stock_quantity: number;
    reader_id?: number;
    active: boolean;
  }
  
  let products: Product[] = [];
  let loading = true;
  let error = '';
  let selectedCategory: string = 'all';
  let searchQuery = '';
  let cart: Map<number, number> = new Map();
  
  // Load cart from localStorage
  onMount(() => {
    const savedCart = localStorage.getItem('soulseer_cart');
    if (savedCart) {
      cart = new Map(JSON.parse(savedCart));
    }
    loadProducts();
  });
  
  async function loadProducts() {
    try {
      loading = true;
      const token = localStorage.getItem('auth_token');
      const res = await fetch(`${PUBLIC_BACKEND_URL}/api/marketplace/products`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (!res.ok) throw new Error('Failed to load products');
      
      const data = await res.json();
      products = data.products;
    } catch (err) {
      error = 'Failed to load products';
      console.error(err);
    } finally {
      loading = false;
    }
  }
  
  function addToCart(product: Product) {
    const current = cart.get(product.id) || 0;
    cart.set(product.id, current + 1);
    cart = cart; // Trigger reactivity
    saveCart();
    
    // Show toast notification
    showToast(`${product.name} added to cart`);
  }
  
  function saveCart() {
    localStorage.setItem('soulseer_cart', JSON.stringify(Array.from(cart)));
  }
  
  function showToast(message: string) {
    const toast = document.createElement('div');
    toast.className = 'fixed bottom-4 right-4 bg-mystic-pink text-white px-6 py-3 rounded-lg shadow-lg z-50 animate-fade-in';
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
      toast.remove();
    }, 3000);
  }
  
  function formatPrice(cents: number): string {
    return `$${(cents / 100).toFixed(2)}`;
  }
  
  $: filteredProducts = products.filter(product => {
    const matchesCategory = selectedCategory === 'all' || product.kind === selectedCategory;
    const matchesSearch = product.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         product.description.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCategory && matchesSearch && product.active;
  });
  
  $: cartItemCount = Array.from(cart.values()).reduce((sum, qty) => sum + qty, 0);
</script>

<svelte:head>
  <title>Shop - SoulSeer</title>
</svelte:head>

<div class="min-h-screen bg-mystic-dark text-white p-4">
  <div class="max-w-7xl mx-auto">
    <!-- Header -->
    <div class="flex justify-between items-center mb-8">
      <h1 class="text-4xl font-script text-mystic-pink">Mystical Marketplace</h1>
      
      <!-- Cart Button -->
      <button
        on:click={() => goto('/shop/cart')}
        class="relative bg-gradient-to-r from-mystic-pink to-mystic-purple px-6 py-2 rounded-full hover:opacity-90 transition"
      >
        <span class="flex items-center gap-2">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
          </svg>
          View Cart
          {#if cartItemCount > 0}
            <span class="absolute -top-2 -right-2 bg-mystic-gold text-black text-xs rounded-full w-6 h-6 flex items-center justify-center">
              {cartItemCount}
            </span>
          {/if}
        </span>
      </button>
    </div>
    
    <!-- Filters -->
    <div class="mb-8 flex flex-wrap gap-4">
      <!-- Search -->
      <div class="flex-1 min-w-[300px]">
        <input
          type="text"
          bind:value={searchQuery}
          placeholder="Search products..."
          class="w-full bg-black/50 border border-mystic-purple rounded-lg px-4 py-2 focus:outline-none focus:border-mystic-pink"
        />
      </div>
      
      <!-- Category Filter -->
      <div class="flex gap-2">
        <button
          on:click={() => selectedCategory = 'all'}
          class="px-4 py-2 rounded-lg transition {selectedCategory === 'all' ? 'bg-mystic-pink' : 'bg-white/10 hover:bg-white/20'}"
        >
          All
        </button>
        <button
          on:click={() => selectedCategory = 'digital'}
          class="px-4 py-2 rounded-lg transition {selectedCategory === 'digital' ? 'bg-mystic-pink' : 'bg-white/10 hover:bg-white/20'}"
        >
          Digital
        </button>
        <button
          on:click={() => selectedCategory = 'physical'}
          class="px-4 py-2 rounded-lg transition {selectedCategory === 'physical' ? 'bg-mystic-pink' : 'bg-white/10 hover:bg-white/20'}"
        >
          Physical
        </button>
        <button
          on:click={() => selectedCategory = 'service'}
          class="px-4 py-2 rounded-lg transition {selectedCategory === 'service' ? 'bg-mystic-pink' : 'bg-white/10 hover:bg-white/20'}"
        >
          Services
        </button>
      </div>
    </div>
    
    <!-- Products Grid -->
    {#if loading}
      <div class="flex justify-center items-center h-64">
        <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-mystic-pink"></div>
      </div>
    {:else if error}
      <div class="text-center text-red-400 py-8">{error}</div>
    {:else if filteredProducts.length === 0}
      <div class="text-center text-gray-400 py-8">No products found</div>
    {:else}
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {#each filteredProducts as product}
          <div class="bg-black/50 rounded-lg overflow-hidden border border-mystic-purple hover:border-mystic-pink transition group">
            <!-- Product Image -->
            <div class="aspect-square bg-black/30 relative overflow-hidden">
              {#if product.image_url}
                <img
                  src={product.image_url}
                  alt={product.name}
                  class="w-full h-full object-cover group-hover:scale-110 transition duration-300"
                />
              {:else}
                <div class="w-full h-full flex items-center justify-center text-gray-600">
                  <svg class="w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                </div>
              {/if}
              
              <!-- Product Type Badge -->
              <span class="absolute top-2 right-2 bg-black/70 text-xs px-2 py-1 rounded capitalize">
                {product.kind}
              </span>
              
              <!-- Stock Badge -->
              {#if product.kind === 'physical' && product.stock_quantity > 0 && product.stock_quantity < 10}
                <span class="absolute top-2 left-2 bg-red-500 text-xs px-2 py-1 rounded">
                  Only {product.stock_quantity} left!
                </span>
              {/if}
            </div>
            
            <!-- Product Info -->
            <div class="p-4">
              <h3 class="text-lg font-semibold mb-2">{product.name}</h3>
              <p class="text-gray-400 text-sm mb-3 line-clamp-2">{product.description}</p>
              
              <div class="flex justify-between items-center">
                <span class="text-2xl font-bold text-mystic-pink">
                  {formatPrice(product.price_cents)}
                </span>
                
                {#if product.kind === 'physical' && product.stock_quantity === 0}
                  <button disabled class="bg-gray-700 text-gray-500 px-4 py-2 rounded-lg cursor-not-allowed">
                    Out of Stock
                  </button>
                {:else}
                  <button
                    on:click={() => addToCart(product)}
                    class="bg-gradient-to-r from-mystic-pink to-mystic-purple px-4 py-2 rounded-lg hover:opacity-90 transition"
                  >
                    Add to Cart
                  </button>
                {/if}
              </div>
            </div>
          </div>
        {/each}
      </div>
    {/if}
  </div>
</div>

<style>
  .line-clamp-2 {
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
  
  @keyframes fade-in {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
  }
  
  .animate-fade-in {
    animation: fade-in 0.3s ease-out;
  }
</style>
