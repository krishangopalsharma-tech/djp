<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import SplitPane from '@/components/SplitPane.vue'
import KpiCard from '@/components/KpiCard.vue'
import BarChart from '@/components/BarChart.vue'
import LineChart from '@/components/LineChart.vue'
import DashboardFilterBar from '@/components/DashboardFilterBar.vue'
import RecentFailures from '@/components/RecentFailures.vue'
import SectionPicker from '@/components/SectionPicker.vue'
//import { failures } from '@/data/mockFailures'
import FailureDetailsDrawer from '@/components/FailureDetailsDrawer.vue'
import { failures as seedFailures } from '@/mock/failures'



// ==================== STATE MANAGEMENT ====================

// UI Controls
const topNMode = ref(true)
const topN = ref(10)
const autoRefresh = ref(false)
const intervalMs = ref(30000)
const cumulativeMode = ref(true) // true = cumulative (current); false = per-interval
const failures = seedFailures


// Load UI controls once (safe even if storage is empty)
let ui = null
try { ui = JSON.parse(localStorage.getItem('dashUI') || 'null') } catch (_) {}
if (ui && typeof ui === 'object') {
  if (typeof ui.topNMode === 'boolean') topNMode.value = ui.topNMode
  if (typeof ui.topN === 'number' && ui.topN > 0) topN.value = ui.topN
  if (typeof ui.intervalMs === 'number' && ui.intervalMs >= 10000) intervalMs.value = ui.intervalMs
  if (typeof ui.autoRefresh === 'boolean') autoRefresh.value = ui.autoRefresh
  if (typeof ui.cumulativeMode === 'boolean') cumulativeMode.value = ui.cumulativeMode
}

// Refresh state
const lastUpdated = ref(Date.now())
const isLoading = ref(false)
let refreshTimer = null
const drawerOpen = ref(false)
const activeItem = ref(null)

// Filters (persisted)
const filters = ref({
  range: 'today',
  status: ['Active', 'In Progress', 'Resolved', 'On Hold'],
  sections: [],
})

// Split pane (persisted)
const split = ref(Number(localStorage.getItem('dashSplit') || 66))
if (isNaN(split.value) || split.value < 35 || split.value > 80) split.value = 66

// ==================== COMPUTED PROPERTIES ====================

// Master lists
const allSectionsMaster = computed(() =>
  Array.from(new Set(failures.map(f => f.section))).sort()
)

// Load filters
try {
  const saved = JSON.parse(localStorage.getItem('dashFilters') || 'null')
  if (saved && typeof saved === 'object') {
    if (['today','7d','30d'].includes(saved.range)) filters.value.range = saved.range
    if (Array.isArray(saved.status) && saved.status.length) filters.value.status = saved.status
    if (Array.isArray(saved.sections)) {
      const valid = new Set(allSectionsMaster.value)
      const cleaned = saved.sections.filter(s => valid.has(s))
      filters.value.sections = cleaned.length ? cleaned : [...allSectionsMaster.value]
    }
  }
} catch (_) {}

// Range helpers
const startTs = computed(() => rangeStart(filters.value.range))

// Data filtering
const filtered = computed(() => {
  const allowedStatus = new Set(filters.value.status)
  const allowedSections = new Set(filters.value.sections || [])
  const ts0 = startTs.value
  return failures.filter(f => {
    if (allowedSections.size && !allowedSections.has(f.section)) return false
    if (!allowedStatus.has(f.status)) return false
    const ts = f.status === 'Resolved' ? (f.resolvedAt ?? f.reportedAt) : f.reportedAt
    return ts >= ts0
  })
})

