<script setup>
import { ref, reactive, onMounted, computed, watch, nextTick } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useFailureStore } from '@/stores/failures';
import { useInfrastructureStore } from '@/stores/infrastructure';
import { useUIStore } from '@/stores/ui';
import FailureForm from '@/components/FailureForm.vue';
import Spinner from '@/components/ui/Spinner.vue';

// Helper to format dates for the datetime-local input
function toLocalISOString(date) {
  if (!date) return '';
  const d = new Date(date);
  if (isNaN(d.getTime())) return '';
  const offset = d.getTimezoneOffset();
  const localDate = new Date(d.getTime() - (offset * 60 * 1000));
  return localDate.toISOString().slice(0, 16);
}

const route = useRoute();
const router = useRouter();
const failureStore = useFailureStore();
const infrastructureStore = useInfrastructureStore();
const ui = useUIStore();

const failureId = route.params.id;
const isLoading = ref(true);
const form = reactive({ userTags: [] });
const errors = reactive({});

const options = computed(() => ({
  depots: infrastructureStore.depots.map(d => ({ label: d.code || d.name, value: d.id })),
  circuits: infrastructureStore.circuits,
  stations: infrastructureStore.stations,
  sections: infrastructureStore.sections,
  subSections: infrastructureStore.subSections,
  supervisors: infrastructureStore.supervisors.map(s => ({ label: s.name, value: s.id })),
  statuses: [ { label: 'Active', value: 'Active' }, { label: 'In Progress', value: 'In Progress' }, { label: 'Resolved', value: 'Resolved' }, { label: 'On Hold', value: 'On Hold' }, { label: 'Information', value: 'Information' }],
}));

onMounted(async () => {
  try {
    await Promise.all([
      infrastructureStore.fetchDepots(),
      infrastructureStore.fetchCircuits(),
      infrastructureStore.fetchStations(),
      infrastructureStore.fetchSections(),
      infrastructureStore.fetchSubSections(),
      infrastructureStore.fetchSupervisors(),
    ]);

    await failureStore.fetchFailure(failureId);
    const failureData = failureStore.currentFailure;
    
    if (failureData) {
      Object.assign(form, {
        ...failureData,
        depot: failureData.station?.depot || failureData.section?.depot || null,
        circuit: failureData.circuit?.id || null,
        station: failureData.station?.id || null,
        section: failureData.section?.id || null,
        sub_section: failureData.sub_section?.id || null,
        assigned_to: failureData.assigned_to?.id || null,
        reported_at: toLocalISOString(failureData.reported_at),
        resolved_at: toLocalISOString(failureData.resolved_at),
        userTags: [],
      });
      // Use nextTick to ensure dependent dropdowns populate correctly
      await nextTick();
    }
  } catch (error) {
    console.error("Failed to load data for editing:", error);
    ui.pushToast({ type: 'error', title: 'Load Failed', message: 'Could not load failure data for editing.' });
  } finally {
    isLoading.value = false;
  }
});

// Watchers for auto-populating date and duration
watch(() => form.current_status, (status) => {
  if (status === 'Resolved' && !form.resolved_at) {
    form.resolved_at = toLocalISOString(new Date());
  }
});

watch(() => [form.reported_at, form.resolved_at], ([reported, resolved]) => {
  if (reported && resolved) {
    const ms = new Date(resolved) - new Date(reported);
    form.duration_minutes = isNaN(ms) || ms < 0 ? '' : Math.round(ms / 60000);
  } else {
    form.duration_minutes = '';
  }
});

function validate() {
  errors.circuit = form.circuit ? '' : 'Required';
  return !errors.circuit;
}

async function submit() {
  if (!validate()) {
    ui.pushToast({ type: 'error', title: 'Missing fields', message: 'Circuit is required.' });
    return;
  }
  
  const payload = { ...form };
  delete payload.userTags;
  payload.resolved_at = payload.resolved_at || null;

  const savedFailure = await failureStore.updateFailure(failureId, payload);
  if (savedFailure) {
    ui.pushToast({ type: 'success', title: 'Success', message: 'Logbook entry updated.' });
    if (savedFailure.current_status !== 'Draft' && savedFailure.current_status !== 'Information') {
      await failureStore.sendFailureNotification(savedFailure.id, ['alert']);
      ui.pushToast({ type: 'info', title: 'Notification', message: 'Update notification sent.' });
    }
    // Go to Logbook to see the change, not the new entry page
    router.push('/logbook');
  }
}

function cancel() {
    router.push('/logbook');
}
</script>

<template>
  <div class="space-y-4 max-w-4xl mx-auto">
    <div class="text-center">
      <h2 class="text-2xl font-semibold leading-tight">
        Edit Failure Log #{{ failureStore.currentFailure?.fail_id || failureId }}
      </h2>
    </div>
    <div class="card min-h-[400px]">
      <div v-if="isLoading" class="flex items-center justify-center p-10">
        <Spinner :size="40" />
      </div>
      <div v-else-if="!failureStore.currentFailure" class="text-center p-10 text-muted">
        Could not load failure record.
      </div>
      <div v-else>
        <FailureForm v-model="form" :options="options" :errors="errors" :is-edit-mode="true" />
        <div class="sm:col-span-2 flex items-center justify-end gap-3 pt-4 mt-4 border-t border-app">
            <button type="button" class="btn btn-outline" @click="cancel">Cancel</button>
            <button type="button" class="btn btn-primary" @click="submit">Save Changes & Notify</button>
        </div>
      </div>
    </div>
  </div>
</template>
