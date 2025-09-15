<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
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
  
  interface CartItem {
    product: Product;
    quantity: number;
  }
  
  let cartItems: CartItem[] = [];
  let loading = false;
  let processingCheckout = false;
  
  // Shipping details
  let shippingDetails = {
    name: '',
    address_line_1: '',
    address_line_2: '',
    city: '',
    state: '',
    postal_code: '',
    country: 'US',
    phone: ''
  };
  
  let showShipping = false;
  
  onMount(() => {
    loadCart();
  });
  
  async function loadCart() {
    const savedCart = localStorage.getItem('soulseer_cart');
    if (!savedCart) return;
    
    const cartMap = new Map<number, number>(JSON.parse(savedCart));
    const productIds = Array.from(cartMap.keys());
    
    if (productIds.length === 0) return;
    
    loading = true;
    
    try {
      const token = localStorage.getItem('auth_token');
      const res = await fetch(`${PUBLIC_BACKEND_URL}/api/marketplace/products`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (!res.ok) throw new Error('Failed to load products');
      
      const data = await res.json();
      const products = data.products as Product[];
      
      cartItems = productIds
        .map(id => {
          const product = products.find(p => p.id === id);
          const quantity = cartMap.get(id) || 0;
          return product ? { product, quantity } : null;
        })
        .filter(item => item !== null) as CartItem[];
      
      // Check if we need shipping
      showShipping = cartItems.some(item => item.product.kind === 'physical');
    } catch (err) {
      console.error('Failed to load cart:', err);
    } finally {
      loading = false;
    }
  }
  
  function updateQuantity(productId: number, newQuantity: number) {
    if (newQuantity <= 0) {
      removeFromCart(productId);
      return;
    }
    
    cartItems = cartItems.map(item => 
      item.product.id === productId 
        ? { ...item, quantity: newQuantity }
        : item
    );
    
    saveCart();
  }
  
  function removeFromCart(productId: number) {
    cartItems = cartItems.filter(item => item.product.id !== productId);
    saveCart();
  }
  
  function saveCart() {
    const cartMap = new Map<number, number>();
    cartItems.forEach(item => {
      cartMap.set(item.product.id, item.quantity);
    });
    localStorage.setItem('soulseer_cart', JSON.stringify(Array.from(cartMap)));
  }
  
  function formatPrice(cents: number): string {
    return `$${(cents / 100).toFixed(2)}`;
  }
  
  async function checkout() {
    if (showShipping && !validateShipping()) {
      alert('Please fill in all required shipping fields');
      return;
    }
    
    processingCheckout = true;
    
    try {
      const token = localStorage.getItem('auth_token');
      const items = cartItems.map(item => ({
        product_id: item.product.id,
        quantity: item.quantity
      }));
      
      const body: any = { items };
      
      if (showShipping) {
        body.shipping_address = shippingDetails;
      }
      
      const res = await fetch(`${PUBLIC_BACKEND_URL}/api/marketplace/checkout`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(body)
      });
      
      if (!res.ok) {
        const error = await res.json();
        throw new Error(error.detail || 'Checkout failed');
      }
      
      const data = await res.json();
      
      // Clear cart
      localStorage.removeItem('soulseer_cart');
      
      // Show success and redirect
      alert(`Order placed successfully! Order ID: ${data.order_id}`);
      goto('/dashboard/client');
      
    } catch (err: any) {
      alert(err.message || 'Checkout failed. Please try again.');
      console.error('Checkout error:', err);
    } finally {
      processingCheckout = false;
    }
  }
  
  function validateShipping(): boolean {
    return !!(
      shippingDetails.name &&
      shippingDetails.address_line_1 &&
      shippingDetails.city &&
      shippingDetails.state &&
      shippingDetails.postal_code &&
      shippingDetails.country
    );
  }
  
  $: subtotal = cartItems.reduce((sum, item) => sum + (item.product.price_cents * item.quantity), 0);
  $: tax = Math.round(subtotal * 0.08); // 8% tax
  $: total = subtotal + tax;
</script>

<svelte:head>
  <title>Shopping Cart - SoulSeer</title>
</svelte:head>

