<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
const route = useRoute()
const links = [
  { to: '/settings/failure-id',        label: 'Failure ID Configuration',       icon: 'failure-id' },
  { to: '/settings/telegram',          label: 'Telegram Integration Settings',  icon: 'telegram' },
  { to: '/settings/users-roles',       label: 'User and Role Management',       icon: 'users-roles' },
  { to: '/settings/circuits',          label: 'Circuit Management',             icon: 'circuits' },
  { to: '/settings/supervisors',       label: 'Supervisor Management',          icon: 'supervisors' },
  { to: '/settings/stations-sections', label: 'Station and Section Management', icon: 'stations-sections' },
  { to: '/settings/depots',            label: 'Depot Management',               icon: 'depot' },
]
const title = computed(() => route.meta?.title ?? 'Settings')
</script>

<template>
  <div class="grid grid-cols-1 lg:grid-cols-[260px_1fr] gap-4">
    <!-- In-page nav -->
    <aside class="rounded-2xl border-app bg-card text-app p-2 h-fit border">
      <nav class="flex flex-col gap-1">
        <RouterLink
          v-for="link in links" :key="link.to" :to="link.to"
          :class="[
            'flex items-center gap-3 rounded-lg px-3 py-2 transition',
            ($route.path === link.to)
              ? 'bg-[var(--button-primary)] text-[var(--seasalt)] hover:bg-[var(--button-primary)] hover:text-[var(--seasalt)]'
              : 'hover:bg-[var(--seasalt-lighter)] hover:shadow-popover'
          ]"
        >
          <span class="w-5 h-5 flex items-center justify-center" aria-hidden="true">
            <!-- Monochrome, inherits current color -->
            <svg v-if="link.icon==='failure-id'" viewBox="0 0 24 24" class="w-5 h-5"><path fill="currentColor" d="M10 2a2 2 0 0 0-2 2v2H6a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-2V4a2 2 0 0 0-2-2zm0 4V4h4v2zM8 12h8v2H8zm0 4h5v2H8z"/></svg>
            <svg v-else-if="link.icon==='telegram'" viewBox="0 0 24 24" class="w-5 h-5"><path fill="currentColor" d="M9.03 14.86 8.7 18.6a.75.75 0 0 0 1.18.68l2.11-1.52l3.94 2.88c.58.43 1.41.11 1.58-.6l3.2-13.22c.18-.75-.5-1.4-1.23-1.16L2.7 10.03c-.83.28-.8 1.46.04 1.7l5.1 1.44l9.24-6.2z"/></svg>
            <svg v-else-if="link.icon==='users-roles'" viewBox="0 0 24 24" class="w-5 h-5"><path fill="currentColor" d="M12 12a5 5 0 1 0-5-5a5 5 0 0 0 5 5m-7 8a7 7 0 0 1 14 0v1H5z"/></svg>
            <svg v-else-if="link.icon==='circuits'" viewBox="0 0 24 24" class="w-5 h-5"><path fill="currentColor" d="M7 3h2v4h6V3h2v4h2a2 2 0 0 1 2 2v3h-2V9H5v9h12v-2h2v2a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V9a2 2 0 0 1 2-2h2z"/></svg>
            <svg v-else-if="link.icon==='supervisors'" viewBox="0 0 24 24" class="w-5 h-5"><path fill="currentColor" d="M12 12a4 4 0 1 0-4-4a4 4 0 0 0 4 4m6 8v-1a5 5 0 0 0-5-5H7a5 5 0 0 0-5 5v1z"/></svg>
            <svg v-else-if="link.icon==='stations-sections'" viewBox="0 0 24 24" class="w-5 h-5"><path fill="currentColor" d="M12 2c3.87 0 7 3.13 7 7c0 5.25-7 13-7 13S5 14.25 5 9c0-3.87 3.13-7 7-7m0 9a2 2 0 1 0-2-2a2 2 0 0 0 2 2"/></svg>
            <svg v-else-if="link.icon==='depot'" viewBox="0 0 24 24" class="w-5 h-5"><path fill="currentColor" d="M3 10.5L12 6l9 4.5V20a1 1 0 0 1-1 1h-6v-6H10v6H4a1 1 0 0 1-1-1z"/></svg>
          </span>
          <span class="truncate">{{ link.label }}</span>
        </RouterLink>
      </nav>
    </aside>

    <!-- Content -->
    <section class="space-y-3">
      <header class="flex items-center justify-between">
        <h1 class="text-2xl font-bold">{{ title }}</h1>
      </header>
      <div class="card">
        <RouterView />
      </div>
    </section>
  </div>
  
</template>
