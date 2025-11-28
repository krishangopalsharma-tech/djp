<script setup>
import { computed, watch } from 'vue'
import InputText from '@/components/form/InputText.vue'
import DateTime from '@/components/form/DateTime.vue'
import SearchSelect from '@/components/form/SearchSelect.vue'
import TagsInput from '@/components/form/TagsInput.vue'
import FailureAttachment from '@/components/FailureAttachment.vue'

const props = defineProps({
  modelValue: { type: Object, required: true },
  options: { type: Object, required: true },
  errors: { type: Object, default: () => ({}) },
  isEditMode: { type: Boolean, default: false },
})

const emit = defineEmits(['update:modelValue'])

const form = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const circuitOptionsForSelect = computed(() => {
  return (props.options.circuits || []).map(c => ({
    label: c.circuit_id,
    value: c.id
  }));
});

const selectedCircuitObject = computed(() => {
  if (!form.value.circuit || !props.options.circuits) return null;
  return props.options.circuits.find(c => c.id === form.value.circuit);
});

const selectedCircuitDescription = computed(() => {
  const circuit = selectedCircuitObject.value;
  if (!circuit) return '';

  let description = circuit.name || '';
  if (circuit.related_equipment) {
    description += ` (Equipment: ${circuit.related_equipment})`;
  }
  return description;
});

const selectedCircuitSeverity = computed(() => {
  return selectedCircuitObject.value ? selectedCircuitObject.value.severity : '';
});

const autoTags = computed(() => {
  const t = [];
  if (form.value.depot) { const depot = props.options.depots.find(d => d.value === form.value.depot); if (depot) t.push(`#${depot.label}`) }
  if (selectedCircuitObject.value) { t.push(`#${selectedCircuitObject.value.circuit_id.replace(/\s+/g, '_')}`) }
  
  // This is the line to change
  if (form.value.station) { const station = props.options.stations.find(s => s.id === form.value.station); if (station) t.push(`#${station.code}`) } 
  
  if (form.value.section) { const section = props.options.sections.find(s => s.id === form.value.section); if (section) t.push(`#${section.name}`) }
  if (form.value.sub_section) { const subSection = props.options.subSections.find(s => s.id === form.value.sub_section); if (subSection) t.push(`#${subSection.name}`) }
  return t
});

const stationOptions = computed(() => {
  if (!form.value.depot) return [];
  return props.options.stations
    .filter(s => s.depot === form.value.depot)
    .map(s => ({ label: s.code, value: s.id })); // <-- Change s.name to s.code
});
const sectionOptions = computed(() => {
    if (!form.value.depot) return [];
    return props.options.sections
        .filter(s => s.depot === form.value.depot)
        .map(s => ({ label: s.name, value: s.id }));
});

const subSectionOptions = computed(() => {
    if (!form.value.section) return [];
    return props.options.subSections
        .filter(s => s.section === form.value.section)
        .map(s => ({ label: s.name, value: s.id }));
});

watch(() => form.value.depot, () => { form.value.station = null; form.value.section = null; form.value.sub_section = null; });
watch(() => form.value.section, () => { form.value.sub_section = null; });
</script>

<template>
  <div class="grid gap-4 sm:grid-cols-2">
    <div class="sm:col-span-2 grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
      <div>
        <span class="text-sm text-app">Entry Type</span>
        <div class="flex items-center gap-4 pt-2">
          <label class="flex items-center gap-2">
            <input type="radio" v-model="form.entry_type" value="item" class="radio" />
            <span>Failure</span>
          </label>
          <label class="flex items-center gap-2">
            <input type="radio" v-model="form.entry_type" value="message" class="radio" />
            <span>General Message</span>
          </label>
        </div>
      </div>
      <div>
        <label class="block space-y-1">
          <span class="text-sm text-app">Circuit</span>
          <SearchSelect v-model="form.circuit" :options="circuitOptionsForSelect" placeholder="Select circuit..." />
          
          <p v-if="selectedCircuitObject" class="text-xs text-blue-600 mt-1 min-h-[1rem]">
            {{ selectedCircuitDescription || '(No description provided for this circuit)' }}
          </p>
          <p v-if="errors.circuit" class="text-xs text-red-600">{{ errors.circuit }}</p>
        </label>
      </div>
      <div>
        <label class="block space-y-1">
          <span class="text-sm text-app">Circuit Severity</span>
          <input readonly :value="selectedCircuitSeverity" class="field bg-app-hover" />
        </label>
      </div>
    </div>
    <div class="sm:col-span-2">
      <label class="block space-y-1">
        <span class="text-sm text-app">Circuit Tags</span>
        <TagsInput v-model="form.userTags" :preset="autoTags" placeholder="Add tag and press Enter" />
        <p class="text-xs text-muted">Auto from selections; you can add/remove your own.</p>
      </label>
    </div>
    <div class="sm:col-span-2 grid gap-4 sm:grid-cols-2 md:grid-cols-4">
      <div>
        <label class="block space-y-1">
          <span class="text-sm text-app">Depot</span>
          <SearchSelect v-model="form.depot" :options="options.depots" placeholder="Select depot..." />
        </label>
      </div>
      <div>
        <label class="block space-y-1">
          <span class="text-sm text-app">Station</span>
          <SearchSelect v-model="form.station" :options="stationOptions" placeholder="Select station..." />
        </label>
      </div>
      <div>
        <label class="block space-y-1">
          <span class="text-sm text-app">Section</span>
          <SearchSelect v-model="form.section" :options="sectionOptions" placeholder="Select section..." />
        </label>
      </div>
      <div>
        <label class="block space-y-1">
          <span class="text-sm text-app">Sub Section</span>
          <SearchSelect v-model="form.sub_section" :options="subSectionOptions" placeholder="Select sub section..." />
        </label>
      </div>
    </div>
    <div class="sm:col-span-2 grid gap-4 grid-cols-1 md:grid-cols-3">
      <DateTime label="Reported At" v-model="form.reported_at" />
      <div>
        <label class="block space-y-1">
          <span class="text-sm text-app">Assigned To</span>
          <SearchSelect v-model="form.assigned_to" :options="options.supervisors" placeholder="Select assignee..." />
        </label>
      </div>
      <div>
        <label class="block space-y-1">
          <span class="text-sm text-app">Current Status</span>
          <SearchSelect
            v-model="form.current_status"
            :options="options.statuses"
            placeholder="Select status..."
            :disabled="form.entry_type === 'message'"/>
        </label>
      </div>
    </div>
    <div class="sm:col-span-2">
      <textarea v-model="form.remark_fail" rows="2" class="field-textarea" placeholder="Notes..."></textarea>
    </div>
    <template v-if="form.current_status === 'Resolved'">
      <DateTime label="Resolve At" v-model="form.resolved_at" />
      <InputText label="Duration (minutes)" v-model="form.duration_minutes" />
      <textarea v-model="form.remark_right" rows="2" class="sm:col-span-2 field-textarea" placeholder="Notes on resolution..."></textarea>
    </template>
    
    <FailureAttachment v-if="isEditMode && form.id" :failure-id="form.id" />
  </div>
</template>