// KPIs
const kpiActive   = computed(() => filtered.value.filter(f => f.status === 'Active').length)
const kpiResolved = computed(() => filtered.value.filter(f => f.status === 'Resolved').length)
const kpiCritical = computed(() => filtered.value.filter(f => f.severity === 'Critical').length)
const kpiTrend = computed(() => {
  const { nowStart, nowEnd, prevStart, prevEnd } = windowBounds()
  const nowRows  = filterWindow(nowStart, nowEnd)
  const prevRows = filterWindow(prevStart, prevEnd)
  const count = (rows, s) => rows.filter(r => r.status === s).length
  const avgResMs = rows => {
    const done = rows.filter(r => r.status === 'Resolved' && r.resolvedAt && r.reportedAt)
    if (!done.length) return null
    return done.reduce((sum, r) => sum + (r.resolvedAt - r.reportedAt), 0) / done.length
  }
  const countCritical = rows => rows.filter(r => r.severity === 'Critical').length
  const aNow = count(nowRows, 'Active'),   aPrev = count(prevRows, 'Active')
  const rNow = count(nowRows, 'Resolved'), rPrev = count(prevRows, 'Resolved')
  const tNow = avgResMs(nowRows),          tPrev = avgResMs(prevRows)
  const cNow = countCritical(nowRows),     cPrev = countCritical(prevRows)
  const delta = (now, prev, higherIsBetter) => {
    if (now == null || prev == null) return { dir: null, label: '' }
    const d = now - prev
    if (d === 0) return { dir: 'flat', label: 'no change' }
    const up = higherIsBetter ? d > 0 : d < 0
    const sign = d > 0 ? '+' : '−'
    return { dir: up ? 'up' : 'down', label: `${sign}${Math.abs(d)} vs prev` }
  }
  const deltaDuration = (nowMs, prevMs) => {
    if (nowMs == null || prevMs == null) return { dir: null, label: '' }
    const d = nowMs - prevMs            // lower is better
    const better = d < 0
    const sign = d > 0 ? '+' : '−'
    const mins = Math.abs(fmtMinutes(d))
    return { dir: better ? 'up' : 'down', label: `${sign}${mins}m vs prev` }
  }
  return {
    active:   delta(aNow, aPrev, false), // fewer active is better
    resolved: delta(rNow, rPrev, true),
    avgTime:  deltaDuration(tNow, tPrev),
    critical: delta(cNow, cPrev, false), // fewer critical is better
  }
})

const avgResolution = computed(() => {
  const res = filtered.value.filter(f => f.status === 'Resolved' && f.resolvedAt && f.reportedAt)
  if (!res.length) return '—'
  const avgMs = res.reduce((sum, f) => sum + (f.resolvedAt - f.reportedAt), 0) / res.length
  return fmtDuration(avgMs)
})

const kpis = computed(() => ([
  {
    label: 'Active Failures',
    value: formatInt(kpiActive.value),
    sublabel: filters.value.range === 'today' ? 'live (today)' : 'live in range',
    trendDir:   kpiTrend.value.active.dir,
    trendLabel: kpiTrend.value.active.label,
  },
  {
    label: 'Resolved',
    value: formatInt(kpiResolved.value),
    sublabel: filters.value.range === 'today' ? 'today' : 'in range',
    trendDir:   kpiTrend.value.resolved.dir,
    trendLabel: kpiTrend.value.resolved.label,
  },
  {
    label: 'Avg Resolution Time',
    value: avgResolution.value, // keep as is (already “1h 42m” etc.)
    sublabel: filters.value.range === 'today' ? 'for today' : 'for range',
    trendDir:   kpiTrend.value.avgTime.dir,
    trendLabel: kpiTrend.value.avgTime.label,
  },
  {
    label: 'Critical Alerts',
    value: formatInt(kpiCritical.value),
    sublabel: 'filtered',
    trendDir:   kpiTrend.value.critical.dir,
    trendLabel: kpiTrend.value.critical.label,
  },
]))


// Charts: Bar
const allSections = computed(() => Array.from(new Set(filtered.value.map(f => f.section))).sort())
const statusBySection = computed(() => {
  const labels = allSections.value
  const active = labels.map(s => countBy(s, 'Active'))
  const resolved = labels.map(s => countBy(s, 'Resolved'))
  if (!topNMode.value || labels.length <= topN.value) {
    return {
      labels,
      datasets: [
        { label: 'Active',   data: active,   backgroundColor: 'rgba(239,68,68,0.5)',  borderRadius: 6 },
        { label: 'Resolved', data: resolved, backgroundColor: 'rgba(34,197,94,0.5)', borderRadius: 6 },
      ],
    }
  }
  const rows = labels.map((s, i) => ({ s, a: active[i], r: resolved[i], t: active[i] + resolved[i] }))
  rows.sort((x, y) => y.t - x.t)
  const n = Math.max(1, Number(topN.value) || 10)
  const top = rows.slice(0, n)
  const rest = rows.slice(top.length)
  const labels2 = top.map(r => r.s)
  const active2 = top.map(r => r.a)
  const resolved2 = top.map(r => r.r)
  if (rest.length) {
    labels2.push('Others')
    active2.push(rest.reduce((sum, r) => sum + r.a, 0))
    resolved2.push(rest.reduce((sum, r) => sum + r.r, 0))
  }
  return {
    labels: labels2,
    datasets: [
      { label: 'Active',   data: active2,   backgroundColor: 'rgba(239,68,68,0.5)',  borderRadius: 6 },
      { label: 'Resolved', data: resolved2, backgroundColor: 'rgba(34,197,94,0.5)', borderRadius: 6 },
    ],
  }
})

