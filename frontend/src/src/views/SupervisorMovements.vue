<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useSupervisorMovementsStore } from '@/stores/supervisorMovements';
import { useInfrastructureStore } from '@/stores/infrastructure';
import { Save, Send } from 'lucide-vue-next';

// --- Store Setup ---
const movementsStore = useSupervisorMovementsStore();
const infrastructureStore = useInfrastructureStore();

// --- State ---
const today = new Date().toISOString().slice(0, 10);
const selectedDate = ref(today);
const supervisorData = computed(() => movementsStore.dailyMovements);
const supervisorOptions = computed(() => infrastructureStore.supervisors.map(s => ({ value: s.id, label: s.name })));

const editableData = ref([]);
const dirtyRows = ref(new Set());
const sortKey = ref('name');
const sortDir = ref('asc');

// --- Data Fetching ---
onMounted(() => {
  movementsStore.fetchMovementsByDate(selectedDate.value);
  infrastructureStore.fetchSupervisors();
});

// --- Sorting Logic ---
const sortedData = computed(() => {
    const data = [...editableData.value];
    if (!sortKey.value) return data;
    return data.sort((a, b) => {
        let valA, valB;
        if (['location', 'purpose'].includes(sortKey.value)) {
            valA = a.movement?.[sortKey.value] || '';
            valB = b.movement?.[sortKey.value] || '';
        } else {
            valA = a[sortKey.value] || '';
            valB = b[sortKey.value] || '';
        }
        
        const modifier = sortDir.value === 'asc' ? 1 : -1;
        if (valA < valB) return -1 * modifier;
        if (valA > valB) return 1 * modifier;
        return 0;
    });
});

function toggleSort(key) {
    if (sortKey.value === key) {
        sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc';
    } else {
        sortKey.value = key;
        sortDir.value = 'asc';
    }
}


// --- Main Logic ---
watch(selectedDate, (newDate) => {
  if (newDate) {
    movementsStore.fetchMovementsByDate(newDate);
    dirtyRows.value.clear();
  }
});

watch(supervisorData, (newData) => {
  editableData.value = JSON.parse(JSON.stringify(newData || [])).map(supervisor => {
    if (!supervisor.movement) {
      supervisor.movement = {
        location: '', on_leave: false, leave_from: null,
        leave_to: null, look_after: null, purpose: '',
      };
    }
    return supervisor;
  });
}, { deep: true, immediate: true });


function markAsDirty(supervisorId) {
  dirtyRows.value.add(supervisorId);
}

async function handleSaveAll() {
  const promises = [];
  for (const supervisorId of dirtyRows.value) {
    const supervisorRow = editableData.value.find(s => s.id === supervisorId);
    if (supervisorRow && supervisorRow.movement) {
      const payload = {
        id: supervisorRow.movement.id,
        date: selectedDate.value,
        supervisor: supervisorRow.id,
        location: supervisorRow.movement.location || '',
        on_leave: supervisorRow.movement.on_leave || false,
        leave_from: supervisorRow.movement.leave_from || null,
        leave_to: supervisorRow.movement.leave_to || null,
        look_after: supervisorRow.movement.look_after || null,
        purpose: supervisorRow.movement.purpose || '',
      };
      if (!payload.on_leave) {
        payload.leave_from = null;
        payload.leave_to = null;
        payload.look_after = null;
      }
      promises.push(movementsStore.saveMovement(payload));
    }
  }
  await Promise.all(promises);
  dirtyRows.value.clear();
}

async function handleSendReport() {
    movementsStore.sendMovementReport(selectedDate.value);
}
</script>

