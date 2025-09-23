<script setup>
import { useUIStore } from '@/stores/ui'
const ui = useUIStore()

const typeStyles = (t) => ({
  info:    'bg-blue-600',
  success: 'bg-green-600',
  error:   'bg-red-600',
  warn:    'bg-amber-600',
}[t] || 'bg-gray-700')
</script>

<template>
  <div class="fixed inset-0 pointer-events-none z-[100]">
    <div class="absolute right-4 top-4 flex flex-col gap-2">
      <div v-for="t in ui.toasts" :key="t.id"
           class="pointer-events-auto w-80 rounded-xl shadow-lg text-white overflow-hidden"
           :class="typeStyles(t.type)">
        <div class="px-3 py-2 flex items-start justify-between gap-2">
          <div>
            <div class="text-sm font-semibold" v-if="t.title">{{ t.title }}</div>
            <div class="text-sm opacity-90" v-if="t.message">{{ t.message }}</div>
          </div>
          <button class="text-white/90 hover:text-white text-sm" @click="ui.removeToast(t.id)">✕</button>
        </div>
      </div>
    </div>
  </div>
</template>
