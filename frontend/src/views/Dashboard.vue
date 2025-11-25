<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue';
import { useRouter } from 'vue-router';
import { useFailureStore } from '@/stores/failures';
import { useSectionsStore } from '@/stores/sections';
import { useDashboardStore } from '@/stores/dashboard'; // Import dashboard store
import SplitPane from '@/components/SplitPane.vue'; // Re-imported
import KpiCard from '@/components/KpiCard.vue';
import BarChart from '@/components/BarChart.vue';
import LineChart from '@/components/LineChart.vue';
import DashboardFilterBar from '@/components/DashboardFilterBar.vue';
import RecentFailures from '@/components/RecentFailures.vue';
import SectionPicker from '@/components/SectionPicker.vue';
import FailureDetailsDrawer from '@/components/FailureDetailsDrawer.vue';
import { borderColor } from '@/lib/statusColors';
import { withAlpha } from '@/lib/theme';

// --- Store and Router setup ---
const failureStore = useFailureStore();
const sectionsStore = useSectionsStore();
const dashboardStore = useDashboardStore(); // Use dashboard store
const router = useRouter();

// --- UI Controls & State ---
const topNMode = ref(true);
const topN = ref(10);
const autoRefresh = ref(false);
const intervalMs = ref(30000);
const verticalSplit = ref(40); // Default 40% height for top chart
const horizontalSplit = ref(40); // Default 40% width for left chart
const cumulativeMode = ref(true);
const lastUpdated = ref(Date.now());
const isLoading = ref(false);
let refreshTimer = null;
const drawerOpen = ref(false);
const activeItem = ref(null);
const filters = ref({
  range: '30d',
  status: ['Active', 'In Progress', 'Resolved', 'On Hold', 'Draft'],
  sections: [],
});
// const split = ref(Number(localStorage.getItem('dashSplit') || 66)); // Removed

// --- Data Fetching ---
onMounted(() => {
  refresh(); // Initial data load
  startTimer();
});

onBeforeUnmount(() => {
  stopTimer();
});

// --- Helper Functions ---
function timeAgo(ts) {
  if (!ts) return '—';
  const diff = Date.now() - ts;
  const m = Math.floor(diff / 60000);
  if (m < 1) return 'just now';
  if (m < 60) return `${m}m ago`;
  const h = Math.floor(m / 60);
  if (h < 24) return `${h}h ago`;
  const d = Math.floor(h / 24);
  return `${d}d ago`;
}

// --- Computed Properties ---
const allSectionsMaster = computed(() =>
  (sectionsStore.sections || []).map(s => s.name).sort()
);

// Use data from dashboardStore
const kpis = computed(() => ([
  { label: 'Active Failures', value: dashboardStore.kpis?.active_failures ?? '—', sublabel: 'in range' },
  { label: 'Resolved', value: dashboardStore.kpis?.resolved_in_range ?? '—', sublabel: 'in range' },
  { label: 'Avg Resolution Time', value: dashboardStore.kpis?.avg_resolution_time ?? '—', sublabel: 'for range' },
  { label: 'Critical Alerts', value: dashboardStore.kpis?.critical_alerts ?? '—', sublabel: 'filtered' },
]));

const recent = computed(() => failureStore.recentFailures);

// --- Chart Specific Computeds ---
const statusBySection = computed(() => {
  const rawData = dashboardStore.charts?.status_by_section || [];
  // Limit to top N if enabled
  const data = topNMode.value ? rawData.slice(0, topN.value) : rawData;
  
  const labels = data.map(d => d.section__name);
  const active = data.map(d => d.active);
  const resolved = data.map(d => d.resolved);

  return {
    labels,
    datasets: [
      { label: 'Active', data: active, borderRadius: 6 },
      { label: 'Resolved', data: resolved, borderRadius: 6 },
    ],
  };
});