const totalsBySection = computed(() => {
  const m = new Map()
  for (const s of allSections.value) m.set(s, countBy(s, 'Active') + countBy(s, 'Resolved'))
  return m
})

const topRank = computed(() => {
  const sorted = [...allSections.value].sort((a, b) => (totalsBySection.value.get(b) || 0) - (totalsBySection.value.get(a) || 0))
  const n = Math.max(1, Number(topN.value) || 10)
  const top = topNMode.value ? sorted.slice(0, n) : sorted
  const others = topNMode.value ? sorted.slice(top.length) : []
  return { top, others }
})

const barKey = computed(() => {
  const sb = statusBySection.value
  const st  = [...filters.value.status].sort().join('-')
  const sec = [...filters.value.sections].sort().join('-')
  return [
    filters.value.range,
    st, sec,
    topNMode.value ? `top-${topN.value}` : 'all',
    sb.labels.join(','),
    (sb.datasets?.[0]?.data || []).join(','),
    (sb.datasets?.[1]?.data || []).join(','),
  ].join('|')
})

const hasBarData = computed(() => {
  const ds = statusBySection.value?.datasets || []
  return ds.some(d => Array.isArray(d.data) && d.data.some(v => Number(v) > 0))
})

// Charts: Line
const rangeLabel = computed(() =>
  filters.value.range === 'today' ? 'today' :
  filters.value.range === '7d'    ? 'last 7 days' : 'last 30 days'
)

const resolvedOverTime = computed(() => {
  if (!filters.value.status.includes('Resolved')) {
    return { labels: [''], datasets: [{ label: 'Resolved', data: [0] }] }
  }
  const { ends, labels } = buildBuckets()
  const times = filtered.value
    .filter(f => f.status === 'Resolved' && f.resolvedAt)
    .map(f => f.resolvedAt)
    .filter(ts => ts >= startTs.value)
    .sort((a,b) => a - b)
  // cumulative counts per bucket
  const cum = []
  let i = 0
  for (const end of ends) { while (i < times.length && times[i] <= end) i++; cum.push(i) }
  // per-interval = first bucket stays same, next buckets are diffs
  const per = cum.map((v, idx) => idx === 0 ? v : v - cum[idx - 1])
  const series = cumulativeMode.value ? cum : per
  return {
    labels,
    datasets: [{
      label: cumulativeMode.value ? 'Resolved (cumulative)' : 'Resolved (per interval)',
      data: series,
      tension: 0.3,
      fill: true,
      borderColor: 'rgba(59,130,246,1)',
      backgroundColor: 'rgba(59,130,246,0.2)'
    }]
  }
})

const hasLineData = computed(() => {
  const ds = resolvedOverTime.value?.datasets || []
  return ds.some(d => Array.isArray(d.data) && d.data.some(v => Number(v) > 0))
})

const lineKey = computed(() => {
  const ro = resolvedOverTime.value
  const sec = [...filters.value.sections].sort().join('-')
  const mode = cumulativeMode.value ? 'cum' : 'per'
  return `${filters.value.range}|${[...filters.value.status].sort().join('-')}|${sec}|${mode}|${ro.labels.join(',')}|${(ro.datasets[0]?.data || []).join(',')}`
})

// Recent list
const recent = computed(() =>
  [...filtered.value]
    .sort((a,b) => (b.resolvedAt ?? b.reportedAt ?? 0) - (a.resolvedAt ?? a.reportedAt ?? 0))
    .slice(0, 8)
)

