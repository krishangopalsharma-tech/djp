<script setup>
import { useUIStore } from '@/stores/ui'
import { useAuthStore } from '@/stores/auth'
import { useRoute } from 'vue-router'
import { computed } from 'vue'
const emit = defineEmits(['toggleSidebar'])

const ui = useUIStore()
const auth = useAuthStore()
const route = useRoute()

const titleMap = {
  '/dashboard': 'Dashboard',
  '/logbook': 'Logbook',
  '/failures/new': 'Logbook Entry',
  '/analytics': 'Analytics Board',
}
const pageTitle = computed(() => {
  if (route.path.startsWith('/settings')) return 'Settings'
  return route.meta?.title
      || titleMap[route.path]
      || titleMap['/' + (route.path.split('/')[1] || '')]
      || 'RFMS'
})

const displayName = computed(() => auth.user?.name || auth.user?.username || '')

function doLogout() {
  auth.logout()
  ui.pushToast({ type: 'info', title: 'Signed out' })
}
</script>

<template>
  <header
    class="h-14 flex items-center justify-between px-4
           bg-[var(--sidebar-bg)] text-[var(--sidebar-fg)]
           rounded-none border-0 shadow-none relative z-10"
  >
    <div class="flex items-center gap-2">
      <!-- Toggle sidebar moved/kept on the LEFT, visible at all sizes -->
      <button
        class="inline-flex items-center justify-center w-9 h-9 rounded-lg
               text-[var(--sidebar-fg)]
               hover:bg-[color-mix(in_oklab,var(--sidebar-fg)/_12%,_transparent)]
               focus-visible:outline-none focus-visible:ring-2
               focus-visible:ring-[var(--sidebar-fg)]/40"
        @click="emit('toggleSidebar')"
        aria-label="Toggle sidebar"
        title="Toggle sidebar"
      >
        <svg viewBox="0 0 24 24" class="w-5 h-5"><path fill="currentColor" d="M3 6h18v2H3zm0 5h18v2H3zm0 5h18v2H3z"/></svg>
      </button>
      <h1 class="text-base font-semibold">{{ pageTitle }}</h1>
    </div>

    <!-- Right side: show current user name -->
    <div class="flex items-center gap-2">
      <span v-if="displayName" class="text-sm opacity-90 truncate max-w-[200px]">{{ displayName }}</span>
    </div>
  </header>
</template>
