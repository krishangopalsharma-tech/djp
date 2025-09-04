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
  '/failures/new': 'New Failure',
  '/analytics': 'Analytics Board',
}
const pageTitle = computed(() => route.meta?.title || titleMap[route.path] || titleMap['/' + (route.path.split('/')[1] || '')] || 'RFMS')

function doLogout() {
  auth.logout()
  ui.pushToast({ type: 'info', title: 'Signed out' })
}
</script>

<template>
  <header class="h-14 navbar border-b border-app flex items-center justify-between px-4">
    <div class="flex items-center gap-2">
      <button
        class="md:hidden inline-flex items-center justify-center w-9 h-9 rounded-lg border border-app bg-card text-app hover-primary"
        @click="emit('toggleSidebar')"
        aria-label="Open menu"
        title="Open menu"
      >
        ☰
      </button>
      <h1 class="text-base font-semibold">{{ pageTitle }}</h1>
    </div>

    <div class="text-sm flex items-center gap-2">
      <RouterLink
        to="/settings"
        class="inline-flex items-center justify-center w-9 h-9 rounded-lg border border-app bg-card text-app hover-primary"
        aria-label="Settings"
        title="Settings"
      >
        <i class="pi pi-cog"></i>
      </RouterLink>
      <template v-if="auth.user">
        <span class="mr-2 text-muted">Hi, <span class="font-medium text-app">{{ auth.user.username }}</span></span>
        <button class="btn btn-ghost h-9" @click="doLogout">Logout</button>
      </template>
      <RouterLink v-else class="btn btn-outline h-9" to="/login">Login</RouterLink>
    </div>
  </header>
</template>
