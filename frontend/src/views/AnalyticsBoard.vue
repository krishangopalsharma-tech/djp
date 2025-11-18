<template>
  <div class="p-6 space-y-6">
    <div class="flex items-baseline justify-between">
      <div>
        <h2 class="text-2xl font-semibold">Analytics Board</h2>
        <!-- helper text removed per request -->
      </div>

      <div class="flex items-center gap-2 text-sm">
        <label class="flex items-center gap-2 text-app">
          <input type="checkbox" v-model="liveToday" class="h-4 w-4 rounded border-app" />
          Live: Today’s Failures
        </label>
        <label class="flex items-center gap-2 text-app">
          <input type="checkbox" v-model="liveRecent" class="h-4 w-4 rounded border-app" />
          Live: Recent Failures
        </label>
      </div>
    </div>

    <!-- Global filters: ranges + statuses -->
    <DashboardFilterBar v-model="filters" />

    <!-- Board grid -->
    <section class="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
      <div
        v-for="(p, idx) in panels"
        :key="p.id"
        class="rounded-2xl border-app bg-card text-app overflow-hidden shadow-card"
        :class="fullscreen === p.id ? 'fixed inset-6 z-50' : 'relative'"
        draggable="true"
        @dragstart="onDragStart(idx)"
        @dragover.prevent
        @drop="onDrop(idx)"
      >
        <!-- Header -->
        <div class="px-4 pt-3 pb-2 flex items-center gap-2 border-b border-app">
          <h3 class="font-semibold text-app flex-1 truncate">{{ p.title }}</h3>

          <!-- chart type -->
          <select v-model="state[p.id].type" class="rounded-lg border-app bg-card text-app px-2 py-1 text-sm">
            <option value="bar">Bar</option>
            <option value="line">Line</option>
            <option value="table">Table</option>
            <option value="pie">Pie</option>
            <option value="doughnut">Doughnut</option>
          </select>

          <!-- Fullscreen / close fullscreen -->
          <button class="p-1.5 rounded hover:bg-card" title="Toggle fullscreen" @click="toggleFullscreen(p.id)">
            <svg v-if="fullscreen !== p.id" class="w-4 h-4" viewBox="0 0 24 24"><path fill="currentColor" d="M4 10V4h6v2H6v4H4Zm10-4V4h6v6h-2V6h-4ZM6 14H4v6h6v-2H6v-4Zm14 0h-2v4h-4v2h6v-6Z"/></svg>
            <svg v-else class="w-4 h-4" viewBox="0 0 24 24"><path fill="currentColor" d="M14 10V6h4V4h-6v6h2ZM6 10V6h4V4H4v6h2Zm8 8v-4h2v6h-6v-2h4ZM6 14H4v6h6v-2H6v-4Z"/></svg>
          </button>

          <!-- Remove button hidden as per request -->
        </div>

        <!-- Toolbar (per-card filters): show only in fullscreen -->
        <div v-if="fullscreen === p.id" class="px-4 pt-2 pb-3 flex flex-wrap items-center gap-2">
          <!-- Time range pills -->
          <button
            v-for="r in ranges"
            :key="r.key"
            class="px-3 py-1.5 text-sm rounded-lg border"
            :class="state[p.id].range === r.key ? 'selected-primary' : 'bg-card text-app border-app hover-primary'"
            @click="setRange(p.id, r.key)"
          >
            {{ r.label }}
          </button>

          <!-- Custom dates -->
          <div v-if="state[p.id].range === 'custom'" class="ml-auto flex items-center gap-2">
            <input type="date" v-model="state[p.id].from" class="rounded-lg border-app bg-card text-app px-2 py-1 text-sm" />
            <span class="text-muted text-sm">to</span>
            <input type="date" v-model="state[p.id].to" class="rounded-lg border-app bg-card text-app px-2 py-1 text-sm" />
            <button class="px-3 py-1.5 text-sm rounded-lg border-app bg-card hover:bg-card" @click="applyCustom(p.id)">Apply</button>
          </div>
          <div v-else class="ml-auto"></div>

          <!-- Status chips (NEW) -->
          <div class="w-full mt-2 flex flex-wrap items-center gap-2">
            <span class="text-xs text-muted mr-1">Status:</span>

            <button
              v-for="s in statuses"
              :key="s"
              class="px-2.5 py-1 text-xs rounded-full border"
              :class="(state[p.id].statuses || []).includes(s) ? 'selected-primary' : 'bg-card text-app border-app hover-primary'"
              @click="togglePanelStatus(p.id, s)"
            >
              {{ s }}
            </button>

            <button
              class="ml-auto px-2.5 py-1 text-xs rounded-full border-app bg-card hover-primary"
              title="Select all statuses"
              @click="clearPanelStatuses(p.id)"
            >
              All
            </button>

            <!-- Severity filter (only for Failure card) -->
            <div v-if="p.kind==='failureSeverity'" class="ml-2 inline-flex items-center gap-2">
              <label class="text-xs text-muted">Severity</label>
              <select v-model="state[p.id].severity" class="rounded border-app bg-card text-app px-2 py-1 text-xs">
                <option value="all">All</option>
                <option value="minor">Minor</option>
                <option value="major">Major</option>
                <option value="critical">Critical</option>
              </select>
            </div>
          </div>
        </div>

        
        <!-- Body (resizable) -->
        <div class="px-4 pb-4">
          <div class="relative rounded-xl border-app bg-card text-app overflow-auto" style="min-height: 240px; resize: both;">
            <PanelBody
              :key="'panel-' + p.id"
              :panel="p"
              :state="state[p.id]"
              :data="panelData(p)"
              :chart-options="chartOptions"
            />
          </div>
        </div>
      </div>
    </section>

    <!-- Restore button when all removed -->
    <div v-if="panels.length === 0" class="text-center text-sm text-muted">
      All panels removed. <button class="underline" @click="restoreDefault">Restore defaults</button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, watch, onMounted, onBeforeUnmount, computed } from 'vue'
