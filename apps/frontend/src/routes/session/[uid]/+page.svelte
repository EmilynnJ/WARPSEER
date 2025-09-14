<script lang="ts">
  import { onMount } from 'svelte';
  import { env } from '$lib/env';
  import { api } from '$lib/api';
  import { page } from '$app/stores';
  let me: any = null;
  let ws: WebSocket | null = null;
  let pc: RTCPeerConnection;
  let localStream: MediaStream | null = null;
  let remoteStream: MediaStream | null = null;
  let micOn = true, camOn = true;

  async function getMe() {
    const { data } = await api.get('/users/me');
    me = data;
  }

  async function init() {
    await getMe();
    const uid = $page.params.uid;
    pc = new RTCPeerConnection({ iceServers: JSON.parse(env.iceServersJson) });
    remoteStream = new MediaStream();

    pc.ontrack = (e) => {
      const [track] = e.streams;
      // @ts-ignore
      document.getElementById('remote').srcObject = track;
    };

    localStream = await navigator.mediaDevices.getUserMedia({ audio: true, video: true });
    // @ts-ignore
    document.getElementById('local').srcObject = localStream;
    localStream.getTracks().forEach((t) => pc.addTrack(t, localStream!));

    ws = new WebSocket(env.backendBase.replace('http', 'ws') + `/signaling/ws/${uid}`);
    ws.onmessage = async (ev) => {
      const msg = JSON.parse(ev.data);
      if (msg.type === 'offer') {
        await pc.setRemoteDescription(new RTCSessionDescription(msg.sdp));
        const answer = await pc.createAnswer();
        await pc.setLocalDescription(answer);
        ws?.send(JSON.stringify({ type: 'answer', sdp: answer }));
      } else if (msg.type === 'answer') {
        await pc.setRemoteDescription(new RTCSessionDescription(msg.sdp));
      } else if (msg.type === 'ice') {
        try { await pc.addIceCandidate(msg.candidate); } catch {}
      }
    };

    pc.onicecandidate = (ev) => {
      if (ev.candidate) ws?.send(JSON.stringify({ type: 'ice', candidate: ev.candidate }));
    };

    // Initiator creates offer
    const offer = await pc.createOffer();
    await pc.setLocalDescription(offer);
    ws?.send(JSON.stringify({ type: 'offer', sdp: offer }));
  }

  function toggleMic() {
    micOn = !micOn;
    localStream?.getAudioTracks().forEach((t) => (t.enabled = micOn));
  }
  function toggleCam() {
    camOn = !camOn;
    localStream?.getVideoTracks().forEach((t) => (t.enabled = camOn));
  }

  onMount(init);
</script>

<section class="mx-auto max-w-6xl px-4 py-6">
  <div class="grid md:grid-cols-2 gap-4">
    <video id="local" class="w-full rounded-lg bg-black" autoplay playsinline muted></video>
    <video id="remote" class="w-full rounded-lg bg-black" autoplay playsinline></video>
  </div>
  <div class="mt-4 flex gap-3">
    <button class="px-4 py-2 rounded bg-mystic-pink text-black" on:click={toggleMic}>{micOn ? 'Mute' : 'Unmute'}</button>
    <button class="px-4 py-2 rounded bg-mystic-gold text-black" on:click={toggleCam}>{camOn ? 'Camera Off' : 'Camera On'}</button>
  </div>
</section>