// Chart options
const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  resizeDelay: 200,
  plugins: {
    legend: { position: 'bottom' },
    tooltip: {
      callbacks: {
        title(ctx) {
          return ctx?.[0]?.label ?? ''
        },
        label(ctx) {
          const val = ctx.parsed?.y ?? ctx.parsed ?? 0
          return `${ctx.dataset?.label ?? 'Value'}: ${nf.format(val)}`
        },
      },
    },
  },
  scales: {
    y: {
      beginAtZero: true,
      ticks: {
        callback: (v) => nf.format(v),
      },
    },
  },
}

const barOptions = computed(() => ({
  ...chartOptions,
  plugins: {
    ...chartOptions.plugins,
    tooltip: {
      ...chartOptions.plugins.tooltip,
      callbacks: {
        ...chartOptions.plugins.tooltip.callbacks,
        footer(items) {
          const i = items?.[0]?.dataIndex
          if (i == null) return ''
          const a = statusBySection.value.datasets?.[0]?.data?.[i] ?? 0
          const r = statusBySection.value.datasets?.[1]?.data?.[i] ?? 0
          const t = a + r
          return `Total: ${nf.format(t)}`
        },
      },
    },
  },
  onClick(evt, elements) {
    const el = elements?.[0]
    if (!el) return
    const label = statusBySection.value.labels[el.index]
    if (label === 'Others' && topNMode.value) {
      const { others } = topRank.value
      if (!others.length) return
      const cur = new Set(filters.value.sections)
      const isOnlyOthers = cur.size === others.length && others.every(s => cur.has(s))
      filters.value.sections = isOnlyOthers ? [...allSectionsMaster.value] : others
    } else {
      toggleSectionOnlyByLabel(label)
    }
  },
}))


// ==================== HELPER FUNCTIONS ====================

// Format time ago
function timeAgo(ts) {
  const diff = Date.now() - ts, m = Math.floor(diff/60000)
  if (m < 1) return 'just now'
  if (m < 60) return `${m}m ago`
  const h = Math.floor(m/60); if (h < 24) return `${h}h ago`
  const d = Math.floor(h/24); return `${d}d ago`
}

// Pretty integer formatting (Indian/Intl grouping)
const nf = new Intl.NumberFormat('en-IN')
const formatInt = n => (typeof n === 'number' ? nf.format(n) : n)


// Get range start timestamp
function rangeStart(key) {
  const now = new Date()
  if (key === 'today') return new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime()
  if (key === '7d') { const d = new Date(now); d.setDate(d.getDate() - 6); d.setHours(0,0,0,0); return d.getTime() }
  if (key === '30d'){ const d = new Date(now); d.setDate(d.getDate() - 29); d.setHours(0,0,0,0); return d.getTime() }
  return 0
}

// Get window bounds
function windowBounds() {
  const nowEnd = Date.now()
  const nowStart = startTs.value
  const dur = nowEnd - nowStart
  const prevEnd = nowStart - 1
  const prevStart = prevEnd - dur
  return { nowStart, nowEnd, prevStart, prevEnd }
}

// Filter data within a time window
function filterWindow(start, end) {
  const allowedStatus = new Set(filters.value.status)
  const allowedSections = new Set(filters.value.sections || [])
  return failures.filter(f => {
    if (allowedSections.size && !allowedSections.has(f.section)) return false
    if (!allowedStatus.has(f.status)) return false
    const ts = f.status === 'Resolved' ? (f.resolvedAt ?? f.reportedAt) : f.reportedAt
    return ts >= start && ts <= end
  })
}

// Format milliseconds to minutes
function fmtMinutes(ms) {
  if (ms == null) return null
  return Math.round(ms / 60000)
}

// Format duration
function fmtDuration(ms) {
  if (!ms || ms < 0) return '—'
  const h = Math.floor(ms / 3600000)
  const m = Math.round((ms % 3600000) / 60000)
  return `${h}h ${m}m`
}

// Count failures by section and status
function countBy(section, status) { 
  return filtered.value.filter(f => f.section === section && f.status === status).length 
}

// Set all sections in filter
function setAllSections() { 
  filters.value.sections = [...allSectionsMaster.value] 
}

