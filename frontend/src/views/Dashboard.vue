<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue';
import { useRouter } from 'vue-router';
import { useDashboardStore } from '@/stores/dashboard';
import { useFailureStore } from '@/stores/failures';
import { useRecentFailuresStore } from '@/stores/recentFailures';
// --- START OF FIX ---
import { useInfrastructureStore } from '@/stores/infrastructure';
// --- END OF FIX ---
import { useDebounce } from '@/composables/useDebounce';

import SplitPane from '@/components/SplitPane.vue';
import KpiCard from '@/components/KpiCard.vue';
import BarChart from '@/components/BarChart.vue';
import LineChart from '@/components/LineChart.vue';
import DashboardFilterBar from '@/components/DashboardFilterBar.vue';
import RecentFailures from '@/components/RecentFailures.vue';
import SectionPicker from '@/components/SectionPicker.vue';
import FailureDetailsDrawer from '@/components/FailureDetailsDrawer.vue';
import NotificationModal from '@/components/NotificationModal.vue';
import { borderColor } from '@/lib/statusColors';
import { withAlpha } from '@/lib/theme';

// --- Store and Router setup ---
const dashboardStore = useDashboardStore();
const failureStore = useFailureStore();
const recentFailuresStore = useRecentFailuresStore();
// --- START OF FIX ---
const infrastructureStore = useInfrastructureStore();
// --- END OF FIX ---
const router = useRouter();

// --- UI Controls & State ---
const topNMode = ref(true);
const topN = ref(10);
const autoRefresh = ref(false);
const intervalMs = ref(30000);
const chartsSplit = ref(60);
const cumulativeMode = ref(true);
const lastUpdated = ref(Date.now());
let refreshTimer = null;
const drawerOpen = ref(false);
const activeItem = ref(null);
const filters = ref({
  range: '30d',
  status: ['Active', 'In Progress', 'Resolved', 'On Hold'],
  sections: [],
});
const split = ref(Number(localStorage.getItem('dashSplit') || 66));
const isNotifyModalOpen = ref(false);
const failureToNotify = ref(null);

// --- Helper Functions ---
const nf = new Intl.NumberFormat('en-IN');
const formatInt = n => (typeof n === 'number' ? nf.format(n) : n);
function timeAgo(ts) {
  const ms = new Date(ts).getTime();
  if (isNaN(ms)) return '—';
  const diff = Date.now() - ms;
  const m = Math.floor(diff / 60000);
  if (m < 1) return 'just now';
  if (m < 60) return `${m}m ago`;
  const h = Math.floor(m / 60);
  if (h < 24) return `${h}h ago`;
  const d = Math.floor(h / 24);
  return `${d}d ago`;
}

const fetchData = useDebounce(() => {
    // We need to map section names to IDs for the API
    const sectionNameToIdMap = new Map(infrastructureStore.sections.map(s => [s.name, s.id]));
    const sectionIds = filters.value.sections.map(name => sectionNameToIdMap.get(name)).filter(id => id);

    dashboardStore.fetchDashboardData({ ...filters.value, sections: sectionIds });
    recentFailuresStore.fetchRecentFailures();
    lastUpdated.value = Date.now();
}, 300);

onMounted(() => {
  // Use infrastructureStore to fetch sections
  infrastructureStore.fetchSections().then(() => {
    fetchData(); // Initial data load after sections are available
  });
  // No need to fetch all failures here anymore, recentFailuresStore handles its own
});

onBeforeUnmount(() => stopTimer());

watch(filters, fetchData, { deep: true });

const isLoading = computed(() => dashboardStore.loading || recentFailuresStore.loading);

const allSectionsMaster = computed(() =>
  (infrastructureStore.sections || []).map(s => s.name).sort()
);

const kpis = computed(() => {
  const data = dashboardStore.data?.kpis;
  return [
    { label: 'Active Failures', value: formatInt(data?.active_failures), sublabel: 'in range' },
    { label: 'Resolved', value: formatInt(data?.resolved_in_range), sublabel: 'in range' },
    { label: 'Avg Resolution Time', value: data?.avg_resolution_time || '—', sublabel: 'for range' },
    { label: 'Critical Alerts', value: formatInt(data?.critical_alerts), sublabel: 'filtered' },
  ];
});

