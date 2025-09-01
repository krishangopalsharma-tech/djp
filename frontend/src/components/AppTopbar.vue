<script setup>
import { useUIStore } from '@/stores/ui'
import { useAuthStore } from '@/stores/auth'
import ThemeSwitcherInline from '@/components/ThemeSwitcherInline.vue'
const emit = defineEmits(['toggleSidebar'])

const ui = useUIStore()
const auth = useAuthStore()

function doLogout() {
  auth.logout()
  ui.pushToast({ type: 'info', title: 'Signed out' })
}
</script>

<template>
  <header class="h-14 bg-card border-b border-app text-app flex items-center justify-between px-4">
    <div class="flex items-center gap-2">
      <ThemeSwitcherInline />
      <button
        class="md:hidden inline-flex items-center justify-center w-9 h-9 rounded-lg border border-app bg-card text-app hover-primary"
        @click="emit('toggleSidebar')"
        aria-label="Open menu"
        title="Open menu"
      >
        ☰
      </button>
      <div>
        <h1 class="text-base font-semibold">Railway Failure System</h1>
        <p class="text-xs text-muted">Frontend scaffold</p>
      </div>
    </div>

    <div class="text-sm flex items-center gap-2">
      <!-- Settings icon-only button -->
      <button
        class="inline-flex items-center justify-center w-9 h-9 rounded-lg border border-app bg-card text-app hover-primary"
        :aria-pressed="String(ui.sidebarCollapsed)"
        title="Toggle sidebar"
        @click="ui.toggleSidebarCollapsed()"
      >
        <svg viewBox="0 0 24 24" class="w-4 h-4"><path fill="currentColor" d="M3 4h18v2H3zm3 4h12v2H6zm-3 4h18v2H3zm3 4h12v2H6z"/></svg>
      </button>
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
