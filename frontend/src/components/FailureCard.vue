<script setup>
defineProps({
  item: { type: Object, required: true }, // { fail_id, status, severity, circuit, reported_at, assigned_to }
})
</script>

<template>
  <article class="card space-y-2">
    <div class="flex items-start justify-between gap-3">
      <h3 class="text-base font-semibold">{{ item.fail_id }}</h3>
      <span
        class="badge"
        :class="{
          'badge-danger': item.severity === 'Critical',
          'badge-warning': item.severity === 'High',
          'badge-neutral': item.severity === 'Low',
        }"
      >
        {{ item.severity }}
      </span>
    </div>

    <div class="text-xs text-muted">
      <span class="inline-block mr-3">
        <span class="font-medium text-app">Status:</span> {{ item.status }}
      </span>
      <span class="inline-block mr-3">
        <span class="font-medium text-app">Circuit:</span> {{ item.circuit }}
      </span>
    </div>

    <div class="text-xs text-muted">
      <span class="inline-block mr-3">
        <span class="font-medium text-app">Reported:</span> {{ item.reported_at }}
      </span>
      <span class="inline-block mr-3">
        <span class="font-medium text-app">Assigned:</span> {{ item.assigned_to }}
      </span>
    </div>

    <div class="pt-2">
      <button class="btn btn-outline btn-sm">View</button>
      <button class="btn btn-primary btn-sm ml-2">Update</button>
    </div>
  </article>
</template>