const hasBarData = computed(() => {
  const ds = statusBySection.value?.datasets || [];
  return ds.some(d => Array.isArray(d.data) && d.data.some(v => Number(v) > 0));
});

const hasLineData = computed(() => {
  const ds = resolvedOverTime.value?.datasets || [];
  return ds.some(d => Array.isArray(d.data) && d.data.some(v => Number(v) > 0));
});

const rangeLabel = computed(() =>
  filters.value.range === 'today' ? 'today' :
  filters.value.range === '7d' ? 'last 7 days' : 'last 30 days'
);

const statusBySection = computed(() => {
  const chartData = dashboardStore.data?.charts?.status_by_section || [];
  const topData = topNMode.value ? chartData.slice(0, topN.value) : chartData;
  const labels = topData.map(item => item.section__name);
  return {
    labels,
    datasets: [
      { label: 'Active', data: topData.map(item => item.active), borderRadius: 6 },
      { label: 'Resolved', data: topData.map(item => item.resolved), borderRadius: 6 },
    ],
  };
});

const resolvedOverTime = computed(() => {
  const chartData = dashboardStore.data?.charts?.resolved_over_time || [];
  const labels = chartData.map(item => new Date(item.date).toLocaleDateString([], { month: 'short', day: '2-digit' }));
  const data = chartData.map(item => item.count);

  const series = cumulativeMode.value
    ? data.map((sum => value => sum += value)(0))
    : data;

  const primary = borderColor('Resolved');
  return {
    labels,
    datasets: [{
      label: cumulativeMode.value ? 'Resolved (cumulative)' : 'Resolved (per interval)',
      data: series,
      tension: 0.3,
      fill: true,
      borderColor: primary,
      backgroundColor: withAlpha(primary, 0.2),
    }],
  };
});

const recent = computed(() => recentFailuresStore.items);

// --- Other methods that can remain ---
function openDetails(item) { activeItem.value = item; drawerOpen.value = true; }
function handleEdit(id) { router.push(`/failures/edit/${id}`); }
function openNotifyModal(row) { failureToNotify.value = row; isNotifyModalOpen.value = true; }
function stopTimer() { if (refreshTimer) { clearInterval(refreshTimer); refreshTimer = null; } }
function startTimer() {
    stopTimer();
    if (autoRefresh.value) {
        refreshTimer = setInterval(fetchData, Number(intervalMs.value) || 30000);
    }
}
watch([autoRefresh, intervalMs], startTimer);
watch(split, v => localStorage.setItem('dashSplit', String(v)));
</script>

