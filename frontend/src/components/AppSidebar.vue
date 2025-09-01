<script setup>
import { useRoute, RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
const auth = useAuthStore()
const route = useRoute()
const links = [
  { to: '/dashboard', label: 'Dashboard', icon: 'pi pi-home' },
  { to: '/logbook', label: 'Logbook', icon: 'pi pi-book' },
  { to: '/failures/new', label: 'New Failure', icon: 'pi pi-plus-circle' },
  { to: '/analytics', label: 'Analytics', icon: 'pi pi-chart-line' },
]

const isActive = (to) => route.path.startsWith(to)
</script>

<template>
  <aside class="h-full flex flex-col overflow-hidden" :data-collapsed="$pinia.state.value.ui?.sidebarCollapsed">
    <div class="px-4 py-3 text-lg font-semibold text-app transition-opacity duration-150" :class="$pinia.state.value.ui?.sidebarCollapsed ? 'opacity-0 pointer-events-none select-none' : 'opacity-100'">Menu</div>

    <template v-if="auth.user">
      <nav class="px-2 space-y-1">
        <RouterLink
          v-for="l in links"
          :key="l.to"
          :to="l.to"
          class="group block rounded-lg px-3 py-2 text-base text-app hover-primary"
          :class="isActive(l.to) ? 'selected-primary' : ''"
          :aria-label="l.label"
          :title="l.label"
          @click="$emit('navigate')"
        >
          <span class="inline-flex items-center" :class="$pinia.state.value.ui?.sidebarCollapsed ? 'justify-center w-10 h-10 gap-0' : 'gap-2'">
            <i :class="l.icon" class="text-[1.1rem] leading-none"></i>
            <span class="leading-none transition-all duration-150"
                  :class="$pinia.state.value.ui?.sidebarCollapsed ? 'w-0 opacity-0 overflow-hidden ml-0' : 'w-auto opacity-100 ml-2'">
              {{ l.label }}
            </span>
          </span>
          
        </RouterLink>
      </nav>
      <div class="mt-auto p-3 text-xs text-muted">v0.1 • Vue + Tailwind</div>
    </template>

    <template v-else>
      <div class="px-4 text-sm text-muted">
        Please <RouterLink class="underline" to="/login">log in</RouterLink>.
      </div>
      <div class="mt-auto p-3 text-xs text-muted">v0.1 • Vue + Tailwind</div>
    </template>
  </aside>
</template>
