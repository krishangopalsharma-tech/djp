<script setup>
</script>
<template>
  <div class="space-y-4">
    <h2 class="text-xl font-semibold">Station and Section Management</h2>
    <p class="text-app/80 text-sm">Maintain stations, sections, and mappings. (Frontend placeholder)</p>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div>
        <label class="block text-sm font-medium mb-1">Station</label>
        <input class="field" placeholder="Dadar" />
      </div>
      <div>
        <label class="block text-sm font-medium mb-1">Code</label>
        <input class="field" placeholder="DDR" />
      </div>
      <div>
        <label class="block text-sm font-medium mb-1">Section</label>
        <input class="field" placeholder="Central Line" />
      </div>
    </div>

    <div class="flex gap-2">
      <button class="btn btn-primary">Save</button>
      <button class="btn">Bulk Upload</button>
    </div>
  </div>
</template>