const resolvedOverTime = computed(() => {
  const rawData = dashboardStore.charts?.resolved_over_time || [];
  const labels = rawData.map(d => new Date(d.date).toLocaleDateString([], { month: 'short', day: '2-digit' }));
  const counts = rawData.map(d => d.count);

  // Calculate cumulative if needed
  let series = counts;
  if (cumulativeMode.value) {
    series = [];
    let sum = 0;
    for (const c of counts) {
      sum += c;
      series.push(sum);
    }
  }

  const primary = borderColor('Resolved');

  return {
    labels,
    datasets: [{
      label: cumulativeMode.value ? 'Resolved (cumulative)' : 'Resolved (daily)',
      data: series,
      tension: 0.3,
      fill: true,
      borderColor: primary,
      backgroundColor: withAlpha(primary, 0.2),
    }],
  };
});

const hasBarData = computed(() => {
    return statusBySection.value.labels && statusBySection.value.labels.length > 0;
});

const hasLineData = computed(() => {
    return resolvedOverTime.value.labels && resolvedOverTime.value.labels.length > 0;
});

const rangeLabel = computed(() =>
  filters.value.range === 'today' ? 'today' :
  filters.value.range === '7d' ? 'last 7 days' : 'last 30 days'
);

// --- Action Methods ---
function openDetails(item) {
  activeItem.value = item;
  drawerOpen.value = true;
}

function handleEdit(id) {
    router.push(`/failures/edit/${id}`);
}

function refresh() {
  isLoading.value = true;
  Promise.all([
    failureStore.fetchRecentFailures(), // Fetch recent failures
    sectionsStore.fetchSections(),
    dashboardStore.fetchDashboardData(filters.value), // Fetch aggregated data
  ]).finally(() => {
    setTimeout(() => {
      lastUpdated.value = Date.now();
      isLoading.value = false;
    }, 600);
  });
}

function startTimer() {
  stopTimer();
  if (autoRefresh.value) {
    refreshTimer = setInterval(refresh, Number(intervalMs.value) || 30000);
  }
}

function stopTimer() {
  if (refreshTimer) {
    clearInterval(refreshTimer);
    refreshTimer = null;
  }
}

function resetFilters() {
    filters.value = { 
        range: '30d', 
        status: ['Active','In Progress','Resolved','On Hold', 'Draft'], 
        sections: [] 
    };
    // Watcher will trigger refresh
}

// --- Watchers ---
watch([autoRefresh, intervalMs], startTimer);
// watch(split, v => localStorage.setItem('dashSplit', String(v))); // Removed
// Watch filters to auto-refresh dashboard data
watch(filters, () => {
    dashboardStore.fetchDashboardData(filters.value);
}, { deep: true });

</script>

