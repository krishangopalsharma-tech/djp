<script setup>
defineProps({
  item: { type: Object, required: true }, // { fail_id, status, severity, circuit, reported_at, assigned_to }
})
</script>

<template>
  <div class="relative pl-8">
    <!-- line -->
    <div class="absolute left-3 top-0 bottom-0 w-px bg-gray-200"></div>
    <!-- dot -->
    <div class="absolute left-2 top-2 h-3 w-3 rounded-full"
         :class="{
           'bg-red-500': item.severity === 'Critical',
           'bg-amber-500': item.severity === 'High',
           'bg-gray-500': item.severity === 'Low'
         }"></div>

    <div class="rounded-xl border bg-white p-3">
      <div class="flex items-center justify-between">
        <div class="text-sm font-semibold">{{ item.fail_id }}</div>
        <span class="text-xs rounded-full px-2 py-0.5 border"
              :class="item.status === 'Resolved' ? 'bg-green-50 text-green-700 border-green-200' : 'bg-amber-50 text-amber-700 border-amber-200'">
          {{ item.status }}
        </span>
      </div>
      <div class="mt-1 text-xs text-gray-500">
        <span class="mr-3"><span class="font-medium text-gray-700">Severity:</span> {{ item.severity }}</span>
        <span class="mr-3"><span class="font-medium text-gray-700">Circuit:</span> {{ item.circuit }}</span>
      </div>
      <div class="mt-1 text-xs text-gray-500">
        <span class="mr-3"><span class="font-medium text-gray-700">Reported:</span> {{ item.reported_at }}</span>
        <span class="mr-3"><span class="font-medium text-gray-700">Assigned:</span> {{ item.assigned_to }}</span>
      </div>
    </div>
  </div>
</template>