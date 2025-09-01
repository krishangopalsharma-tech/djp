<script setup>
import { Bell, Pencil, Trash2, ChevronLeft, ChevronRight } from 'lucide-vue-next'

defineProps({
  columns: { type: Array, required: true }, // [{ key, label }]
  rows: { type: Array, required: true },    // [{ [key]: value }]
})
</script>

<template>
  <div class="overflow-x-auto rounded-2xl border-app bg-card text-app">
    <table class="min-w-full text-sm">
      <thead class="bg-card">
        <tr>
          <th v-for="c in columns" :key="c.key"
              class="text-left font-semibold text-app px-4 py-3">
            {{ c.label }}
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(r, i) in rows" :key="i" class="border-t hover-primary">
          <td v-for="c in columns" :key="c.key" class="px-4 py-3">
            <slot :name="c.key" :row="r">
              {{ r[c.key] }}
            </slot>
          </td>
        </tr>
        <tr v-if="rows.length === 0" class="border-t">
          <td :colspan="columns.length" class="px-4 py-6 text-center text-muted">
            No data
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