// Toggle section filter
function toggleSectionOnlyByLabel(label) {
  const cur = new Set(filters.value.sections)
  if (cur.size === 1 && cur.has(label)) setAllSections()
  else filters.value.sections = [label]
}

// Set all statuses in filter
function setAllStatuses(){ 
  filters.value.status = ['Active','In Progress','Resolved','On Hold'] 
}

// Toggle status filter
function toggleStatusOnly(status){
  const cur = filters.value.status.slice().sort().join('|')
  const only = [status].sort().join('|')
  if (cur === only) setAllStatuses(); else filters.value.status = [status]
}

// Build time buckets for line chart
function buildBuckets() {
  const now = new Date()
  const start = new Date(startTs.value)
  const ends = []; const labels = []
  if (filters.value.range === 'today') {
    for (const h of [0,4,8,12,16,20]) {
      const t = new Date(start); t.setHours(h,0,0,0)
      if (t.getTime() <= now.getTime()) { ends.push(t.getTime()); labels.push(t.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })) }
    }
  } else {
    const d = new Date(start)
    while (d.getTime() <= now.getTime()) {
      const end = new Date(d); end.setHours(23,59,59,999)
      ends.push(end.getTime()); labels.push(d.toLocaleDateString([], { month: 'short', day: '2-digit' }))
      d.setDate(d.getDate() + 1)
    }
  }
  return { ends, labels }
}

// Open failure details drawer
function openDetails(item) {
  activeItem.value = item
  drawerOpen.value = true
}

// Refresh data
function refresh() {
  isLoading.value = true
  setTimeout(() => { lastUpdated.value = Date.now(); isLoading.value = false }, 600)
}

// Start auto-refresh timer
function startTimer() {
  stopTimer()
  if (autoRefresh.value) refreshTimer = setInterval(refresh, Number(intervalMs.value) || 30000)
}

// Stop auto-refresh timer
function stopTimer() {
  if (refreshTimer) { clearInterval(refreshTimer); refreshTimer = null }
}

// ==================== WATCHERS (React to data changes) ====================

// Watcher for auto-refresh settings - START: WATCHER
watch([autoRefresh, intervalMs], startTimer)
// END: WATCHER

// Watcher for UI controls persistence - START: WATCHER
watch([topNMode, topN, intervalMs, autoRefresh], ([m, n, i, a]) => {
  localStorage.setItem('dashUI', JSON.stringify({ topNMode: m, topN: Number(n), intervalMs: Number(i), autoRefresh: a }))
})
// END: WATCHER

// Watcher for filters persistence - START: WATCHER
watch(filters, v => localStorage.setItem('dashFilters', JSON.stringify(v)), { deep: true })
// END: WATCHER

// Watcher for split pane persistence - START: WATCHER
watch(split, v => localStorage.setItem('dashSplit', String(v)))
// END: WATCHER

// ==================== LIFECYCLE HOOKS ====================

// Start timer when component mounts
onMounted(startTimer)

// Stop timer when component unmounts
onBeforeUnmount(stopTimer)
</script>

