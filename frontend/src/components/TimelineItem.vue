<script setup>
defineProps({
  item: { type: Object, required: true }, // { fail_id, status, severity, circuit, reported_at, assigned_to }
})
</script>

<template>
  <div class="relative pl-8">
    <!-- line -->
    <div class="absolute left-3 top-0 bottom-0 w-px bg-[var(--border)]"></div>
    <!-- dot -->
    <div class="absolute left-2 top-2 h-3 w-3 rounded-full"
         :class="{
           'bg-[var(--danger)]': item.severity === 'Critical',
           'bg-[var(--warning)]': item.severity === 'High',
           'bg-[var(--neutral)]': item.severity === 'Low'
         }"></div>

    <div class="rounded-xl border-app bg-card text-app p-3">
      <div class="flex items-center justify-between">
        <div class="text-sm font-semibold">{{ item.fail_id }}</div>
        <span class="badge"
              :class="item.status === 'Resolved' ? 'badge-success' : 'badge-warning'">
          {{ item.status }}
        </span>
      </div>
      <div class="mt-1 text-xs text-muted">
        <span class="mr-3"><span class="font-medium text-app">Severity:</span> {{ item.severity }}</span>
        <span class="mr-3"><span class="font-medium text-app">Circuit:</span> {{ item.circuit }}</span>
      </div>
      <div class="mt-1 text-xs text-muted">
        <span class="mr-3"><span class="font-medium text-app">Reported:</span> {{ item.reported_at }}</span>
        <span class="mr-3"><span class="font-medium text-app">Assigned:</span> {{ item.assigned_to }}</span>
      </div>
    </div>
  </div>
</template>
