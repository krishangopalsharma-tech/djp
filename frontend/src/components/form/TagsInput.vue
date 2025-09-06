<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  modelValue: { type: Array, default: () => [] },   // user-added tags
  preset:     { type: Array, default: () => [] },   // auto tags (non-removable)
  placeholder:{ type: String, default: 'Add tag and press Enter' },
})
const emit = defineEmits(['update:modelValue'])

const input = ref('')
const local = ref([...props.modelValue])

watch(() => props.modelValue, v => { local.value = [...v] })

function normalize(t) {
  if (!t) return ''
  let v = String(t).trim()
  if (!v) return ''
  if (!v.startsWith('#')) v = '#' + v
  return v.replace(/\s+/g, '')                      // no spaces inside tags
}

function addFromInput() {
  const v = normalize(input.value)
  if (!v) return
  if (![...props.preset, ...local.value].includes(v)) {
    local.value.push(v)
    emit('update:modelValue', local.value)
  }
  input.value = ''
}

function removeTag(ix) {
  local.value.splice(ix, 1)
  emit('update:modelValue', local.value)
}

function onKeydown(e) {
  if (e.key === 'Enter' || e.key === ',' || e.key === 'Tab') {
    e.preventDefault(); addFromInput()
  } else if (e.key === 'Backspace' && !input.value && local.value.length) {
    // backspace to remove last
    local.value.pop(); emit('update:modelValue', local.value)
  }
}
</script>

<template>
  <div class="field-shell min-h-10 w-full px-2 py-1.5">
    <div class="flex flex-wrap items-center gap-1">
      <!-- preset (auto) tags – non-removable -->
      <span v-for="t in preset" :key="'p'+t"
            class="inline-flex items-center gap-1 rounded-full bg-[var(--border)]/30 text-app text-xs px-2 py-1">
        {{ t }}
      </span>

      <!-- user tags – removable -->
      <span v-for="(t, i) in local" :key="'u'+t"
            class="inline-flex items-center gap-1 rounded-full bg-[var(--secondary)] text-[var(--secondary-foreground)] text-xs px-2 py-1">
        {{ t }}
        <button class="ml-1 text-[var(--secondary-foreground)]/80 hover:text-[var(--secondary-foreground)]" @click="removeTag(i)" aria-label="Remove">✕</button>
      </span>

      <!-- input -->
      <input
        v-model="input"
        :placeholder="preset.length || local.length ? '' : placeholder"
        class="input-reset flex-1 min-w-[10ch] text-sm px-1 h-9"
        @keydown="onKeydown"
        @blur="addFromInput"
      />
    </div>
  </div>
</template>