<template>
  <div class="space-y-6">
    <div>
      <h2 class="text-2xl font-semibold">Dashboard</h2>
      <p class="text-sm text-gray-500">Overview</p>
    </div>
    
    <!-- Filters -->
    <DashboardFilterBar v-model="filters" />
        <div class="mt-1">
      <SectionPicker v-model="filters.sections" :sections="allSectionsMaster" :max-inline="6" placeholder="Search sections…" />
    </div>
    
    <!-- Toolbar -->
    <div class="flex items-center gap-3 justify-between">
      <div class="text-xs text-gray-500">Last updated: {{ timeAgo(lastUpdated) }}</div>
      <div class="flex items-center gap-2">
        <select v-model="intervalMs" class="rounded-lg border px-2 py-1 text-sm bg-white" title="Auto-refresh interval">
          <option :value="10000">10s</option>
          <option :value="30000">30s</option>
          <option :value="60000">1m</option>
          <option :value="300000">5m</option>
        </select>
        <label class="flex items-center gap-2 text-sm">
          <input type="checkbox" v-model="autoRefresh" class="h-4 w-4 rounded border align-middle" />
          <span class="align-middle">Auto-refresh</span>
        </label>
        <button
          @click="refresh"
          :disabled="isLoading"
          class="inline-flex items-center gap-2 rounded-lg border px-3 py-2 text-sm hover:bg-gray-50 disabled:opacity-60 disabled:cursor-not-allowed"
          title="Refresh now"
        >
          <svg viewBox="0 0 24 24" class="w-4 h-4 shrink-0 align-middle">
            <path fill="currentColor" d="M12 6V3l-4 4l4 4V8c2.76 0 5 2.24 5 5a5 5 0 0 1-8.66 3.54a1 1 0 1 0-1.41 1.41A7 7 0 0 0 19 13c0-3.87-3.13-7-7-7Z"/>
          </svg>
          <span class="leading-none">Refresh</span>
        </button>
        <button
          @click="(() => { filters.value = { range: 'today', status: ['Active','In Progress','Resolved','On Hold'], sections: [...allSectionsMaster] }; lastUpdated.value = Date.now() })()"
          :disabled="isLoading"
          class="inline-flex items-center gap-2 rounded-lg border px-3 py-2 text-sm hover:bg-gray-50 disabled:opacity-60 disabled:cursor-not-allowed"
          title="Reset to Today + All statuses + All sections"
        >
          <svg viewBox="0 0 24 24" class="w-4 h-4 shrink-0 align-middle">
            <path fill="currentColor" d="M12 5a7 7 0 1 1-6.71 9H3a1 1 0 0 1 0-2h4v4a1 1 0 1 1-2 0v-1.52A9 9 0 1 0 12 3a1 1 0 1 1 0 2Z"/>
          </svg>
          <span class="leading-none">Reset</span>
        </button>
      </div>
    </div>
    
    <!-- KPIs -->
    <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <div class="cursor-pointer" @click="toggleStatusOnly('Active')" title="Filter to Active / reset on second click">
        <KpiCard
          :label="kpis[0].label"
          :value="kpis[0].value"
          :sublabel="kpis[0].sublabel"
          :trend-dir="kpis[0].trendDir"
          :trend-label="kpis[0].trendLabel"
        />
      </div>
      <div class="cursor-pointer" @click="toggleStatusOnly('Resolved')" title="Filter to Resolved / reset on second click">
        <KpiCard
          :label="kpis[1].label"
          :value="kpis[1].value"
          :sublabel="kpis[1].sublabel"
          :trend-dir="kpis[1].trendDir"
          :trend-label="kpis[1].trendLabel"
        />
      </div>
      <KpiCard
        :label="kpis[2].label"
        :value="kpis[2].value"
        :sublabel="kpis[2].sublabel"
        :trend-dir="kpis[2].trendDir"
        :trend-label="kpis[2].trendLabel"
      />
      <KpiCard
        :label="kpis[3].label"
        :value="kpis[3].value"
        :sublabel="kpis[3].sublabel"
        :trend-dir="kpis[3].trendDir"
        :trend-label="kpis[3].trendLabel"
      />
    </div>

    <!-- Split charts (left) and recent list (right) -->
    <SplitPane v-model="split">
      <template #left>
        <div class="grid gap-4 lg:grid-cols-2">
          <!-- Bar -->
          <div class="rounded-2xl border bg-white p-4 relative">
            <div class="mb-2 text-sm font-semibold text-gray-700 flex items-center justify-between">
              <span>Status by Section</span>
              <div class="flex items-center gap-2 text-xs font-normal">
                <label class="inline-flex items-center gap-1">
                  <input type="checkbox" v-model="topNMode" class="h-3.5 w-3.5 rounded border" />
                  Top-N
                </label>
                <select
                  v-model="topN"
                  :disabled="!topNMode"
                  class="rounded border px-1.5 py-1 bg-white disabled:opacity-50"
                  title="How many sections to show"
                >
                  <option :value="5">5</option>
                  <option :value="10">10</option>
                  <option :value="15">15</option>
                  <option :value="20">20</option>
                </select>
              </div>
            </div>
            <div v-if="!hasBarData && !isLoading" class="h-64 md:h-80 flex items-center justify-center text-sm text-gray-500">
              No data for current filters
            </div>
            <div class="rounded-2xl border bg-white p-4">
              <div class="mb-2 text-sm font-semibold text-gray-700 flex items-center justify-between">
                <span>Status by Section</span>
              </div>

              <div class="relative h-[300px]">
                <!-- Loading skeleton -->
                <div v-if="isLoading" class="absolute inset-0 p-4">
                  <div class="h-6 w-40 rounded bg-gray-200 animate-pulse mb-4"></div>
                  <div class="grid grid-cols-6 gap-3 items-end h-[220px]">
                    <div v-for="i in 6" :key="'skb'+i" class="rounded bg-gray-200 animate-pulse" :style="{ height: (20 + i*10) + 'px' }"></div>
                  </div>
                </div>

                <!-- No data -->
                <div v-else-if="!hasBarData" class="absolute inset-0 flex items-center justify-center">
                  <div class="text-sm text-gray-500">
                    No data for the current filters.
                  </div>
                </div>

                <!-- Chart -->
                <div v-else class="absolute inset-0">
                  <BarChart :data="statusBySection" :options="barOptions" />
                </div>
              </div>
            </div>

            <div v-if="isLoading" class="absolute inset-0 bg-white/70 flex items-center justify-center rounded-2xl">
              <svg class="animate-spin h-6 w-6 text-gray-700" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"/>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 0 1 8-8v4a4 4 0 0 0-4 4H4z"/>
              </svg>
            </div>
          </div>
          <!-- Line -->
          <div class="rounded-2xl border bg-white p-4 relative">
            <div class="mb-2 text-sm font-semibold text-gray-700 flex items-center justify-between">
              <span>Resolved over Time ({{ rangeLabel }})</span>
              <label class="inline-flex items-center gap-1 text-xs font-normal">
                <input type="checkbox" v-model="cumulativeMode" class="h-3.5 w-3.5 rounded border" />
                Cumulative
              </label>
            </div>
            <div v-if="!hasLineData && !isLoading" class="h-64 md:h-80 flex items-center justify-center text-sm text-gray-500">
              No data for current filters
            </div>
            <div class="rounded-2xl border bg-white p-4">
              <div class="mb-2 text-sm font-semibold text-gray-700 flex items-center justify-between">
                <span>Resolved over Time ({{ rangeLabel }})</span>
                <label class="inline-flex items-center gap-1 text-xs font-normal">
                  <input type="checkbox" v-model="cumulativeMode" class="h-3.5 w-3.5 rounded border" />
                  Cumulative
                </label>
              </div>

              <div class="relative h-[300px]">
                <!-- Loading skeleton -->
                <div v-if="isLoading" class="absolute inset-0 p-4">
                  <div class="h-6 w-48 rounded bg-gray-200 animate-pulse mb-4"></div>
                  <div class="h-[220px] rounded bg-gray-200 animate-pulse"></div>
                </div>

                <!-- No data -->
                <div v-else-if="!hasLineData" class="absolute inset-0 flex items-center justify-center">
                  <div class="text-sm text-gray-500">No resolved items in this range.</div>
                </div>

                <!-- Chart -->
                <div v-else class="absolute inset-0">
                  <LineChart :data="resolvedOverTime" :options="chartOptions" />
                </div>
              </div>
            </div>

            <div v-if="isLoading" class="absolute inset-0 bg-white/70 flex items-center justify-center rounded-2xl">
              <svg class="animate-spin h-6 w-6 text-gray-700" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"/>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 0 1 8-8v4a4 4 0 0 0-4 4H4z"/>
              </svg>
            </div>
          </div>
        </div>
      </template>
      <template #right>
        <div class="rounded-2xl border bg-white mt-4 lg:mt-0">
          <div class="px-4 py-3 border-b text-sm font-semibold">Recent Failures</div>
          <div class="p-2">
            <RecentFailures
                :items="recent"
                :show-toolbar="false"
                :show-bottom-actions="false"
                :show-row-actions="false"
                :loading="isLoading"
                 storage-key="rf-dashboard"
                @view="openDetails"
              />
              <!-- Mount once near the end of template -->
              <FailureDetailsDrawer v-model="drawerOpen" :item="activeItem" 
                @notify="row => console.log('notify', row)"
                @edit="row => console.log('edit', row)"
                @delete="row => console.log('delete', row)"
              />
          </div>
        </div>
      </template>
    </SplitPane>
  </div>
</template>