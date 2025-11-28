<script setup>
defineProps({
  label: String,
  modelValue: [String, Number],
  placeholder: String,
  error: String,
  type: { type: String, default: 'text' },
})
defineEmits(['update:modelValue'])
</script>

<template>
  <label class="block space-y-1">
    <span class="text-sm text-app">{{ label }}</span>
    <input
      :type="type"
      class="h-10 w-full rounded-lg border-app bg-card text-app px-3 text-sm"
      :placeholder="placeholder"
      :value="modelValue"
      @input="$emit('update:modelValue', $event.target.value)"
    />
    <p v-if="error" class="text-xs text-red-600">{{ error }}</p>
  </label>
</template>
