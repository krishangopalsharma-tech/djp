<script setup>
import { ref } from 'vue'
import AppSidebar from './components/AppSidebar.vue'
import AppTopbar from './components/AppTopbar.vue'
import Toasts from '@/components/ui/Toasts.vue'
const sidebarOpen = ref(false)
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Sidebar: fixed always; slide-in on mobile -->
    <div
      class="fixed inset-y-0 left-0 z-40 w-64 bg-white border-r transform transition-transform"
      :class="sidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'"
    >
      <AppSidebar @navigate="sidebarOpen = false" />
    </div>

    <!-- Main content: shifted right on md+ -->
    <div class="min-h-screen flex flex-col md:ml-64">
      <AppTopbar @toggleSidebar="sidebarOpen = true" />
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
</style>