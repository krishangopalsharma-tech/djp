    <script setup>
    import { computed, onMounted, onBeforeUnmount, ref } from 'vue';
    import { useReportsStore } from '@/stores/reports.js';
    import { useTelegramStore } from '@/stores/telegram.js';
    import { Save, Trash2 } from 'lucide-vue-next';

    const reportsStore = useReportsStore();
    const telegramStore = useTelegramStore();

    const schedules = computed(() => reportsStore.schedules);
    const tgOptions = computed(() => telegramStore.list);
    const fileInputs = ref({});

    // For multi-select dropdown state
    const activeDropdownId = ref(null);

    onMounted(() => {
      reportsStore.fetchSchedules();
      if (telegramStore.list.length === 0) {
        telegramStore.fetchTelegramGroups();
      }
      // Close dropdown if user clicks outside
      document.addEventListener('click', closeDropdowns);
    });

    onBeforeUnmount(() => {
        document.removeEventListener('click', closeDropdowns);
    });

    function closeDropdowns(event) {
        if (event.target.closest('[data-dropdown-host]')) return;
        activeDropdownId.value = null;
    }

    const freqOptions = [
      { label: 'Daily', value: 'daily' },
      { label: 'Weekly', value: 'weekly' },
      { label: 'Monthly', value: 'monthly' },
    ];
    const dowOptions = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    const domOptions = Array.from({ length: 31 }, (_, i) => String(i + 1));

    function addReport() {
      const newReport = {
        name: 'New Report',
        frequency: 'daily',
        day_of_week: 'Mon',
        day_of_month: 1,
        time: '09:00',
        send_email: false,
        send_telegram: false,
        telegram_group_keys: [], // Use the correct key and initialize as an array
      };
      reportsStore.addSchedule(newReport);
    }

    function updateSchedule(schedule) {
      reportsStore.updateSchedule(schedule.id, schedule);
    }

    function removeSchedule(id) {
      if (confirm('Are you sure you want to delete this report schedule?')) {
        reportsStore.removeSchedule(id);
      }
    }

    function triggerFileInput(id) {
        fileInputs.value[id]?.click();
    }

    async function onTemplatePicked(id, event) {
      const file = event.target.files?.[0];
      if (file) {
        await reportsStore.uploadTemplate(id, file);
        if(event.target) event.target.value = '';
      }
    }

    function toggleTelegramGroup(schedule, groupKey) {
        const selectedKeys = new Set(schedule.telegram_group_keys || []);
        if (selectedKeys.has(groupKey)) {
            selectedKeys.delete(groupKey);
        } else {
            selectedKeys.add(groupKey);
        }
        schedule.telegram_group_keys = Array.from(selectedKeys);
    }

    function getSelectedGroupsText(keys) {
        if (!keys || keys.length === 0) return '-- Select --';
        if (keys.length === 1) {
            const group = tgOptions.value.find(g => g.key === keys[0]);
            return group ? group.name : keys[0];
        }
        return `${keys.length} groups selected`;
    }
    </script>

    <template>
      <div class="space-y-4">
        <div class="flex justify-between items-center">
            <p class="text-app/80 text-sm">
              Configure scheduled report emails and Telegram deliveries.
            </p>
            <button class="btn btn-primary" @click="addReport">+ Add Report</button>
        </div>
        
        <div v-if="reportsStore.loading && schedules.length === 0" class="text-center py-10 text-muted">
            Loading schedules...
        </div>
        <div v-else-if="reportsStore.error" class="text-center py-10 text-red-500">
            {{ reportsStore.error }}
        </div>
         <div v-else-if="schedules.length === 0" class="text-center py-10 text-muted">
            No report schedules found. Click "Add Report" to create one.
        </div>

        <div v-else class="overflow-x-auto">
          <table class="min-w-full w-full text-sm">
            <thead>
              <tr class="text-left border-b border-app/40">
                <th class="py-2.5 px-3 w-[220px]">Report Name</th>
                <th class="py-2.5 px-3 w-[260px]">Report Template (Excel)</th>
                <th class="py-2.5 px-3 w-[300px]">Schedule</th>
                <th class="py-2.5 px-3 w-[120px]">Emails</th>
                <th class="py-2.5 px-3 w-[220px]">Telegram Group</th>
                <th class="py-2.5 px-3 w-[140px] text-center">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="r in schedules" :key="r.id" class="border-b border-app/30">
                <!-- Report Name -->
                <td class="py-2 px-3 align-top">
                  <input
                    class="field h-9"
                    v-model="r.name"
                    placeholder="e.g., Daily Failure Summary"
                  />
                </td>

                <!-- Template -->
                <td class="py-2 px-3 align-top">
                  <div class="flex items-center gap-2">
                    <input
                      type="file"
                      accept=".xlsx,.xls"
                      class="hidden"
                      :ref="el => fileInputs[r.id] = el"
                      @change="e => onTemplatePicked(r.id, e)"
                    />
                    <button class="btn btn-sm" @click="triggerFileInput(r.id)">Choose…</button>
                    <span class="opacity-80 truncate max-w-[180px]" :title="r.template_name || 'No file chosen'">
                      {{ r.template_name || 'No file chosen' }}
                    </span>
                  </div>
                </td>

                <!-- Schedule -->
                <td class="py-2 px-3 align-top">
                  <div class="flex flex-wrap items-center gap-2">
                    <select class="field h-9" v-model="r.frequency">
                      <option v-for="o in freqOptions" :key="o.value" :value="o.value">{{ o.label }}</option>
                    </select>

                    <select v-if="r.frequency === 'weekly'" class="field h-9" v-model="r.day_of_week">
                      <option v-for="d in dowOptions" :key="d" :value="d">{{ d }}</option>
                    </select>

                    <select v-if="r.frequency === 'monthly'" class="field h-9 w-20" v-model.number="r.day_of_month">
                      <option v-for="d in domOptions" :key="d" :value="d">{{ d }}</option>
                    </select>

                    <input type="time" class="field h-9" v-model="r.time" />
                  </div>
                </td>

                <!-- Emails -->
                <td class="py-2 px-3 align-top">
                  <label class="inline-flex items-center gap-2">
                    <input type="checkbox" v-model="r.send_email" class="h-4 w-4" />
                    <span>Enable</span>
                  </label>
                </td>

                <!-- Telegram Multi-Select -->
                <td class="py-2 px-3 align-top">
                    <div class="flex flex-wrap items-center gap-2">
                        <label class="inline-flex items-center gap-2">
                            <input type="checkbox" v-model="r.send_telegram" class="h-4 w-4" />
                            <span>Enable</span>
                        </label>
                        <div class="relative w-full" data-dropdown-host>
                            <button
                                class="field h-9 w-full text-left flex items-center justify-between pr-2"
                                :disabled="!r.send_telegram"
                                @click.stop="activeDropdownId = activeDropdownId === r.id ? null : r.id"
                            >
                                <span class="truncate">{{ getSelectedGroupsText(r.telegram_group_keys) }}</span>
                                <span class="text-muted">▾</span>
                            </button>
                            <div v-if="activeDropdownId === r.id" class="absolute z-10 mt-1 w-full rounded-lg border bg-card text-app border-app shadow-lg max-h-48 overflow-auto">
                                <label v-for="g in tgOptions" :key="g.key" class="flex items-center gap-2 px-3 py-2 text-sm cursor-pointer hover:bg-gray-100">
                                    <input type="checkbox" :checked="(r.telegram_group_keys || []).includes(g.key)" @change="toggleTelegramGroup(r, g.key)" class="h-4 w-4" />
                                    <span>{{ g.name }}</span>
                                </label>
                            </div>
                        </div>
                    </div>
                </td>

                <!-- Actions -->
                <td class="py-2 px-3 align-top text-center">
                    <div class="flex items-center justify-center gap-2">
                        <button
                          class="h-9 w-9 flex items-center justify-center rounded-lg bg-[var(--button-primary)] text-[var(--seasalt)] hover:bg-[var(--button-hover)] transition"
                          @click="updateSchedule(r)"
                          :disabled="reportsStore.loading"
                          title="Save Changes"
                        >
                            <Save class="w-5 h-5" />
                        </button>
                        <button
                          class="inline-flex items-center justify-center h-9 w-9 rounded-md text-app border border-app hover:bg-gray-100 transition"
                          @click="removeSchedule(r.id)"
                          title="Delete Schedule"
                        >
                            <Trash2 class="w-5 h-5" />
                        </button>
                    </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>
    