<template>
  <div class="space-y-4">
    <div class="flex flex-wrap items-center justify-between gap-4">
        <h1 class="text-2xl font-bold">Supervisor Movements</h1>
        <div class="flex flex-wrap items-center gap-4">
            <div class="flex items-center gap-2">
                <label for="movement-date" class="text-sm font-medium">Date:</label>
                <input type="date" id="movement-date" v-model="selectedDate" class="field h-10 w-48" />
            </div>
            <div class="flex items-center gap-2">
                 <button 
                    @click="handleSaveAll" 
                    class="h-9 w-9 flex items-center justify-center rounded-lg bg-[var(--button-primary)] text-[var(--seasalt)] hover:bg-[var(--button-hover)] transition" 
                    :disabled="dirtyRows.size === 0 || movementsStore.loading" 
                    title="Save All Changes">
                    <Save class="w-5 h-5" />
                </button>
                <button 
                    @click="handleSendReport" 
                    class="h-9 w-9 flex items-center justify-center rounded-lg bg-[var(--french-gray)] text-[var(--eerie-black)] hover:bg-[var(--french-gray-lighter)] transition"
                    :disabled="movementsStore.loading"
                    title="Send Report">
                    <Send class="w-5 h-5" />
                </button>
            </div>
        </div>
    </div>

    <div v-if="movementsStore.loading" class="text-center py-10 text-muted">Loading...</div>
    <div v-else-if="movementsStore.error" class="text-center py-10 text-red-500">{{ movementsStore.error }}</div>

    <div v-else class="rounded-2xl border-app bg-card text-app overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <colgroup>
            <col class="w-[15%]" />
            <col class="w-[15%]" />
            <col class="w-[15%]" />
            <col class="w-[10%]" />
            <col class="w-[10%]" />
            <col class="w-[20%]" />
            <col class="w-[15%]" />
          </colgroup>
          <thead>
            <tr class="text-left border-b border-app/40">
              <th @click="toggleSort('depot_name')" class="py-2.5 px-3 cursor-pointer select-none">Depot <span v-if="sortKey === 'depot_name'">{{ sortDir === 'asc' ? '▲' : '▼' }}</span></th>
              <th @click="toggleSort('name')" class="py-2.5 px-3 cursor-pointer select-none">Name <span v-if="sortKey === 'name'">{{ sortDir === 'asc' ? '▲' : '▼' }}</span></th>
              <th @click="toggleSort('designation')" class="py-2.5 px-3 cursor-pointer select-none">Designation <span v-if="sortKey === 'designation'">{{ sortDir === 'asc' ? '▲' : '▼' }}</span></th>
              <th @click="toggleSort('location')" class="py-2.5 px-3 cursor-pointer select-none">Location <span v-if="sortKey === 'location'">{{ sortDir === 'asc' ? '▲' : '▼' }}</span></th>
              <th class="py-2.5 px-3">On Leave</th>
              <th class="py-2.5 px-3">Leave Details</th>
              <th class="py-2.5 px-3">Purpose</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in sortedData" :key="row.id" class="border-t border-app/30">
              <td class="py-2 px-3 align-top font-semibold">{{ row.depot_name || 'N/A' }}</td>
              <td class="py-2 px-3 align-top">{{ row.name }}</td>
              <td class="py-2 px-3 align-top text-muted">{{ row.designation }}</td>
              <td class="py-2 px-3 align-top">
                <input v-model="row.movement.location" class="field h-9" placeholder="Location" @change="markAsDirty(row.id)" />
              </td>
              <td class="py-2 px-3 align-top">
                <label class="inline-flex items-center gap-2 mt-2">
                  <input type="checkbox" v-model="row.movement.on_leave" class="h-4 w-4" @change="markAsDirty(row.id)" />
                </label>
              </td>
              <td class="py-2 px-3 align-top">
                <div v-if="row.movement.on_leave" class="space-y-2">
                  <div class="grid grid-cols-2 gap-2">
                    <input type="date" v-model="row.movement.leave_from" class="field h-9" title="Leave From" @change="markAsDirty(row.id)" />
                    <input type="date" v-model="row.movement.leave_to" class="field h-9" title="Leave To" @change="markAsDirty(row.id)" />
                  </div>
                  <select v-model="row.movement.look_after" class="field h-9" title="Looked After By" @change="markAsDirty(row.id)">
                    <option :value="null">-- Looked After By --</option>
                    <option v-for="opt in supervisorOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
                  </select>
                </div>
              </td>
              <td class="py-2 px-3 align-top">
                 <input type="text" v-model="row.movement.purpose" class="field h-9" placeholder="Purpose / Remarks..." @change="markAsDirty(row.id)" maxlength="100" />
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
