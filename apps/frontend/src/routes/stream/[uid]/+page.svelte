<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { page } from '$app/stores';
  import { api } from '$lib/api';
  import { env } from '$lib/env';
  let isStreamer = false;
  let viewerCount = 0;
  let chatMessages: any[] = [];
  let chatInput = '';
  let ws: WebSocket | null = null;
  let gifts: any[] = [];
  let selectedGift: any = null;
  let displayedGifts: any[] = [];
  let error: string | null = null;
  let localStream: MediaStream | null = null;
  let pc: RTCPeerConnection | null = null;

  async function loadGifts() {
    const { data } = await api.get('/streams/gifts');
    gifts = data.items;
  }

  async function checkIfStreamer() {
    const { data } = await api.get('/users/me');
    const streamData = await api.get(`/sessions/${$page.params.uid}`);
    isStreamer = data.id === streamData.data.reader_id;
  }

  async function sendGift() {
    if (!selectedGift) return;
    try {
      await api.post(`/streams/${$page.params.uid}/gift`, { gift_id: selectedGift.id });
      selectedGift = null;
    } catch (e: any) {
      error = e?.response?.data?.detail || e.message;
    }
  }

  function sendChat() {
    if (!chatInput.trim() || !ws) return;
    ws.send(JSON.stringify({ type: 'chat', message: chatInput, sender: 'You' }));
    chatMessages = [...chatMessages, { sender: 'You', message: chatInput }];
    chatInput = '';
  }

  function showGiftAnimation(gift: any) {
    displayedGifts = [...displayedGifts, { ...gift, id: Date.now() }];
    setTimeout(() => {
      displayedGifts = displayedGifts.filter(g => g.id !== gift.id);
    }, 3000);
  }

  async function initStream() {
    await checkIfStreamer();
    await loadGifts();

    // WebSocket for chat and events
    ws = new WebSocket(env.backendBase.replace('http', 'ws') + `/streams/ws/${$page.params.uid}`);
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'viewers') {
        viewerCount = data.count;
      } else if (data.type === 'chat') {
        chatMessages = [...chatMessages, { sender: data.sender, message: data.message }];
      } else if (data.type === 'gift') {
        showGiftAnimation(data);
        chatMessages = [...chatMessages, { 
          sender: 'System', 
          message: `${data.sender} sent a ${data.gift_name}!` 
        }];
      }
    };

    // Setup video stream if streamer
    if (isStreamer) {
      try {
        localStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
        const video = document.getElementById('stream-video') as HTMLVideoElement;
        if (video) video.srcObject = localStream;
      } catch (e) {
        error = 'Could not access camera/microphone';
      }
    }
  }

  onMount(initStream);
  
  onDestroy(() => {
    ws?.close();
    localStream?.getTracks().forEach(t => t.stop());
  });
</script>

<section class="mx-auto max-w-7xl px-4 py-6">
  <div class="grid lg:grid-cols-3 gap-6">
    <!-- Video -->
    <div class="lg:col-span-2">
      <div class="relative rounded-xl overflow-hidden bg-black aspect-video">
        {#if isStreamer}
          <video id="stream-video" class="w-full h-full" autoplay muted playsinline></video>
        {:else}
          <div class="flex items-center justify-center h-full">
            <p class="text-white/60">Stream video would appear here</p>
          </div>
        {/if}
        <div class="absolute top-4 left-4 px-3 py-1 bg-red-600 text-white rounded-full text-sm font-bold">
          LIVE • {viewerCount} viewers
        </div>
        <!-- Gift animations -->
        {#each displayedGifts as gift (gift.id)}
          <div class="absolute inset-0 flex items-center justify-center pointer-events-none animate-bounce">
            <div class="text-6xl">{gift.gift_image}</div>
          </div>
        {/each}
      </div>
      
      <!-- Gifts selector -->
      {#if !isStreamer}
        <div class="mt-4 p-4 rounded-xl bg-white/5 ring-1 ring-white/10">
          <div class="flex gap-3 items-center">
            {#each gifts as gift}
              <button 
                class="p-3 rounded-lg transition {selectedGift?.id === gift.id ? 'bg-mystic-pink text-black' : 'bg-white/10 hover:bg-white/20'}"
                on:click={() => selectedGift = gift}
              >
                <div class="text-2xl">{gift.image_url}</div>
                <div class="text-xs">${(gift.price_cents/100).toFixed(2)}</div>
              </button>
            {/each}
            {#if selectedGift}
              <button 
                class="ml-auto px-4 py-2 bg-mystic-gold text-black rounded"
                on:click={sendGift}
              >
                Send {selectedGift.name}
              </button>
            {/if}
          </div>
        </div>
      {/if}
    </div>

    <!-- Chat -->
    <div class="flex flex-col h-[600px] rounded-xl bg-white/5 ring-1 ring-white/10">
      <div class="p-4 border-b border-white/10">
        <h3 class="font-display text-xl">Live Chat</h3>
      </div>
      <div class="flex-1 overflow-y-auto p-4 space-y-2">
        {#each chatMessages as msg}
          <div class="text-sm">
            <span class="font-bold text-mystic-pink">{msg.sender}:</span>
            <span class="text-white/90">{msg.message}</span>
          </div>
        {/each}
      </div>
      <div class="p-4 border-t border-white/10">
        <div class="flex gap-2">
          <input 
            type="text" 
            bind:value={chatInput}
            on:keydown={(e) => e.key === 'Enter' && sendChat()}
            class="flex-1 bg-black/40 rounded px-3 py-2"
            placeholder="Type a message..."
          />
          <button 
            class="px-4 py-2 bg-mystic-pink text-black rounded"
            on:click={sendChat}
          >
            Send
          </button>
        </div>
      </div>
    </div>
  </div>
  {#if error}<p class="text-red-400 mt-4">{error}</p>{/if}
</section>