import { useUIStore } from '@/stores/ui'
const ui = useUIStore()
import PanelBody from '@/components/PanelBody.vue'
import DashboardFilterBar from '@/components/DashboardFilterBar.vue'
import { useFailureStore } from '@/stores/failures'

const failureStore = useFailureStore()

onMounted(() => {
  failureStore.fetchFailures(); // Initial data load
});

const statuses = ['Active', 'In Progress', 'Resolved', 'On Hold', 'Draft'];

/* ------------------- sample data generator ------------------- */


/* ------------------- board + per-panel state ------------------- */
const panels = ref([
  { id: 'today',       title: "Failure",                    kind: 'count' },
  { id: 'failureSeverity', title: 'Failure',                 kind: 'failureSeverity' },
  { id: 'avgtime',     title: 'Avg. Resolution Time',      kind: 'avgTime' },
  { id: 'bysection',   title: 'Failures by Section',       kind: 'bySection' },
  { id: 'bycircuit',   title: 'Failures by Circuit',       kind: 'byCircuit' },
  { id: 'statusdist',  title: 'Status Distribution',       kind: 'statusDistribution' },
  { id: 'bysuper',     title: 'Failure Count by Supervisor', kind: 'bySupervisor' },
])

const defaultState = () => ({
  type: 'bar',
  range: 'today',
  from: '',
  to: '',
  statuses: [...statuses], // select all by default
  severity: 'all',
})

function togglePanelStatus(id, s) {
  const arr = state[id].statuses || []
  const set = new Set(arr)
  set.has(s) ? set.delete(s) : set.add(s)
  state[id].statuses = Array.from(set)
}
function clearPanelStatuses(id) {
  state[id].statuses = [...statuses] // back to “All”
}


const state = reactive(Object.fromEntries(panels.value.map(p => [p.id, defaultState()])))
state.bysection.range = 'month'
state.bycircuit.range = 'month'
state.statusdist.range = 'month'
state.avgtime.range = 'month'

const liveToday = ref(true)
const liveRecent = ref(true)

// Global Analytics filters (UI only for now)
const filters = ref({ range: 'today', status: ['Active','In Progress','Resolved','On Hold'] })

// ---- persistence (localStorage) ----
const STORAGE_KEY = 'analyticsBoard.v1'

function serializeState() {
  const out = {}
  for (const id of Object.keys(state)) out[id] = { ...state[id] }
  return out
}

function saveBoard() {
  try {
    const payload = {
      panels: panels.value.map(p => ({ id: p.id, title: p.title, kind: p.kind })),
      state: serializeState(),
      liveToday: !!liveToday.value,
      liveRecent: !!liveRecent.value,
    }
    localStorage.setItem(STORAGE_KEY, JSON.stringify(payload))
  } catch (e) {
    console.warn('saveBoard failed', e)
  }
}