<template>
  <div class="space-y-6">
    <div class="mt-3 mb-3 flex flex-wrap items-start justify-between gap-3">
      <div class="flex flex-wrap items-start gap-2">
          <DashboardFilterBar v-model="filters" :show-statuses="false" />
          <SectionPicker v-model="filters.sections" :sections="allSectionsMaster" :max-inline="1" placeholder="Search sections…" />
          <!-- Status Filters Moved Here -->
          <DashboardFilterBar v-model="filters" :show-ranges="false" />
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
        <button @click="refresh" :disabled="isLoading" class="h-10 inline-flex items-center gap-2 rounded-lg border-app bg-card text-app px-3 text-sm shadow-card hover:shadow-popover hover:bg-[var(--seasalt-lighter)] transition disabled:opacity-60 disabled:cursor-not-allowed" title="Refresh now">
          <svg viewBox="0 0 24 24" class="w-4 h-4 shrink-0 align-middle"><path fill="currentColor" d="M12 6V3l-4 4l4 4V8c2.76 0 5 2.24 5 5a5 5 0 0 1-8.66 3.54a1 1 0 1 0-1.41 1.41A7 7 0 0 0 19 13c0-3.87-3.13-7-7-7Z"/></svg>
          <span class="leading-none">Refresh</span>
        </button>
        <button @click="resetFilters" :disabled="isLoading" class="h-10 inline-flex items-center gap-2 rounded-lg border-app bg-card text-app px-3 text-sm shadow-card hover:shadow-popover hover:bg-[var(--seasalt-lighter)] transition disabled:opacity-60 disabled:cursor-not-allowed" title="Reset Filters">
          <svg viewBox="0 0 24 24" class="w-4 h-4 shrink-0 align-middle"><path fill="currentColor" d="M12 5a7 7 0 1 1-6.71 9H3a1 1 0 0 1 0-2h4v4a1 1 0 1 1-2 0v-1.52A9 9 0 1 0 12 3a1 1 0 1 1 0 2Z"/></svg>
          <span class="leading-none">Reset</span>
        </button>
      </div>
    </div>
      
    <!-- Removed separate DashboardFilterBar for statuses -->

    <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KpiCard v-for="(kpi, index) in kpis" :key="index" :label="kpi.label" :value="kpi.value" :sublabel="kpi.sublabel" />
    </div>
 
    <!-- Resizable Layout Container -->
    <div class="h-[800px] mt-4">
      <SplitPane v-model="verticalSplit" layout="vertical" :min="20" :max="80">
        <template #one>
          <!-- Middle Row: Status by Section (Full Width) -->
          <div class="rounded-2xl border-app bg-card text-app p-4 relative overflow-hidden shadow-card h-full flex flex-col">
            <div class="mb-2 text-sm font-semibold text-app flex items-center justify-between shrink-0">
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
            <div v-if="!hasBarData && !isLoading" class="flex-1 flex items-center justify-center text-sm text-muted">No data for current filters</div>
            <div v-else class="relative flex-1 w-full"><div class="absolute inset-0"><BarChart :data="statusBySection" /></div></div>
            <div class="mt-2 text-xs text-muted shrink-0">Last updated: {{ timeAgo(lastUpdated) }}</div>
            <div v-if="isLoading" class="absolute inset-0 bg-card/70 flex items-center justify-center rounded-2xl">
              <svg class="animate-spin h-6 w-6 text-app" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 0 1 8-8v4a4 4 0 0 0-4 4H4z"/></svg>
            </div>
          </div>
        </template>
        
        <template #two>
          <!-- Bottom Row: Resolved over Time + Recent Logs -->
          <SplitPane v-model="horizontalSplit" layout="horizontal" :min="20" :max="80">
            <template #one>
              <div class="rounded-2xl border-app bg-card text-app p-4 relative overflow-hidden shadow-card flex flex-col h-full">
                <div class="mb-2 text-sm font-semibold text-app flex items-center justify-between shrink-0">
                  <span>Resolved over Time ({{ rangeLabel }})</span>
                  <label class="inline-flex items-center gap-1 text-xs font-normal">
                    <input type="checkbox" v-model="cumulativeMode" class="h-3.5 w-3.5 rounded border-app" />
                    Cumulative
                  </label>
                </div>
                <div v-if="!hasLineData && !isLoading" class="flex-1 flex items-center justify-center text-sm text-muted">No data for current filters</div>
                <div v-else class="relative flex-1 w-full"><div class="absolute inset-0"><LineChart :data="resolvedOverTime" /></div></div>
                <div v-if="isLoading" class="absolute inset-0 bg-card/70 flex items-center justify-center rounded-2xl">
                  <svg class="animate-spin h-6 w-6 text-app" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 0 1 8-8v4a4 4 0 0 0-4 4H4z"/></svg>
                </div>
              </div>
            </template>
            
            <template #two>
              <div class="rounded-2xl border-app bg-card text-app overflow-hidden shadow-card flex flex-col h-full">
                <div class="px-4 py-3 border-b border-app text-sm font-semibold shrink-0">Recent Logs</div>
                <div class="p-2 flex-1 overflow-y-auto">
                  <RecentFailures 
                      :items="recent" 
                      :show-toolbar="false" 
                      :show-bottom-actions="false" 
                      :show-row-actions="false" 
                      :loading="isLoading" 
                      :show-header="false" 
                      :flat="true"
                      storage-key="rf-dashboard" 
                      @view="openDetails" 
                      @edit="handleEdit" 
                  />
                  <FailureDetailsDrawer v-model="drawerOpen" :item="activeItem" />
                </div>
              </div>
            </template>
          </SplitPane>
        </template>
      </SplitPane>
    </div>
  </div>
</template>