<script setup>
import { ref } from 'vue'
import { getCurrentPreset, applyPreset, clearPreset } from '@/lib/presets'

const text = ref(JSON.stringify(getCurrentPreset(), null, 2))

const samples = [
  {
    name: 'Indigo • light • default sizes',
    preset: {
      theme: 'light',
      brand: 'indigo',
      vars: { scaleText: '1', scaleControl: '1' }
    }
  },
  {
    name: 'Rail • light • larger text',
    preset: {
      theme: 'light',
      brand: 'rail',
      vars: { scaleText: '1.12', scaleControl: '1' }
    }
  },
  {
    name: 'Emerald • dark • compact controls',
    preset: {
      theme: 'dark',
      brand: 'emerald',
      vars: { scaleText: '1', scaleControl: '0.9' }
    }
  }
]

function exportCurrent() {
  text.value = JSON.stringify(getCurrentPreset(), null, 2)
}

function applyFromTextarea() {
  try {
    const parsed = JSON.parse(text.value)
    applyPreset(parsed)
  } catch (e) {
    alert('Invalid JSON. Please check and try again.')
  }
}

function applySample(p) {
  text.value = JSON.stringify(p, null, 2)
  applyPreset(p)
}

function resetToDefaults() {
  clearPreset()
  alert('Preset cleared. Defaults from CSS will apply on next paint.')
}
</script>

<template>
  <div class="card max-w-3xl mx-auto my-token-6">
    <div class="card-body stack-md">
      <div class="text-h3">Preset Manager</div>

      <div class="row-md">
        <PButton label="Export Current" icon="pi pi-download" @click="exportCurrent" />
        <PButton label="Apply JSON" icon="pi pi-upload" @click="applyFromTextarea" />
        <PButton label="Clear Preset" severity="secondary" icon="pi pi-trash" @click="resetToDefaults" />
      </div>

      <label class="text-muted text-token-sm">Preset JSON</label>
      <textarea
        class="input"
        style="min-height: 10rem; font-family: var(--font-mono);"
        v-model="text"
      ></textarea>

      <div class="text-h3 mt-token-4">Samples</div>
      <div class="row-md">
        <button
          v-for="s in samples"
          :key="s.name"
          class="btn btn-outline"
          @click="applySample(s.preset)"
        >
          {{ s.name }}
        </button>
      </div>
    </div>
  </div>
</template>
