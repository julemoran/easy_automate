<template>
  <div>
    <h1>WebSocket Event Viewer</h1>
    <div id="events" v-html="eventsHtml"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';

const eventsHtml = ref('');

onMounted(() => {
  // Replace with your actual WebSocket server URL if needed
  const wsUrl = (location.protocol === 'https:' ? 'wss://' : 'ws://') + location.host + '/ws';
  const socket = new WebSocket(wsUrl);

  socket.addEventListener('open', () => {
    eventsHtml.value += '<p>Connected to server</p>';
  });

  socket.addEventListener('close', () => {
    eventsHtml.value += '<p>Disconnected from server</p>';
  });

  socket.addEventListener('message', (event) => {
    let data;
    try {
      data = JSON.parse(event.data);
    } catch {
      data = event.data;
    }
    // If the event is a ping, show it specially
    if (typeof data === 'object' && data && data.type === 'ping') {
      eventsHtml.value += `<p>Ping event: ${JSON.stringify(data)}</p>`;
    } else {
      eventsHtml.value += `<p>Message: ${JSON.stringify(data)}</p>`;
    }
  });
});
</script>

<!-- Add Socket.IO client script globally in index.html or via CDN if needed -->
