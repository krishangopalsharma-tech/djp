<script setup>
import { useUIStore } from '@/stores/ui'
import { useAuthStore } from '@/stores/auth'
const ui = useUIStore()
const auth = useAuthStore()

function doLogout() {
  auth.logout()
  ui.pushToast({ type: 'info', title: 'Signed out' })
}
</script>

<template>
  <header class="h-14 bg-white border-b flex items-center justify-between px-4">
    <div class="flex items-center gap-2">
      <button class="md:hidden inline-flex items-center justify-center w-9 h-9 rounded-lg border" @click="$emit('toggleSidebar')" aria-label="Open menu">☰</button>
      <div>
        <h1 class="text-base font-semibold">Railway Failure System</h1>
        <p class="text-xs text-gray-500">Frontend scaffold</p>
      </div>
    </div>

    <div class="text-sm">
      <template v-if="auth.user">
        <span class="mr-2 text-gray-600">Hi, <span class="font-medium">{{ auth.user.username }}</span></span>
        <button class="h-8 px-3 rounded-lg border bg-white" @click="doLogout">Logout</button>
      </template>
      <RouterLink v-else class="h-8 px-3 inline-flex items-center rounded-lg border bg-white" to="/login">Login</RouterLink>
    </div>
  </header>
</template>