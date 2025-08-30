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
  <div class="flex flex-wrap items-center gap-2">
    <span class="text-sm text-gray-500 mr-1">Sections:</span>

    <button
      class="px-2.5 py-1 text-xs rounded-full border"
      :class="(modelValue?.length || 0) === sections.length && sections.length
        ? 'bg-gray-900 text-white border-gray-900' : 'bg-white text-gray-700 hover:bg-gray-100'"
      @click="setAll"
      title="Select all sections"
    >All</button>

    <button
      class="px-2.5 py-1 text-xs rounded-full border"
      :class="(modelValue?.length || 0) === 0
        ? 'bg-gray-900 text-white border-gray-900' : 'bg-white text-gray-700 hover:bg-gray-100'"
      @click="clearAll"
      title="Clear all sections"
    >None</button>

    <button
      v-for="s in sections" :key="s"
      class="px-2.5 py-1 text-xs rounded-full border transition"
      :class="isSelected(s)
        ? 'bg-gray-900 text-white border-gray-900'
        : 'bg-white text-gray-700 hover:bg-gray-100'"
      @click="toggle(s)"
    >{{ s }}</button>
  </div>
</template>