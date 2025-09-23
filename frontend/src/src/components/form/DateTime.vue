<script setup>
defineProps({
  label: String,
  modelValue: String,   // ISO-ish: "2025-08-19T08:30"
  error: String,
})
defineEmits(['update:modelValue'])
</script>

<template>
  <label class="block space-y-1">
    <span class="text-sm text-app">{{ label }}</span>
    <input
      type="datetime-local"
      class="field"
      :value="modelValue"
      @input="$emit('update:modelValue', $event.target.value)"
    />
    <p v-if="error" class="text-xs text-red-600">{{ error }}</p>
  </label>
</template>
