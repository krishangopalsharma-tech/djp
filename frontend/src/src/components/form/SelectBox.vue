<script setup>
defineProps({
  label: String,
  modelValue: [String, Number],
  options: { type: Array, default: () => [] }, // [{label, value}]
  error: String,
})
defineEmits(['update:modelValue'])
</script>

<template>
  <label class="block space-y-1">
    <span class="text-sm text-app">{{ label }}</span>
    <select
      class="field"
      :value="modelValue"
      @change="$emit('update:modelValue', $event.target.value)"
    >
      <option value="" disabled>Select…</option>
      <option v-for="o in options" :key="o.value" :value="o.value">{{ o.label }}</option>
    </select>
    <p v-if="error" class="text-xs text-red-600">{{ error }}</p>
  </label>
</template>
