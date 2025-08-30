<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'

const props = defineProps({
  sections: { type: Array, default: () => [] },     // ['Section A', 'Section B', ...]
  modelValue: { type: Array, default: () => [] },   // selected sections
  maxInline: { type: Number, default: 6 },          // how many selected chips to preview on the button
  placeholder: { type: String, default: 'Filter sections...' },
})
const emit = defineEmits(['update:modelValue'])

const open = ref(false)
const query = ref('')
const host = ref(null)

const selected = computed(() => new Set(props.modelValue || []))
const filteredSections = computed(() => {
  const q = query.value.trim().toLowerCase()
  if (!q) return props.sections
  return props.sections.filter(s => String(s).toLowerCase().includes(q))
})
function toggle(s) {
  const next = new Set(selected.value)
  next.has(s) ? next.delete(s) : next.add(s)
  emit('update:modelValue', Array.from(next))
}
function setAll() { emit('update:modelValue', [...props.sections]) }
function clearAll() { emit('update:modelValue', []) }

const selectedList = computed(() => props.sections.filter(s => selected.value.has(s)))
const inlineChips = computed(() => selectedList.value.slice(0, props.maxInline))
const hiddenCount = computed(() => Math.max(0, selectedList.value.length - props.maxInline))

function onDocClick(e) {
  if (!open.value) return
  if (host.value && !host.value.contains(e.target)) open.value = false
}
onMounted(() => document.addEventListener('mousedown', onDocClick))
onBeforeUnmount(() => document.removeEventListener('mousedown', onDocClick))
</script>

<template>
  <div ref="host" class="relative">
    <!-- Trigger button -->
    <button
      type="button"
      class="w-full sm:w-auto inline-flex items-center gap-2 rounded-lg border px-3 py-2 text-sm bg-white hover:bg-gray-50"
      @click="open = !open"
      :title="selectedList.length ? selectedList.join(', ') : 'All sections selected'"
    >
      <svg viewBox="0 0 24 24" class="w-4 h-4"><path fill="currentColor" d="M3 5h18v2H3zm0 6h12v2H3zm0 6h8v2H3z"/></svg>
      <span class="font-medium">Sections</span>

        <!-- selection preview -->
        <span v-if="selectedList.length === 0 || selectedList.length === props.sections.length" class="text-gray-500">
          • All
        </span>
        <span v-else class="flex flex-wrap gap-1">

        <span
          v-for="s in inlineChips"
          :key="s"
          class="px-2 py-0.5 rounded-full text-xs border bg-gray-50"
        >{{ s }}</span>
        <span v-if="hiddenCount" class="text-gray-500 text-xs">+{{ hiddenCount }}</span>
      </span>

      <svg viewBox="0 0 24 24" class="w-4 h-4 ml-1"><path fill="currentColor" d="M7 10l5 5 5-5z"/></svg>
    </button>

    <!-- Popover -->
    <div
      v-show="open"
      class="absolute z-50 mt-2 w-[min(90vw,28rem)] rounded-xl border bg-white shadow-lg"
    >
      <!-- search + actions -->
      <div class="p-3 border-b flex items-center gap-2">
        <svg viewBox="0 0 24 24" class="w-4 h-4 text-gray-500"><path fill="currentColor" d="M15.5 14h-.79l-.28-.27A6.471 6.471 0 0 0 16 9.5 6.5 6.5 0 1 0 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 5l1.5-1.5l-5-5ZM9.5 14A4.5 4.5 0 1 1 14 9.5A4.5 4.5 0 0 1 9.5 14Z"/></svg>
        <input
          v-model="query"
          :placeholder="placeholder"
          class="flex-1 rounded-lg border px-3 py-1.5 text-sm"
        />
        <button class="text-xs px-2 py-1 rounded-lg border hover:bg-gray-50" @click="setAll">All</button>
        <button class="text-xs px-2 py-1 rounded-lg border hover:bg-gray-50" @click="clearAll">None</button>
      </div>

      <!-- list -->
      <div class="max-h-72 overflow-auto p-2">
        <template v-if="filteredSections.length">
          <label
            v-for="s in filteredSections"
            :key="s"
            class="flex items-center gap-2 px-2 py-1.5 rounded hover:bg-gray-50 cursor-pointer"
          >
            <input type="checkbox" class="h-4 w-4" :checked="selected.has(s)" @change="toggle(s)" />
            <span class="text-sm">{{ s }}</span>
          </label>
        </template>
        <div v-else class="p-6 text-center text-sm text-gray-500">No matches</div>
      </div>

      <!-- footer -->
      <div class="p-2 border-t flex items-center justify-end gap-2">
        <span class="text-xs text-gray-500 mr-auto">
          {{ selectedList.length }} / {{ sections.length }} selected
        </span>
        <button class="text-sm px-2 py-1 rounded-lg border hover:bg-gray-50" @click="open=false">Close</button>
      </div>
    </div>
  </div>
</template>