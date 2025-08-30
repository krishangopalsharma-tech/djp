<script setup>
import DataTable from '@/components/DataTable.vue'
import FailureCard from '@/components/FailureCard.vue'
import KanbanColumn from '@/components/KanbanColumn.vue'
import TimelineItem from '@/components/TimelineItem.vue'
import Spinner from '@/components/ui/Spinner.vue'

import { ref, computed, onMounted } from 'vue'
import { listFailures } from '@/api/mock'

const view = ref('table') // table | cards | board | timeline
const query = ref('')

const loading = ref(false)
const error = ref('')
const rows = ref([])

onMounted(async () => {
  loading.value = true
  error.value = ''
  try {
    const { results } = await listFailures()
    rows.value = results
  } catch (e) {
    error.value = e?.message || 'Failed to load logbook data'
  } finally {
    loading.value = false
  }
})

const columns = [
  { key: 'fail_id', label: 'Fail ID' },
  { key: 'status', label: 'Status' },
  { key: 'severity', label: 'Severity' },
  { key: 'circuit', label: 'Circuit' },
  { key: 'reported_at', label: 'Reported At' },
  { key: 'assigned_to', label: 'Assigned To' },
]

const filteredRows = computed(() => {
  const q = query.value.trim().toLowerCase()
  if (!q) return rows.value
  return rows.value.filter(r => Object.values(r).some(v => String(v).toLowerCase().includes(q)))
})

const statuses = ['Active', 'Resolved']
const byStatus = computed(() =>
  Object.fromEntries(statuses.map(s => [s, filteredRows.value.filter(r => r.status === s)]))
)
</script>

<template>
  <div class="space-y-4">
    <!-- Toolbar -->
    <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h2 class="text-2xl font-semibold">Logbook</h2>
        <p class="text-sm text-gray-500">Active and recent failures</p>
      </div>

      <div class="flex items-center gap-2">
        <input
          v-model="query"
          type="text"
          placeholder="Search..."
          class="h-10 w-56 rounded-lg border px-3 text-sm bg-white"
        />
        <div class="inline-flex rounded-lg border bg-white p-1">
          <button
            v-for="m in ['table','cards','board','timeline']"
            :key="m"
            class="px-3 py-1.5 text-sm rounded-md capitalize"
            :class="view === m ? 'bg-gray-900 text-white' : 'text-gray-700 hover:bg-gray-100'"
            @click="view = m"
          >
            {{ m }}
          </button>
        </div>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="rounded-2xl border bg-white p-6 text-sm text-gray-700 flex items-center gap-3">
      <Spinner :size="18" />
      Loading logbook...
    </div>

    <!-- Error -->
    <div v-else-if="error" class="rounded-2xl border bg-white p-6 text-sm text-red-600">
      {{ error }}
    </div>

    <!-- Views -->
    <div v-else>
      <!-- Board view -->
      <div v-if="view === 'board'" class="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <KanbanColumn v-for="s in statuses" :key="s" :title="s" :items="byStatus[s]" />
      </div>

      <!-- Cards view -->
      <div v-else-if="view === 'cards'" class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <FailureCard v-for="(r, i) in filteredRows" :key="i" :item="r" />
      </div>

      <!-- Table view -->
      <DataTable v-else-if="view === 'table'" :columns="columns" :rows="filteredRows" />

      <!-- Timeline view -->
      <div v-else-if="view === 'timeline'" class="space-y-4">
        <TimelineItem v-for="(r, i) in filteredRows" :key="i" :item="r" />
      </div>

      <!-- Fallback -->
      <div v-else class="rounded-2xl border bg-white p-6 text-sm text-gray-500">
        "{{ view }}" view coming soon.
      </div>
    </div>
  </div>
</template>