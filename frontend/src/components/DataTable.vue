<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  columns: { type: Array, required: true }, // [{ key, label, sortable?, width?, align?, sortAccessor? }]
  rows: { type: Array, required: true },    // [{ [key]: value }]
  defaultSortKey: { type: String, default: '' },
  defaultSortDir: { type: String, default: 'asc' }, // 'asc' | 'desc'
})
const emit = defineEmits(['rowclick'])

const sortKey = ref(props.defaultSortKey || (props.columns[0]?.key || ''))
const sortDir = ref(props.defaultSortDir)

function toggleSort(key, sortable = true) {
  if (!sortable) return
  if (sortKey.value === key) {
    sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortKey.value = key
    sortDir.value = 'asc'
  }
}

const sortedRows = computed(() => {
  const data = Array.isArray(props.rows) ? [...props.rows] : []
  const col = props.columns.find(c => c.key === sortKey.value)
  if (!col) return data
  const dir = sortDir.value === 'asc' ? 1 : -1
  const acc = typeof col.sortAccessor === 'function'
    ? (r) => col.sortAccessor(r)
    : (r) => r[col.key]
  return data.sort((a, b) => {
    const av = acc(a)
    const bv = acc(b)
    if (av == null && bv == null) return 0
    if (av == null) return -1 * dir
    if (bv == null) return  1 * dir
    const na = Number(av), nb = Number(bv)
    const va = Number.isNaN(na) ? String(av) : na
    const vb = Number.isNaN(nb) ? String(bv) : nb
    return (va > vb ? 1 : va < vb ? -1 : 0) * dir
  })
})
</script>

<template>
  <div class="overflow-x-auto rounded-2xl border-app bg-card text-app">
    <table class="min-w-full text-sm">
      <thead class="bg-card">
        <tr>
          <th v-for="c in columns" :key="c.key"
              :class="['font-semibold text-app px-4 py-3 select-none', c.align || 'text-left']"
              :style="c.width ? { width: c.width } : null"
              @click="toggleSort(c.key, c.sortable !== false)"
              role="columnheader"
              :aria-sort="sortKey===c.key ? (sortDir==='asc'?'ascending':'descending') : 'none'">
            <div class="inline-flex items-center gap-1">
              <span>{{ c.label }}</span>
              <span v-if="c.sortable !== false" class="text-xs text-muted">
                <span v-if="sortKey!==c.key">↕</span>
                <span v-else>{{ sortDir==='asc' ? '▲' : '▼' }}</span>
              </span>
            </div>
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(r, i) in sortedRows" :key="i" class="border-t hover-primary cursor-pointer"
            @click="emit('rowclick', r)">
          <td v-for="c in columns" :key="c.key" :class="['px-4 py-3', c.align || 'text-left']">
            <slot :name="c.key" :row="r">
              {{ r[c.key] }}
            </slot>
          </td>
        </tr>
        <tr v-if="sortedRows.length === 0" class="border-t">
          <td :colspan="columns.length" class="px-4 py-6 text-center text-muted">
            No data
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
