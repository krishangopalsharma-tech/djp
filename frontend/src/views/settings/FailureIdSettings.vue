<script setup>
</script>
<template>
  <div class="space-y-4">
    <h2 class="text-xl font-semibold">Failure ID Configuration</h2>
    <p class="text-app/80 text-sm">Configure Event ID/sequence rules, prefixes, padding, and resets. (Frontend placeholder)</p>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div>
        <label class="block text-sm font-medium mb-1">Prefix</label>
        <input class="field" placeholder="e.g., RF" />
      </div>
      <div>
        <label class="block text-sm font-medium mb-1">Padding (digits)</label>
        <input class="field" type="number" min="1" max="10" placeholder="4" />
      </div>
      <div>
        <label class="block text-sm font-medium mb-1">Reset Cycle</label>
        <select class="field">
          <option value="never">Never</option>
          <option value="yearly">Yearly</option>
          <option value="monthly">Monthly</option>
        </select>
      </div>
      <div>
        <label class="block text-sm font-medium mb-1">Preview</label>
        <input class="field" value="RF-2025-0001" readonly />
      </div>
    </div>

    <div class="flex gap-2">
      <button class="btn btn-primary">Save</button>
      <button class="btn">Reset</button>
    </div>
  </div>
</template>

