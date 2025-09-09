<script setup>
import { ref, watch, computed, onMounted, onBeforeUnmount } from 'vue'

const props = defineProps({
  modelValue: [String, Number, Object, null],
  options: { type: Array, default: () => [] },
  placeholder: { type: String, default: 'Select…' },
  disabled: { type: Boolean, default: false },
  clearable: { type: Boolean, default: true },
  labelKey: { type: String, default: 'label' },
  valueKey: { type: String, default: 'value' },
})
const emit = defineEmits(['update:modelValue'])

const open = ref(false)
const query = ref('')
const hoverIndex = ref(-1)
const rootEl = ref(null)
const inputEl = ref(null)
const controlButton = ref(null)

// --- FLAG TO PREVENT IMMEDIATE REOPENING ---
let justClosed = false;

const selectedLabel = computed(() => {
  const val = props.modelValue
  if (val == null || val === '') return ''
  const found = props.options.find(o => (o[props.valueKey] === val) || (o === val))
  return found ? (found[props.labelKey] ?? String(found)) : String(val)
})

const filtered = computed(() => {
  const q = query.value.trim().toLowerCase()
  if (!q) return props.options
  return props.options.filter(o => String(o[props.labelKey] ?? o).toLowerCase().includes(q))
})

function toggleMenu() {
    if (justClosed) {
        return;
    }
    if (open.value) {
        closeMenu();
    } else {
        openMenu();
    }
}

function openMenu() {
  if (props.disabled) return
  open.value = true
  hoverIndex.value = -1
  requestAnimationFrame(() => inputEl.value?.focus())
}

function closeMenu() {
  open.value = false
}

function selectOption(opt) {
  const val = opt?.[props.valueKey] ?? opt
  emit('update:modelValue', val)
  closeMenu()
  controlButton.value?.blur()

  // --- SET FLAG AND CLEAR IT AFTER A SHORT DELAY ---
  justClosed = true;
  setTimeout(() => {
    justClosed = false;
  }, 150); // 150ms cooldown period
}

function clearSelection(e) {
  e?.stopPropagation()
  if (!props.clearable) return
  emit('update:modelValue', null)
  query.value = ''
  openMenu()
}

function onKeydown(e) {
  if (!open.value && (e.key === 'Enter' || e.key === 'ArrowDown' || e.key === ' ')) {
    e.preventDefault(); openMenu(); return
  }
  if (!open.value) return
  const max = filtered.value.length - 1
  if (e.key === 'ArrowDown') { e.preventDefault(); hoverIndex.value = Math.min(max, hoverIndex.value + 1) }
  else if (e.key === 'ArrowUp') { e.preventDefault(); hoverIndex.value = Math.max(0, hoverIndex.value - 1) }
  else if (e.key === 'Enter') { e.preventDefault(); if (filtered.value[hoverIndex.value]) selectOption(filtered.value[hoverIndex.value]) }
  else if (e.key === 'Escape') { e.preventDefault(); closeMenu() }
}

function onClickOutside(e) {
  if (!rootEl.value) return
  if (!rootEl.value.contains(e.target)) closeMenu()
}

onMounted(() => document.addEventListener('mousedown', onClickOutside))
onBeforeUnmount(() => document.removeEventListener('mousedown', onClickOutside))

watch(() => props.modelValue, (v) => {
  if (!open.value) query.value = ''
})
</script>

<template>
  <div ref="rootEl" class="relative">
    <!-- control -->
    <button
      ref="controlButton" type="button"
      class="field-shell h-11 w-full text-left px-3 text-sm flex items-center justify-between gap-2"
      :class="disabled ? 'opacity-60 cursor-not-allowed' : ''"
      :aria-expanded="open"
      @click="toggleMenu"
      @keydown="onKeydown"
    >
      <span class="truncate" v-if="!open">
        <span v-if="selectedLabel" class="text-app">{{ selectedLabel }}</span>
        <span v-else class="text-muted">{{ placeholder }}</span>
      </span>
      <input
        v-else
        ref="inputEl"
        v-model="query"
        type="text"
        class="w-full outline-none bg-transparent text-app h-11"
        :placeholder="placeholder"
        @keydown.stop="onKeydown"
      />
      <span class="flex items-center gap-2 shrink-0">
        <button
          v-if="clearable && modelValue != null && modelValue !== ''"
          class="text-muted hover:text-app"
          title="Clear"
          @click.stop="clearSelection"
        >✕</button>
        <span class="text-muted">▾</span>
      </span>
    </button>

    <!-- dropdown -->
    <div
      v-if="open"
      class="absolute z-50 mt-1 w-full rounded-lg border bg-card text-app border-app shadow-lg max-h-60 overflow-auto"
      role="listbox"
    >
      <div
        v-for="(opt, i) in filtered"
        :key="opt[valueKey] ?? String(opt)"
        class="px-3 py-2 text-sm cursor-pointer flex items-center justify-between hover-primary"
        :class="[
          i === hoverIndex ? 'bg-primary-tint' : '',
          (opt[valueKey] ?? opt) === modelValue ? 'selected-primary' : ''
        ]"
        @mouseenter="hoverIndex = i"
        @mouseleave="hoverIndex = -1"
        @click.stop="selectOption(opt)"
      >
        <span class="truncate">{{ opt[labelKey] ?? String(opt) }}</span>
        <span v-if="(opt[valueKey] ?? opt) === modelValue" class="text-xs text-muted">✓</span>
      </div>
      <div v-if="filtered.length === 0" class="px-3 py-2 text-sm text-muted">No results</div>
    </div>
  </div>
</template>