<template>
  <div class="space-y-6">
    <div class="mt-3 mb-3 flex flex-wrap items-center justify-between gap-3">
      <div class="flex flex-wrap items-center gap-2">
          <DashboardFilterBar v-model="filters" :show-statuses="false" />
          <SectionPicker v-model="filters.sections" :sections="allSectionsMaster" :max-inline="1" placeholder="Search sections…" />
      </div>
      <div class="flex flex-wrap items-center gap-2 shrink-0">
        <select v-model="intervalMs" class="h-10 rounded-lg border-app bg-card text-app px-2 text-sm" title="Auto-refresh interval">
          <option :value="10000">10s</option>
          <option :value="30000">30s</option>
          <option :value="60000">1m</option>
          <option :value="300000">5m</option>
        </select>
        <label class="h-10 inline-flex items-center gap-2 text-sm text-app px-2">
          <input type="checkbox" v-model="autoRefresh" class="h-4 w-4 rounded border-app align-middle" />
          <span class="align-middle">Auto-refresh</span>
        </label>
        <button @click="fetchData" :disabled="isLoading" class="h-10 inline-flex items-center gap-2 rounded-lg border-app bg-card text-app px-3 text-sm shadow-card hover:shadow-popover hover:bg-[var(--seasalt-lighter)] transition disabled:opacity-60 disabled:cursor-not-allowed" title="Refresh now">
          <svg viewBox="0 0 24 24" class="w-4 h-4 shrink-0 align-middle"><path fill="currentColor" d="M12 6V3l-4 4l4 4V8c2.76 0 5 2.24 5 5a5 5 0 0 1-8.66 3.54a1 1 0 1 0-1.41 1.41A7 7 0 0 0 19 13c0-3.87-3.13-7-7-7Z"/></svg>
          <span class="leading-none">Refresh</span>
        </button>
      </div>
    </div>
      
    <DashboardFilterBar v-model="filters" :show-ranges="false" />

    <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KpiCard v-for="(kpi, index) in kpis" :key="index" :label="kpi.label" :value="kpi.value" :sublabel="kpi.sublabel" />
    </div>
 
    <SplitPane v-model="split">
      <template #left>
        <SplitPane v-model="chartsSplit" :min-left="35" :max-left="80" class="widget-eq">
          <template #left>
            <div class="rounded-2xl border-app bg-card text-app p-4 relative overflow-hidden shadow-card mr-2 widget-eq-body">
              <div class="mb-2 text-sm font-semibold text-app flex items-center justify-between">
                <span>Status by Section</span>
                <div class="flex items-center gap-2 text-xs font-normal">
                  <label class="inline-flex items-center gap-1">
                    <input type="checkbox" v-model="topNMode" class="h-3.5 w-3.5 rounded border-app" />
                    Top-N
                  </label>
                  <select v-model="topN" :disabled="!topNMode" class="rounded border-app bg-card text-app px-1.5 py-1 disabled:opacity-50" title="How many sections to show">
                    <option :value="5">5</option><option :value="10">10</option><option :value="15">15</option><option :value="20">20</option>
                  </select>
                </div>
              </div>
              <div v-if="!hasBarData && !isLoading" class="h-64 md:h-80 flex items-center justify-center text-sm text-muted">No data for current filters</div>
              <div v-else class="relative h-[300px]"><div class="absolute inset-0"><BarChart :data="statusBySection" /></div></div>
              <div class="mt-2 text-xs text-muted">Last updated: {{ timeAgo(lastUpdated) }}</div>
              <div v-if="isLoading" class="absolute inset-0 bg-card/70 flex items-center justify-center rounded-2xl">
                <svg class="animate-spin h-6 w-6 text-app" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 0 1 8-8v4a4 4 0 0 0-4 4H4z"/></svg>
              </div>
            </div>
          </template>
          <template #right>
            <div class="rounded-2xl border-app bg-card text-app p-4 relative overflow-hidden shadow-card ml-2 widget-eq-body">
              <div class="mb-2 text-sm font-semibold text-app flex items-center justify-between">
                <span>Resolved over Time ({{ rangeLabel }})</span>
                <label class="inline-flex items-center gap-1 text-xs font-normal">
                  <input type="checkbox" v-model="cumulativeMode" class="h-3.5 w-3.5 rounded border-app" />
                  Cumulative
                </label>
              </div>
              <div v-if="!hasLineData && !isLoading" class="h-64 md:h-80 flex items-center justify-center text-sm text-muted">No data for current filters</div>
              <div v-else class="relative h-[320px]"><div class="absolute inset-0"><LineChart :data="resolvedOverTime" /></div></div>
              <div v-if="isLoading" class="absolute inset-0 bg-card/70 flex items-center justify-center rounded-2xl">
                <svg class="animate-spin h-6 w-6 text-app" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 0 1 8-8v4a4 4 0 0 0-4 4H4z"/></svg>
              </div>
            </div>
          </template>
        </SplitPane>
      </template>
      <template #right>
        <div class="rounded-2xl border-app bg-card text-app overflow-hidden shadow-card widget-eq">
          <div class="px-4 py-3 border-b border-app text-sm font-semibold">Recent Failures</div>
          <div class="p-2">
            <RecentFailures 
                :items="recent" 
                :show-toolbar="false" 
                :show-bottom-actions="false" 
                :show-row-actions="true" 
                :loading="isLoading" 
                :show-header="false" 
                storage-key="rf-dashboard" 
                @view="openDetails" 
                @edit="handleEdit" 
                @notify="openNotifyModal" />
            <FailureDetailsDrawer v-model="drawerOpen" :item="activeItem" />
            <NotificationModal v-model="isNotifyModalOpen" :failure="failureToNotify" />
          </div>
        </div>
      </template>
    </SplitPane>
  </div>
</template>