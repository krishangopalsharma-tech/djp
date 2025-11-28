<script setup>
import { ref, watch, computed, onMounted, onBeforeUnmount } from 'vue'

const props = defineProps({
  modelValue: [String, Number, Object, Array, null],
  options: { type: Array, default: () => [] },
  placeholder: { type: String, default: 'Select…' },
  disabled: { type: Boolean, default: false },
  clearable: { type: Boolean, default: true },
  labelKey: { type: String, default: 'label' },
  valueKey: { type: String, default: 'value' },
  multiple: { type: Boolean, default: false },
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
  if (val == null || val === '' || (Array.isArray(val) && val.length === 0)) return ''
  
  if (props.multiple) {
      if (!Array.isArray(val)) return '';
      if (val.length === 1) {
          const found = props.options.find(o => (o[props.valueKey] === val[0]) || (o === val[0]))
          return found ? (found[props.labelKey] ?? String(found)) : String(val[0])
      }
      return `${val.length} selected`
  }

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
  
  if (props.multiple) {
      const current = Array.isArray(props.modelValue) ? [...props.modelValue] : []
      const idx = current.indexOf(val)
      if (idx > -1) {
          current.splice(idx, 1)
      } else {
          current.push(val)
      }
      emit('update:modelValue', current)
      // Keep menu open for multiple selection
      requestAnimationFrame(() => inputEl.value?.focus())
  } else {
      emit('update:modelValue', val)
      closeMenu()
      controlButton.value?.blur()
      
      // --- SET FLAG AND CLEAR IT AFTER A SHORT DELAY ---
      justClosed = true;
      setTimeout(() => {
        justClosed = false;
      }, 150); // 150ms cooldown period
  }
}

function clearSelection(e) {
  e?.stopPropagation()
  if (!props.clearable) return
  emit('update:modelValue', props.multiple ? [] : null)
  query.value = ''
  if (!props.multiple) openMenu()
}

function selectAll() {
    if (!props.multiple) return
    const allValues = props.options.map(o => o[props.valueKey] ?? o)
    emit('update:modelValue', allValues)
}

function deselectAll() {
    if (!props.multiple) return
    emit('update:modelValue', [])
}

function isSelected(opt) {
    const val = opt?.[props.valueKey] ?? opt
    if (props.multiple) {
        return Array.isArray(props.modelValue) && props.modelValue.includes(val)
    }
    return val === props.modelValue
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
  if (!open.value && !props.multiple) query.value = ''
})
</script>

<template>
  <div ref="rootEl" class="relative">
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
          v-if="clearable && ((!multiple && modelValue != null && modelValue !== '') || (multiple && modelValue?.length > 0))"
          class="text-muted hover:text-app"
          title="Clear"
          @click.stop="clearSelection"
        >✕</button>
        <span class="text-muted">▾</span>
      </span>
    </button>
    <div
      v-if="open"
      class="absolute z-50 mt-1 w-full rounded-lg border bg-card text-app border-app shadow-lg max-h-60 overflow-auto"
      role="listbox"
    >
      <div v-if="multiple" class="px-3 py-2 border-b flex gap-2">
          <button type="button" class="text-xs text-primary hover:underline" @click.stop="selectAll">Select All</button>
          <button type="button" class="text-xs text-muted hover:text-app" @click.stop="deselectAll">Deselect All</button>
      </div>
      <div
        v-for="(opt, i) in filtered"
        :key="opt[valueKey] ?? String(opt)"
        class="px-3 py-2 text-sm cursor-pointer flex items-center justify-between hover-primary"
        :class="[
          i === hoverIndex ? 'bg-primary-tint' : '',
          isSelected(opt) ? 'selected-primary' : ''
        ]"
        @mouseenter="hoverIndex = i"
        @mouseleave="hoverIndex = -1"
        @click.stop="selectOption(opt)"
      >
        <span class="truncate flex items-center gap-2">
            <input v-if="multiple" type="checkbox" :checked="isSelected(opt)" class="pointer-events-none" />
            {{ opt[labelKey] ?? String(opt) }}
        </span>
        <span v-if="isSelected(opt) && !multiple" class="text-xs text-muted">✓</span>
      </div>
      <div v-if="filtered.length === 0" class="px-3 py-2 text-sm text-muted">No results</div>
    </div>
  </div>
</template>