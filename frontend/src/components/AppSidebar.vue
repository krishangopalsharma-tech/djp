<script setup>
import { useRoute, RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
const auth = useAuthStore()
const route = useRoute()
const links = [
  { to: '/dashboard', label: 'Dashboard' },
  { to: '/logbook', label: 'Logbook' },
  { to: '/failures/new', label: 'New Failure' },
  { to: '/settings', label: 'Settings' },
  { to: '/analytics',    label: 'Analytics' },
]

const isActive = (to) => route.path.startsWith(to)
</script>

<template>
  <aside class="h-full flex flex-col">
    <div class="px-4 py-3 text-lg font-semibold">Menu</div>

    <template v-if="auth.user">
      <nav class="px-2 space-y-1">
        <RouterLink
          v-for="l in links"
          :key="l.to"
          :to="l.to"
          class="block rounded-lg px-3 py-2 text-sm"
          :class="isActive(l.to) ? 'bg-gray-900 text-white' : 'text-gray-700 hover:bg-gray-100'"
          @click="$emit('navigate')"
        >
          {{ l.label }}
          
        </RouterLink>
      </nav>
      <div class="mt-auto p-3 text-xs text-gray-500">v0.1 • Vue + Tailwind</div>
    </template>

    <template v-else>
      <div class="px-4 text-sm text-gray-600">
        Please <RouterLink class="underline" to="/login">log in</RouterLink>.
      </div>
      <div class="mt-auto p-3 text-xs text-gray-500">v0.1 • Vue + Tailwind</div>
    </template>
  </aside>
</template>