<script setup>
import FailureCard from '@/components/FailureCard.vue'

defineProps({
  title: { type: String, required: true },
  items: { type: Array, default: () => [] },
})
</script>

<template>
  <section class="rounded-2xl border bg-white p-3 flex flex-col gap-3">
    <header class="flex items-center justify-between">
      <h3 class="text-sm font-semibold text-gray-700">{{ title }}</h3>
      <span class="text-xs text-gray-500">{{ items.length }}</span>
    </header>
    <div class="space-y-3">
      <FailureCard v-for="(it, i) in items" :key="i" :item="it" />
      <div v-if="items.length === 0" class="text-xs text-gray-400 border rounded-lg p-3">
        No items
      </div>
    </div>
  </section>
</template>