<div class="min-h-screen bg-mystic-dark text-white p-4">
  <div class="max-w-6xl mx-auto">
    <h1 class="text-4xl font-script text-mystic-pink mb-8">Shopping Cart</h1>
    
    {#if loading}
      <div class="flex justify-center items-center h-64">
        <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-mystic-pink"></div>
      </div>
    {:else if cartItems.length === 0}
      <div class="text-center py-16">
        <svg class="w-24 h-24 mx-auto mb-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
        </svg>
        <p class="text-gray-400 mb-4">Your cart is empty</p>
        <button
          on:click={() => goto('/shop')}
          class="bg-gradient-to-r from-mystic-pink to-mystic-purple px-6 py-2 rounded-lg hover:opacity-90 transition"
        >
          Continue Shopping
        </button>
      </div>
    {:else}
      <div class="grid lg:grid-cols-3 gap-8">
        <!-- Cart Items -->
        <div class="lg:col-span-2 space-y-4">
          {#each cartItems as item}
            <div class="bg-black/50 rounded-lg p-4 border border-mystic-purple">
              <div class="flex gap-4">
                <!-- Product Image -->
                <div class="w-24 h-24 bg-black/30 rounded-lg overflow-hidden flex-shrink-0">
                  {#if item.product.image_url}
                    <img
                      src={item.product.image_url}
                      alt={item.product.name}
                      class="w-full h-full object-cover"
                    />
                  {:else}
                    <div class="w-full h-full flex items-center justify-center text-gray-600">
                      <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                    </div>
                  {/if}
                </div>
                
                <!-- Product Details -->
                <div class="flex-1">
                  <h3 class="text-lg font-semibold mb-1">{item.product.name}</h3>
                  <p class="text-gray-400 text-sm mb-2">{item.product.description}</p>
                  <div class="flex items-center gap-4">
                    <!-- Quantity Controls -->
                    <div class="flex items-center gap-2">
                      <button
                        on:click={() => updateQuantity(item.product.id, item.quantity - 1)}
                        class="w-8 h-8 bg-white/10 hover:bg-white/20 rounded-lg flex items-center justify-center transition"
                      >
                        -
                      </button>
                      <span class="w-12 text-center">{item.quantity}</span>
                      <button
                        on:click={() => updateQuantity(item.product.id, item.quantity + 1)}
                        class="w-8 h-8 bg-white/10 hover:bg-white/20 rounded-lg flex items-center justify-center transition"
                      >
                        +
                      </button>
                    </div>
                    
                    <!-- Price -->
                    <div class="flex-1 text-right">
                      <span class="text-xl font-bold text-mystic-pink">
                        {formatPrice(item.product.price_cents * item.quantity)}
                      </span>
                    </div>
                    
                    <!-- Remove Button -->
                    <button
                      on:click={() => removeFromCart(item.product.id)}
                      class="text-red-400 hover:text-red-300 transition"
                    >
                      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          {/each}
          
          <!-- Shipping Form -->
          {#if showShipping}
            <div class="bg-black/50 rounded-lg p-6 border border-mystic-purple">
              <h2 class="text-xl font-semibold mb-4">Shipping Information</h2>
              <div class="grid md:grid-cols-2 gap-4">
                <div class="md:col-span-2">
                  <label class="block text-sm mb-1">Full Name *</label>
                  <input
                    type="text"
                    bind:value={shippingDetails.name}
                    class="w-full bg-black/50 border border-mystic-purple rounded-lg px-3 py-2 focus:outline-none focus:border-mystic-pink"
                  />
                </div>
                
                <div class="md:col-span-2">
                  <label class="block text-sm mb-1">Address Line 1 *</label>
                  <input
                    type="text"
                    bind:value={shippingDetails.address_line_1}
                    class="w-full bg-black/50 border border-mystic-purple rounded-lg px-3 py-2 focus:outline-none focus:border-mystic-pink"
                  />
                </div>
                
                <div class="md:col-span-2">
                  <label class="block text-sm mb-1">Address Line 2</label>
                  <input
                    type="text"
                    bind:value={shippingDetails.address_line_2}
                    class="w-full bg-black/50 border border-mystic-purple rounded-lg px-3 py-2 focus:outline-none focus:border-mystic-pink"
                  />
                </div>
                
                <div>
                  <label class="block text-sm mb-1">City *</label>
                  <input
                    type="text"
                    bind:value={shippingDetails.city}
                    class="w-full bg-black/50 border border-mystic-purple rounded-lg px-3 py-2 focus:outline-none focus:border-mystic-pink"
                  />
                </div>
                
                <div>
                  <label class="block text-sm mb-1">State *</label>
                  <input
                    type="text"
                    bind:value={shippingDetails.state}
                    class="w-full bg-black/50 border border-mystic-purple rounded-lg px-3 py-2 focus:outline-none focus:border-mystic-pink"
                  />
                </div>
                
                <div>
                  <label class="block text-sm mb-1">Postal Code *</label>
                  <input
                    type="text"
                    bind:value={shippingDetails.postal_code}
                    class="w-full bg-black/50 border border-mystic-purple rounded-lg px-3 py-2 focus:outline-none focus:border-mystic-pink"
                  />
                </div>
                
                <div>
                  <label class="block text-sm mb-1">Phone</label>
                  <input
                    type="tel"
                    bind:value={shippingDetails.phone}
                    class="w-full bg-black/50 border border-mystic-purple rounded-lg px-3 py-2 focus:outline-none focus:border-mystic-pink"
                  />
                </div>
              </div>
            </div>
          {/if}
        </div>
        
        <!-- Order Summary -->
        <div class="lg:col-span-1">
          <div class="bg-black/50 rounded-lg p-6 border border-mystic-purple sticky top-4">
            <h2 class="text-xl font-semibold mb-4">Order Summary</h2>
            
            <div class="space-y-2 mb-4">
              <div class="flex justify-between">
                <span>Subtotal</span>
                <span>{formatPrice(subtotal)}</span>
              </div>
              <div class="flex justify-between">
                <span>Tax</span>
                <span>{formatPrice(tax)}</span>
              </div>
              <div class="border-t border-mystic-purple pt-2 flex justify-between text-xl font-bold">
                <span>Total</span>
                <span class="text-mystic-pink">{formatPrice(total)}</span>
              </div>
            </div>
            
            <button
              on:click={checkout}
              disabled={processingCheckout}
              class="w-full bg-gradient-to-r from-mystic-pink to-mystic-purple py-3 rounded-lg hover:opacity-90 transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {processingCheckout ? 'Processing...' : 'Checkout with Wallet'}
            </button>
            
            <p class="text-xs text-gray-400 mt-4 text-center">
              Your order will be paid using your SoulSeer wallet balance
            </p>
          </div>
        </div>
      </div>
    {/if}
  </div>
</div>