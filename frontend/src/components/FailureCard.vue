<script setup>
defineProps({
  item: { type: Object, required: true }, // { fail_id, status, severity, circuit, reported_at, assigned_to }
})
</script>

<template>
  <article class="rounded-2xl border bg-white p-4 space-y-2">
    <div class="flex items-start justify-between gap-3">
      <h3 class="text-base font-semibold">{{ item.fail_id }}</h3>
      <span
        class="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium"
        :class="{
          'bg-red-100 text-red-700': item.severity === 'Critical',
          'bg-amber-100 text-amber-700': item.severity === 'High',
          'bg-gray-100 text-gray-700': item.severity === 'Low',
        }"
      >
        {{ item.severity }}
      </span>
    </div>

    <div class="text-xs text-gray-500">
      <span class="inline-block mr-3">
        <span class="font-medium text-gray-700">Status:</span> {{ item.status }}
      </span>
      <span class="inline-block mr-3">
        <span class="font-medium text-gray-700">Circuit:</span> {{ item.circuit }}
      </span>
    </div>

    <div class="text-xs text-gray-500">
      <span class="inline-block mr-3">
        <span class="font-medium text-gray-700">Reported:</span> {{ item.reported_at }}
      </span>
      <span class="inline-block mr-3">
        <span class="font-medium text-gray-700">Assigned:</span> {{ item.assigned_to }}
      </span>
    </div>

    <div class="pt-2">
      <button class="h-8 px-3 rounded-lg border text-xs bg-white hover:bg-gray-50">View</button>
      <button class="h-8 px-3 rounded-lg bg-gray-900 text-white text-xs ml-2">Update</button>
    </div>
  </article>
</template>