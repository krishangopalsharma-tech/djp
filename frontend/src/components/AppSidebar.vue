<script setup>
import { useRoute, RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useUIStore } from '@/stores/ui'
// RFMS icon is inlined as SVG for reliable theming
const auth = useAuthStore()
const ui = useUIStore()
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
  <aside class="h-full flex flex-col overflow-hidden sidebar" :data-collapsed="$pinia.state.value.ui?.sidebarCollapsed">
    <!-- Branding + collapse control -->
    <div class="px-3 py-2 flex items-center justify-between">
      <div
        class="flex items-center gap-2"
        :class="$pinia.state.value.ui?.sidebarCollapsed ? 'w-full justify-center' : ''"
      >
        <!-- Inline SVG for maximum reliability and theming via currentColor -->
        <svg
          class="inline-block h-8 w-8"
          :style="{ color: 'var(--sidebar-fg)' }"
          viewBox="0 0 21.24 25.23"
          role="img"
          aria-label="RFMS icon"
          fill="currentColor"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path d="M14.39,17.38l-1.39-.03c.24.43.48.87.72,1.3H4.7c.24-.43.48-.87.72-1.3l-1.39.03c-1.34,2.38-2.68,4.76-4.03,7.15.11.62.8.89,1.13.56.32-.58.64-1.16.96-1.74h14.24c.32.58.64,1.16.96,1.74.33.33,1.02.06,1.13-.56-1.34-2.39-2.69-4.77-4.03-7.15ZM2.74,22.18c.44-.79.88-1.58,1.32-2.37h10.3c.44.79.88,1.58,1.32,2.37H2.74Z"/>
          <path d="M16.17,9.44c-.83,0-1.62-.24-2.28-.65-1.18-.72-1.99-1.99-2.08-3.45,0-.09,0-.18,0-.27,0-.97.32-1.87.86-2.59-.26-.04-.52-.07-.79-.09C7.17,1.93,1.43,2.67.35,4.64v11.14c0,.62.5,1.13,1.12,1.13h15.48c.62,0,1.12-.51,1.12-1.13v-6.78c-.57.28-1.22.44-1.9.44ZM3.43,14.33c-.86,0-1.56-.66-1.56-1.48s.7-1.48,1.56-1.48,1.55.66,1.55,1.48-.69,1.48-1.55,1.48ZM2.71,10.15c-.33,0-.6-.27-.6-.59v-3.63c0-.33.27-.59.6-.59h8.4c.09,1.87,1.19,3.47,2.78,4.27-.03.3-.29.54-.59.54H2.71ZM14.98,14.33c-.86,0-1.55-.66-1.55-1.48s.69-1.48,1.55-1.48,1.56.66,1.56,1.48-.7,1.48-1.56,1.48Z"/>
          <path d="M16.17,0c-1.82,0-3.41.95-4.3,2.39-.5.77-.78,1.69-.78,2.68,0,.09,0,.18.02.27.09,1.87,1.19,3.47,2.78,4.27.68.34,1.46.54,2.28.54.67,0,1.32-.13,1.9-.37,1.86-.76,3.17-2.58,3.17-4.71,0-2.8-2.27-5.07-5.07-5.07ZM18.07,9c-.57.28-1.22.44-1.9.44-.83,0-1.62-.24-2.28-.65-1.18-.72-1.99-1.99-2.08-3.45,0-.09,0-.18,0-.27,0-.97.32-1.87.86-2.59.79-1.08,2.07-1.77,3.51-1.77,2.41,0,4.36,1.95,4.36,4.36,0,1.73-1,3.23-2.46,3.93Z"/>
          <path d="M13.89,8.79v.82c-1.59-.8-2.69-2.4-2.78-4.27h.7c.09,1.46.9,2.73,2.08,3.45Z"/>
          <g>
            <rect x="13.41" y="4.31" width="3.37" height=".67" rx=".33" ry=".33" transform="translate(23.3 18.13) rotate(-138.42)"/>
            <rect x="15.56" y="4.31" width="4.46" height=".67" rx=".33" ry=".33" transform="translate(-.01 9.23) rotate(-29.09)"/>
          </g>
        </svg>
      
        <span class="font-semibold tracking-wide"
              :class="$pinia.state.value.ui?.sidebarCollapsed ? 'sr-only' : ''">RFMS</span>
      </div>
      <button
        v-if="!$pinia.state.value.ui?.sidebarCollapsed"
        class="inline-flex items-center justify-center w-9 h-9 rounded-lg border border-app bg-transparent text-[var(--sidebar-fg)] hover:bg-transparent"
        :aria-pressed="String(ui.sidebarCollapsed)"
        aria-label="Toggle sidebar"
        title="Toggle sidebar"
        @click="ui.toggleSidebarCollapsed()"
      >
        <svg viewBox="0 0 24 24" class="w-4 h-4"><path fill="currentColor" d="M3 4h18v2H3zm3 4h12v2H6zm-3 4h18v2H3zm3 4h12v2H6z"/></svg>
      </button>
      <button
        v-else
        class="inline-flex items-center justify-center w-9 h-9 rounded-lg border border-app bg-transparent text-[var(--sidebar-fg)] hover:bg-transparent"
        :aria-pressed="String(ui.sidebarCollapsed)"
        aria-label="Expand sidebar"
        title="Expand sidebar"
        @click="ui.toggleSidebarCollapsed()"
      >
        <svg viewBox="0 0 24 24" class="w-4 h-4"><path fill="currentColor" d="M4 11h16v2H4zM4 7h16v2H4zM4 15h10v2H4z"/></svg>
      </button>
    </div>

    <template v-if="auth.user">
      <nav class="space-y-1" :class="$pinia.state.value.ui?.sidebarCollapsed ? 'px-0' : 'px-2'">
        <RouterLink
          v-for="l in links"
          :key="l.to"
          :to="l.to"
          class="group flex items-center rounded-lg text-base sidebar-link"
          :class="{
            'justify-center h-16 w-full': $pinia.state.value.ui?.sidebarCollapsed,
            'px-3 py-2 gap-2': !$pinia.state.value.ui?.sidebarCollapsed,
            'sidebar-link-active': isActive(l.to)
          }"
          :aria-label="l.label"
          :title="l.label"
          :data-active="isActive(l.to) ? 'true' : 'false'"
          :aria-current="isActive(l.to) ? 'page' : undefined"
          @click="$emit('navigate')"
        >
          <i :class="l.icon" class="text-[1.1rem] leading-none"></i>
          <span class="leading-none transition-all duration-150"
                :class="$pinia.state.value.ui?.sidebarCollapsed ? 'w-0 opacity-0 overflow-hidden' : 'w-auto opacity-100'">
            {{ l.label }}
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
