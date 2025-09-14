<script lang="ts">
  import { api } from '$lib/api';
  import { getStripe } from '$lib/stripe';
  import { onMount } from 'svelte';
  let amount = 2000; // cents
  let clientSecret: string | null = null;
  let message: string | null = null;
  let error: string | null = null;
  let elements: any;
  let stripe: any;

  async function createIntent() {
    try {
      const { data } = await api.post('/payments/topup/intents', { amount_cents: amount });
      clientSecret = data.client_secret;
      stripe = await getStripe();
      elements = stripe.elements({ clientSecret });
      const paymentElement = elements.create('payment');
      paymentElement.mount('#payment-element');
    } catch (e: any) {
      error = e?.response?.data?.detail || e.message || 'Failed to create payment';
    }
  }

  async function confirmPayment() {
    if (!stripe || !elements) return;
    const { error: stripeError } = await stripe.confirmPayment({
      elements,
      confirmParams: {
        return_url: window.location.origin + '/wallet?status=success'
      }
    });
    if (stripeError) {
      error = stripeError.message;
    } else {
      message = 'Payment processing. You will be redirected if 3DS is required.';
    }
  }

  onMount(() => {
    const url = new URL(window.location.href);
    if (url.searchParams.get('status') === 'success') {
      message = 'Payment successful. Your wallet will update shortly.';
    }
  });
</script>

<section class="mx-auto max-w-2xl px-4 py-10">
  <h2 class="font-script text-4xl text-mystic-pink mb-4">Add Funds</h2>
  <div class="rounded-xl bg-white/5 ring-1 ring-white/10 p-6 space-y-4">
    <label class="block">Amount (USD cents)
      <input class="mt-2 w-full bg-black/40 rounded px-3 py-2" type="number" bind:value={amount} min="100" step="50" />
    </label>
    <button on:click={createIntent} class="px-4 py-2 bg-mystic-pink text-black rounded">Create Payment</button>
    {#if clientSecret}
      <div id="payment-element" class="mt-4"></div>
      <button on:click={confirmPayment} class="mt-4 px-4 py-2 bg-mystic-gold text-black rounded">Pay</button>
    {/if}
    {#if message}<p class="text-green-400">{message}</p>{/if}
    {#if error}<p class="text-red-400">{error}</p>{/if}
  </div>
</section>