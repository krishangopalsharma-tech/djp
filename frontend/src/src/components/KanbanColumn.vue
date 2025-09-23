<script setup>
import FailureCard from '@/components/FailureCard.vue'

defineProps({
  title: { type: String, required: true },
  items: { type: Array, default: () => [] },
})
</script>

<template>
  <section class="rounded-2xl border-app bg-card text-app p-3 flex flex-col gap-3">
    <header class="flex items-center justify-between">
      <h3 class="text-sm font-semibold text-app">{{ title }}</h3>
      <span class="text-xs text-muted">{{ items.length }}</span>
    </header>
    <div class="space-y-3">
      <FailureCard v-for="(it, i) in items" :key="i" :item="it" />
      <div v-if="items.length === 0" class="text-xs text-muted border-app bg-card rounded-lg p-3">
        No items
      </div>
    </div>
  </section>
</template>
