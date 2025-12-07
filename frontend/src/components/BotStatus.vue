<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { http } from '@/lib/http'

const status = ref('unknown') // 'running', 'stopped', 'unknown'
const lastHeartbeat = ref(null)
let pollInterval = null

async function checkStatus() {
  try {
    const { data } = await http.get('/telegram-settings/')
    const settings = Array.isArray(data) ? data[0] : (data.results ? data.results[0] : data)
    
    if (settings && settings.bot_last_heartbeat) {
      const heartbeat = new Date(settings.bot_last_heartbeat)
      const now = new Date()
      const diffSeconds = (now - heartbeat) / 1000
      
      // If heartbeat is within last 60 seconds, consider it running
      if (diffSeconds < 65) {
        status.value = 'running'
      } else {
        status.value = 'stopped'
      }
      lastHeartbeat.value = heartbeat
    } else {
      status.value = 'stopped'
    }
  } catch (e) {
    status.value = 'unknown'
    console.error('Bot status check failed', e)
  }
}

onMounted(() => {
  checkStatus()
  pollInterval = setInterval(checkStatus, 30000) // Poll every 30s
})

onUnmounted(() => {
  if (pollInterval) clearInterval(pollInterval)
})
</script>

<template>
  <div 
    class="flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium border"
    :class="{
      'bg-green-50 text-green-700 border-green-200': status === 'running',
      'bg-red-50 text-red-700 border-red-200': status === 'stopped',
      'bg-gray-50 text-gray-700 border-gray-200': status === 'unknown'
    }"
    :title="status === 'running' ? 'Bot Service is Running' : 'Bot Service is Stopped'"
  >
    <span class="relative flex h-2 w-2">
      <span v-if="status === 'running'" class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
      <span class="relative inline-flex rounded-full h-2 w-2" 
        :class="{
          'bg-green-500': status === 'running',
          'bg-red-500': status === 'stopped',
          'bg-gray-400': status === 'unknown'
        }">
      </span>
    </span>
    <span class="hidden sm:inline">Bot: {{ status === 'running' ? 'Online' : 'Offline' }}</span>
  </div>
</template>