function loadBoard() {
  let saved = null
  try { saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || 'null') } catch (_) {}
  if (!saved || typeof saved !== 'object') return

  if (Array.isArray(saved.panels) && saved.panels.length) {
    panels.value = saved.panels
      .filter(p => p && p.id && p.kind && p.title)
      // Remove deprecated KPI panels per spec
      .filter(p => !['week','pending','recent'].includes(p.id))
      // Rename today's panel to "Failure"
      .map(p => p.id === 'today' ? { ...p, title: 'Failure' } : p)
    // Ensure new Failure-by-Severity card exists
    if (!panels.value.some(p => p.id === 'failureSeverity')) {
      panels.value.splice(1, 0, { id: 'failureSeverity', title: 'Failure', kind: 'failureSeverity' })
    }
  }

  const rebuilt = {}
  for (const p of panels.value) {
    rebuilt[p.id] = { ...defaultState(), ...(saved.state?.[p.id] || {}) }
  }
  Object.keys(state).forEach(k => delete state[k])
  Object.assign(state, rebuilt)

  if (typeof saved.liveToday === 'boolean')  liveToday.value  = saved.liveToday
  if (typeof saved.liveRecent === 'boolean') liveRecent.value = saved.liveRecent
}

// Load any saved layout/settings (now safe)
loadBoard()

// Save whenever layout or settings change
watch(panels, saveBoard, { deep: true })
watch(state,  saveBoard, { deep: true })
watch([liveToday, liveRecent], saveBoard)


/* ------------------- time ranges ------------------- */
const ranges = [
  { key: 'today',  label: 'Today' },
  { key: 'week',   label: 'This Week' },
  { key: 'month',  label: 'This Month' },
  { key: 'year',   label: 'This Year' },
  { key: 'custom', label: 'Custom' },
]
function startOfDay(ts){ const d=new Date(ts); d.setHours(0,0,0,0); return d.getTime() }
function startOfWeek(ts){ const d=new Date(ts); const day=(d.getDay()+6)%7; d.setDate(d.getDate()-day); d.setHours(0,0,0,0); return d.getTime() }
function startOfMonth(ts){ const d=new Date(ts); d.setDate(1); d.setHours(0,0,0,0); return d.getTime() }
function startOfYear(ts){ const d=new Date(ts); d.setMonth(0,1); d.setHours(0,0,0,0); return d.getTime() }
function bounds(rangeKey, from='', to=''){
  const now = Date.now()
  if(rangeKey==='today') return { start: startOfDay(now), end: now }
  if(rangeKey==='week')  return { start: startOfWeek(now), end: now }
  if(rangeKey==='month') return { start: startOfMonth(now), end: now }
  if(rangeKey==='year')  return { start: startOfYear(now), end: now }
  const s = from ? new Date(from).getTime() : startOfDay(now)
  const e = to ? (new Date(to).getTime() + 86399999) : now
  return { start: s, end: e }
}
function setRange(id, key){ state[id].range = key }
function applyCustom(_id){ /* state already holds from/to */ }

/* ------------------- data shaping helpers ------------------- */
const nf = new Intl.NumberFormat('en-IN')
function filterRange(rows, b){ return rows.filter(r => r.reported_at >= b.start && r.reported_at <= b.end) }
function countBy(rows, key){ 
  const m=new Map();
  rows.forEach(r=>{
    let val = r;
    // Handle nested properties like 'section.name'
    if (key.includes('.')) {
      const parts = key.split('.');
      for (const part of parts) {
        val = val ? val[part] : undefined;
      }
    } else {
      val = r[key];
    }
    if (val !== undefined) {
      m.set(val, (m.get(val)||0)+1);
    }
  });
  return m
 }
function toChart(m){ const labels=[...m.keys()]; const data=labels.map(l=>m.get(l)); return {labels, data} }
function avgResolutionMs(rows){
  const done = rows.filter(r => r.current_status==='Resolved' && r.resolved_at && r.reported_at)
  if(!done.length) return 0
  return Math.round(done.reduce((s,r)=>s+(r.resolved_at - r.reported_at),0) / done.length)
}
function fmtDuration(ms){
  if(!ms) return '—'
  const m = Math.round(ms/60000)
  const h = Math.floor(m/60)
  const mm = m%60
  return h? `${h}h ${mm}m` : `${mm}m`
}

