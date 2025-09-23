<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue';
import { useRouter } from 'vue-router';
import { useFailureStore } from '@/stores/failures';
import { useInfrastructureStore } from '@/stores/infrastructure';
import SplitPane from '@/components/SplitPane.vue';
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
const infrastructureStore = useInfrastructureStore();
const router = useRouter();

// --- UI Controls & State ---
const topNMode = ref(true);
const topN = ref(10);
const autoRefresh = ref(false);
const intervalMs = ref(30000);
const chartsSplit = ref(60);
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
const split = ref(Number(localStorage.getItem('dashSplit') || 66));

// --- Data Fetching ---
onMounted(() => {
  refresh(); // Initial data load
  startTimer();
});

onBeforeUnmount(() => {
  stopTimer();
});

// --- Helper Functions ---
function toMs(ts) {
  if (ts == null) return null;
  if (typeof ts === 'number') return ts;
  const ms = new Date(ts).getTime();
  return Number.isNaN(ms) ? null : ms;
}

function rangeStart(key) {
  const now = new Date();
  if (key === 'today') return new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime();
  if (key === '7d') { const d = new Date(now); d.setDate(d.getDate() - 6); d.setHours(0,0,0,0); return d.getTime(); }
  if (key === '30d'){ const d = new Date(now); d.setDate(d.getDate() - 29); d.setHours(0,0,0,0); return d.getTime(); }
  return 0;
}

const nf = new Intl.NumberFormat('en-IN');
const formatInt = n => (typeof n === 'number' ? nf.format(n) : n);

function timeAgo(ts) {
  const ms = toMs(ts);
  if (ms == null) return '—';
  const diff = Date.now() - ms;
  const m = Math.floor(diff / 60000);
  if (m < 1) return 'just now';
  if (m < 60) return `${m}m ago`;
  const h = Math.floor(m / 60);
  if (h < 24) return `${h}h ago`;
  const d = Math.floor(h / 24);
  return `${d}d ago`;
}

function fmtDuration(ms) {
  if (!ms || ms < 0) return '—';
  const h = Math.floor(ms / 3600000);
  const m = Math.round((ms % 3600000) / 60000);
  return `${h}h ${m}m`;
}

// --- Computed Properties ---
const allSectionsMaster = computed(() =>
  (infrastructureStore.sections || []).map(s => s.name).sort()
);

const startTs = computed(() => rangeStart(filters.value.range));

const filtered = computed(() => {
  const allowedStatus = new Set(filters.value.status);
  const allowedSections = new Set(filters.value.sections || []);
  const ts0 = startTs.value;
  
  return failureStore.failures.filter(f => {
    if (!f) return false;
    if (allowedSections.size && !allowedSections.has(f.section?.name)) return false;
    if (!allowedStatus.has(f.current_status)) return false;
    
    const ts = f.current_status === 'Resolved' ? (toMs(f.resolved_at) ?? toMs(f.reported_at)) : toMs(f.reported_at);
    if (!ts) return false;
    return ts >= ts0;
  });
});

// KPIs
const kpiActive = computed(() => filtered.value.filter(f => f.current_status === 'Active').length);
const kpiResolved = computed(() => filtered.value.filter(f => f.current_status === 'Resolved').length);
const kpiCritical = computed(() => filtered.value.filter(f => f.severity === 'Critical').length);

const avgResolution = computed(() => {
  const res = filtered.value.filter(f => f.current_status === 'Resolved' && f.resolved_at && f.reported_at);
  if (!res.length) return '—';
  const avgMs = res.reduce((sum, f) => sum + (toMs(f.resolved_at) - toMs(f.reported_at)), 0) / res.length;
  return fmtDuration(avgMs);
});

const kpis = computed(() => ([
  { label: 'Active Failures', value: formatInt(kpiActive.value), sublabel: 'in range' },
  { label: 'Resolved', value: formatInt(kpiResolved.value), sublabel: 'in range' },
  { label: 'Avg Resolution Time', value: avgResolution.value, sublabel: 'for range' },
  { label: 'Critical Alerts', value: formatInt(kpiCritical.value), sublabel: 'filtered' },
]));

const recent = computed(() =>
  [...failureStore.failures]
    .sort((a,b) => (toMs(b.reported_at) ?? 0) - (toMs(a.reported_at) ?? 0))
    .slice(0, 8)
);

// --- Chart Specific Computeds ---
const allSectionsInFiltered = computed(() => Array.from(new Set(filtered.value.map(f => f.section?.name))).filter(name => name).sort());

function countBy(sectionName, status) {
  return filtered.value.filter(f => f.section?.name === sectionName && f.current_status === status).length;
}

const statusBySection = computed(() => {
  const labels = allSectionsInFiltered.value;
  const active = labels.map(s => countBy(s, 'Active'));
  const resolved = labels.map(s => countBy(s, 'Resolved'));

  return {
    labels,
    datasets: [
      { label: 'Active', data: active, borderRadius: 6 },
      { label: 'Resolved', data: resolved, borderRadius: 6 },
    ],
  };
});

function buildBuckets() {
  const now = new Date();
  const start = new Date(startTs.value);
  const ends = [];
  const labels = [];
  if (filters.value.range === 'today') {
    for (const h of [0, 4, 8, 12, 16, 20, 23]) {
      const t = new Date(start);
      t.setHours(h, 59, 59, 999);
      if (t.getTime() <= now.getTime() + 3 * 3600 * 1000) {
        ends.push(t.getTime());
        labels.push(new Date(t).toLocaleTimeString([], { hour: '2-digit' }));
      }
    }
  } else {
    const d = new Date(start);
    while (d.getTime() <= now.getTime()) {
      const end = new Date(d);
      end.setHours(23, 59, 59, 999);
      ends.push(end.getTime());
      labels.push(d.toLocaleDateString([], { month: 'short', day: '2-digit' }));
      d.setDate(d.getDate() + 1);
    }
  }
  return { ends, labels };
}

const resolvedOverTime = computed(() => {
  if (!filters.value.status.includes('Resolved')) {
    return { labels: [''], datasets: [{ label: 'Resolved', data: [0] }] };
  }
  const { ends, labels } = buildBuckets();
  const times = filtered.value
    .filter(f => f.current_status === 'Resolved' && f.resolved_at)
    .map(f => toMs(f.resolved_at))
    .filter(ts => ts && ts >= startTs.value)
    .sort((a, b) => a - b);

  const cum = [];
  let i = 0;
  for (const end of ends) {
    while (i < times.length && times[i] <= end) i++;
    cum.push(i);
  }

  const per = cum.map((v, idx) => (idx === 0 ? v : v - cum[idx - 1]));
  const series = cumulativeMode.value ? cum : per;
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
    failureStore.fetchFailures(),
    infrastructureStore.fetchSections(),
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
    lastUpdated.value = Date.now();
}

// --- Watchers ---
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
            />
            <FailureDetailsDrawer v-model="drawerOpen" :item="activeItem" />
          </div>
        </div>
      </template>
    </SplitPane>
  </div>
</template>