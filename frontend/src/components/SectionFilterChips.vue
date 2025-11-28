<script setup>
const props = defineProps({
  sections: { type: Array, default: () => [] },   // ['Section A', 'Section B', ...]
  modelValue: { type: Array, default: () => [] }, // selected sections
})
const emit = defineEmits(['update:modelValue'])

function setAll() {
  emit('update:modelValue', [...props.sections])
}
function clearAll() {
  emit('update:modelValue', [])
}
function toggle(s) {
  const set = new Set(props.modelValue || [])
  set.has(s) ? set.delete(s) : set.add(s)
  emit('update:modelValue', Array.from(set))
}
function isSelected(s) {
  return (props.modelValue || []).includes(s)
}
</script>

<template>
  <div class="chip-group flex-wrap items-center gap-2">
    <span class="text-sm text-muted mr-1">Sections:</span>

    <button
      class="chip text-xs"
      :class="(modelValue?.length || 0) === sections.length && sections.length
        ? 'selected-primary' : 'text-app hover-primary'"
      @click="setAll"
      title="Select all sections"
    >All</button>

    <button
      class="chip text-xs"
      :class="(modelValue?.length || 0) === 0
        ? 'selected-primary' : 'text-app hover-primary'"
      @click="clearAll"
      title="Clear all sections"
    >None</button>

    <button
      v-for="s in sections" :key="s"
      class="chip text-xs transition"
      :class="isSelected(s)
        ? 'selected-primary'
        : 'text-app hover-primary'"
      @click="toggle(s)"
    >{{ s }}</button>
  </div>
</template>
