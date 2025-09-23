<script setup>
import { useUIStore } from '@/stores/ui'
import { ref } from 'vue'
import AppSidebar from './components/AppSidebar.vue'
import AppTopbar from './components/AppTopbar.vue'
import Toasts from '@/components/ui/Toasts.vue'
const ui = useUIStore()
// Default: open on md+ screens, closed on mobile
const sidebarOpen = ref(typeof window !== 'undefined' ? window.matchMedia('(min-width: 768px)').matches : false)

function onTopbarToggle() {
  const isDesktop = typeof window !== 'undefined' && window.matchMedia('(min-width: 768px)').matches
  if (isDesktop) {
    ui.toggleSidebarCollapsed()
  } else {
    sidebarOpen.value = !sidebarOpen.value
  }
}

// Sidebar drag-resize
let resizing = false
function onSidebarPointerDown(e){
  resizing = true
  window.addEventListener('pointermove', onSidebarPointerMove)
  window.addEventListener('pointerup', onSidebarPointerUp)
  e.preventDefault()
}
function onSidebarPointerMove(e){
  if (!resizing) return
  // sidebar anchored at left=0; use clientX as width
  ui.setSidebarWidth(e.clientX)
}
function onSidebarPointerUp(){
  resizing = false
  ui.snapSidebar()
  window.removeEventListener('pointermove', onSidebarPointerMove)
  window.removeEventListener('pointerup', onSidebarPointerUp)
}
</script>

<template>
  <div class="min-h-screen bg-app text-app" :style="{ '--sidebar-w': ui.computedSidebarWidth + 'px' }">
    <!-- Sidebar: fixed always; slide-in on mobile -->
    <div
      class="fixed inset-y-0 left-0 z-40 sidebar transform transition-transform transition-all duration-200 motion-reduce:transition-none"
      :class="sidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'"
      :style="{ width: ui.computedSidebarWidth + 'px' }"
      :data-collapsed="ui.sidebarCollapsed"
      :data-sidebar-width="ui.computedSidebarWidth"
    >
      <AppSidebar @navigate="sidebarOpen = false" />
      <!-- Drag handle -->
      <div
        class="absolute top-0 right-0 h-full w-2 cursor-col-resize bg-[var(--sidebar-bg)] focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--sidebar-fg)]/40 focus-visible:ring-offset-0"
        title="Drag to resize"
        tabindex="0"
        role="separator"
        aria-orientation="vertical"
        :aria-valuemin="ui.SIDEBAR_MIN"
        :aria-valuemax="ui.SIDEBAR_MAX"
        :aria-valuenow="ui.computedSidebarWidth"
        aria-label="Resize sidebar"
        @pointerdown="onSidebarPointerDown"
        @keydown.left.prevent="ui.setSidebarWidth(ui.sidebarWidth - 10)"
        @keydown.right.prevent="ui.setSidebarWidth(ui.sidebarWidth + 10)"
        @keydown.enter.prevent="ui.snapSidebar(ui.sidebarWidth)"
      />
    </div>

    <!-- Main content: shifted right on md+ -->
    <div class="min-h-screen flex flex-col ml-sidebar transition-all duration-200 motion-reduce:transition-none">
      <AppTopbar @toggleSidebar="onTopbarToggle" />
      <main class="p-6">
        <RouterView />
      </main>
    </div>

    <!-- Backdrop for mobile -->
    <div
      v-if="sidebarOpen"
      class="fixed inset-0 bg-black/30 z-30 md:hidden"
      @click="sidebarOpen = false"
    />
    <Toasts />
  </div>
</template>

<style scoped>
@media (min-width: 768px) {
  .ml-sidebar { margin-left: var(--sidebar-w, 256px); }
}
</style>
