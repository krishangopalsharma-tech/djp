<script setup>
import InputText from '@/components/form/InputText.vue'
import SelectBox from '@/components/form/SelectBox.vue'
import { reactive } from 'vue'
import { useAppStore } from '@/stores/app'
import { useUIStore } from '@/stores/ui'
import ThemeSwitcher from '@/components/ThemeSwitcher.vue'
//import PrimeButtonsDemo from '@/components/PrimeButtonsDemo.vue'

const app = useAppStore()
const ui = useUIStore()

// demo form state (later we’ll load/save via API)
const form = reactive({
  appName: app.appName,
  realtimeIntervalSec: '30',
  failIdSeparator: '-',
})

const intervalOptions = [
  { label: '10 sec', value: '10' },
  { label: '20 sec', value: '20' },
  { label: '30 sec', value: '30' },
  { label: '60 sec', value: '60' },
]

function save() {
  // for now, just update the store for app name and toast
  app.setAppName(form.appName || 'Railway Failure System')
  ui.pushToast({ type: 'success', title: 'Saved', message: 'Settings updated (local only).' })
}
</script>

<template>
  <div class="space-y-6 max-w-3xl">
    <div>
      <h2 class="text-2xl font-semibold">Settings</h2>
      <p class="text-sm text-gray-500">UI-only for now. We’ll wire to Django later.</p>
    </div>

    <div class="rounded-2xl border bg-white p-4 space-y-6">
      <section class="space-y-3">
        <h3 class="text-sm font-semibold text-gray-700">General</h3>
        <InputText label="Application Name" v-model="form.appName" placeholder="Railway Failure System" />
        <SelectBox label="Realtime Update Interval" v-model="form.realtimeIntervalSec" :options="intervalOptions" />
      </section>

      <section class="space-y-3">
        <h3 class="text-sm font-semibold text-gray-700">Failure ID</h3>
        <InputText label="Separator" v-model="form.failIdSeparator" placeholder="-" />
      </section>

      <div class="flex gap-2">
        <button @click="save" class="h-10 px-4 rounded-lg bg-gray-900 text-white text-sm">Save</button>
        <button
          @click="Object.assign(form,{ appName:'Railway Failure System', realtimeIntervalSec:'30', failIdSeparator:'-' })"
          class="h-10 px-4 rounded-lg border bg-white text-sm"
        >
          Reset
        </button>
      </div>
    </div>
    <!-- <div class="rounded-2xl border bg-white p-4 mt-6">
        <h3 class="text-sm font-semibold text-gray-700 mb-3">PrimeVue Buttons Preview</h3>
        <PrimeButtonsDemo />
    </div> -->
  </div>
  <ThemeSwitcher />
  <BrandSwitcher />
</template>