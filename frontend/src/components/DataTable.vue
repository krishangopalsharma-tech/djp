<script setup>
defineProps({
  columns: { type: Array, required: true }, // [{ key, label }]
  rows: { type: Array, required: true },    // [{ [key]: value }]
})
</script>

<template>
  <div class="overflow-x-auto rounded-2xl border bg-white">
    <table class="min-w-full text-sm">
      <thead class="bg-gray-50">
        <tr>
          <th v-for="c in columns" :key="c.key"
              class="text-left font-semibold text-gray-600 px-4 py-3">
            {{ c.label }}
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(r, i) in rows" :key="i" class="border-t hover:bg-gray-50">
          <td v-for="c in columns" :key="c.key" class="px-4 py-3">
            <slot :name="c.key" :row="r">
              {{ r[c.key] }}
            </slot>
          </td>
        </tr>
        <tr v-if="rows.length === 0" class="border-t">
          <td :colspan="columns.length" class="px-4 py-6 text-center text-gray-500">
            No data
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>