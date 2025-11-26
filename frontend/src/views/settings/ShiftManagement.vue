<script setup>
import { onMounted } from 'vue'
import { useShiftStore } from '@/stores/shifts'
import { useUIStore } from '@/stores/ui'
import Spinner from '@/components/ui/Spinner.vue'

const shiftStore = useShiftStore()
const ui = useUIStore()

onMounted(() => {
  shiftStore.fetchShifts()
})

async function saveShift(shift) {
  const success = await shiftStore.updateShift(shift.id, {
    start_time: shift.start_time,
    end_time: shift.end_time,
  })
  if (success) {
    ui.pushToast({ type: 'success', title: 'Saved', message: `${shift.name} shift updated.` })
  } else {
    ui.pushToast({ type: 'error', title: 'Error', message: shiftStore.error })
  }
}
</script>

<template>
  <div class="space-y-6 max-w-3xl">
    <div>
      <p class="text-sm text-gray-500">Configure the start and end times for each shift. These settings will affect the Logbook filters.</p>
    </div>

    <div v-if="shiftStore.loading && shiftStore.shifts.length === 0" class="text-center p-6">
      <Spinner />
    </div>
    <div v-else-if="shiftStore.error" class="card p-6 text-center text-red-500">
      {{ shiftStore.error }}
    </div>

    <div v-else class="grid gap-6">
      <div v-for="shift in shiftStore.shifts" :key="shift.id" class="card p-4 flex items-center justify-between">
        <div>
          <h3 class="font-semibold text-lg">{{ shift.name }}</h3>
          <p class="text-sm text-muted">Configure timing for {{ shift.name }} shift</p>
        </div>
        <div class="flex items-center gap-4">
          <div class="flex flex-col">
            <label class="text-xs font-medium text-muted mb-1">Start Time</label>
            <input type="time" v-model="shift.start_time" class="input input-bordered input-sm" />
          </div>
          <div class="flex flex-col">
            <label class="text-xs font-medium text-muted mb-1">End Time</label>
            <input type="time" v-model="shift.end_time" class="input input-bordered input-sm" />
          </div>
          <button @click="saveShift(shift)" class="btn btn-primary btn-sm self-end">Save</button>
        </div>
      </div>
    </div>
  </div>
</template>