/* ------------------- per-panel data ------------------- */
function panelData(p){
  const st = state[p.id]
  const { start, end } = bounds(st.range, st.from, st.to)
  const baseRows = filterRange(failureStore.failures, { start, end })
  const selected = (st.statuses && st.statuses.length) ? new Set(st.statuses) : new Set(statuses)
  const rows = baseRows.filter(r => selected.has(r.current_status))


  switch(p.kind){
    case 'failureSeverity': {
      // provide raw records for the card to aggregate by severity
      return { records: rows }
    }
    case 'count': {
      const byDay = new Map()
      rows.forEach(r=>{
        const d = new Date(r.reported_at); d.setHours(0,0,0,0)
        const k = d.toISOString().slice(0,10)
        byDay.set(k, (byDay.get(k)||0)+1)
      })
      const labels = [...byDay.keys()].sort()
      const data = labels.map(k=>byDay.get(k))
      return { labels, datasets: [{ label: 'Failure Count', data }] }
    }
    case 'pending': {
      const pending = rows.filter(r => r.current_status==='Active' || r.current_status==='In Progress' || r.current_status==='On Hold')
      const m = countBy(pending, 'current_status')
      const {labels, data} = toChart(m)
      return { labels, datasets: [{ label: 'Pending', data }] }
    }
    case 'avgTime': {
      const val = avgResolutionMs(rows)
      return { labels: ['Avg'], datasets: [{ label: fmtDuration(val), data: [Math.round(val/60000)] }], pretty: fmtDuration(val) }
    }
    case 'bySection': {
      const m = countBy(rows, 'section.name')
      const {labels, data} = toChart(m)
      return { labels, datasets: [{ label: 'Failures', data }] }
    }
    case 'byCircuit': {
      const m = countBy(rows, 'circuit')
      const {labels, data} = toChart(m)
      return { labels, datasets: [{ label: 'Failures', data }] }
    }
    case 'statusDistribution': {
      const m = countBy(rows, 'current_status')
      const {labels, data} = toChart(m)
      return { labels, datasets: [{ label: 'Status', data }] }
    }
    case 'bySupervisor': {
      const m = countBy(rows, 'supervisor')
      const {labels, data} = toChart(m)
      return { labels, datasets: [{ label: 'Failures', data }] }
    }
    case 'recent': {
      const recent = [...rows].sort((a,b)=>b.reported_at - a.reported_at).slice(0, 10)
      return { recent }
    }
    default:
      return { labels: [], datasets: [{ label: 'N/A', data: [] }] }
  }
}

/* ------------------- chart options ------------------- */
const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  resizeDelay: 150,
  plugins: {
    legend: { position: 'bottom' },
    tooltip: {
      callbacks: {
        title(ctx){ return ctx?.[0]?.label ?? '' },
        label(ctx){ const v = ctx.parsed?.y ?? ctx.parsed ?? 0; return `${ctx.dataset?.label ?? 'Value'}: ${nf.format(v)}` },
      }
    }
  },
  scales: { y: { beginAtZero: true, ticks: { callback: v => nf.format(v) } } }
}

/* ------------------- drag & drop reorder ------------------- */
let dragFrom = -1
function onDragStart(i){ dragFrom = i }
function onDrop(i){
  if(dragFrom < 0 || dragFrom === i) return
  const arr = panels.value
  const [moved] = arr.splice(dragFrom, 1)
  arr.splice(i, 0, moved)
  dragFrom = -1
}

/* ------------------- fullscreen toggle ------------------- */
const fullscreen = ref(null)
function toggleFullscreen(id){ fullscreen.value = (fullscreen.value === id ? null : id) }
function removePanel(id){
  const i = panels.value.findIndex(p=>p.id===id)
  if(i>=0) panels.value.splice(i,1)
}
function restoreDefault(){
  panels.value = [
    { id: 'today',       title: "Failure",                    kind: 'count' },
    { id: 'failureSeverity', title: 'Failure',                 kind: 'failureSeverity' },
    { id: 'avgtime',     title: 'Avg. Resolution Time',      kind: 'avgTime' },
    { id: 'bysection',   title: 'Failures by Section',       kind: 'bySection' },
    { id: 'bycircuit',   title: 'Failures by Circuit',       kind: 'byCircuit' },
    { id: 'statusdist',  title: 'Status Distribution',       kind: 'statusDistribution' },
    { id: 'bysuper',     title: 'Failure Count by Supervisor', kind: 'bySupervisor' },
  ]
    // reset state for the new set
  const rebuilt = {}
  for (const p of panels.value) rebuilt[p.id] = defaultState()
  Object.keys(state).forEach(k => delete state[k])
  Object.assign(state, rebuilt)
  // clear saved board
  localStorage.removeItem(STORAGE_KEY)
}


</script>

<style scoped>
[draggable="true"] { cursor: move; }
</style>
