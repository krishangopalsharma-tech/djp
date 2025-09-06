<script setup>
import { computed } from 'vue'
import BarChart from '@/components/BarChart.vue'
import { severityHex, severityBg, SEVERITY_ORDER } from '@/lib/severityColors'

const props = defineProps({
  range: { type: String, default: 'today' },
  records: { type: Array, default: () => [] },
  severity: { type: String, default: 'all' }, // 'all' | 'minor' | 'major' | 'critical'
})

// Normalize severity to title case used in palette
function normSeverity(s) {
  const m = String(s || '').toLowerCase()
  if (m === 'critical') return 'Critical'
  if (m === 'major') return 'Major'
  if (m === 'minor') return 'Minor'
  return 'Minor'
}

function recSeverity(rec) {
  // Map record.severity into Minor/Major/Critical; adapt here if model differs
  const raw = rec?.severity || rec?.Severity || rec?.sev || ''
  const n = String(raw).toLowerCase()
  if (n === 'critical') return 'Critical'
  if (n === 'major') return 'Major'
  if (n === 'minor') return 'Minor'
  // fallback mapping for datasets that only have 'Normal'
  if (n === 'normal') return 'Minor'
  return 'Minor'
}

function recTimeMs(rec) {
  const t = rec?.occurred_at || rec?.reportedAt || rec?.reported_at || rec?.ts
  const ms = typeof t === 'number' ? t : new Date(t).getTime()
  return Number.isFinite(ms) ? ms : 0
}

// Buckets for x-axis based on range
function buildBuckets(range) {
  const now = new Date()
  const labels = []
  const keys = []
  if (range === 'today') {
    // single-day bucket
    const key = now.toISOString().slice(0,10)
    labels.push('Today')
    keys.push(key)
  } else if (range === 'week') {
    for (let i=6;i>=0;i--) {
      const d = new Date(now)
      d.setDate(now.getDate() - i)
      labels.push(d.toLocaleDateString())
      keys.push(d.toISOString().slice(0,10))
    }
  } else if (range === 'month') {
    for (let i=29;i>=0;i--) {
      const d = new Date(now)
      d.setDate(now.getDate() - i)
      labels.push(d.toLocaleDateString())
      keys.push(d.toISOString().slice(0,10))
    }
  } else if (range === 'year') {
    for (let m=0;m<12;m++) {
      const d = new Date(now.getFullYear(), m, 1)
      labels.push(d.toLocaleString(undefined, { month: 'short' }))
      keys.push(`${d.getFullYear()}-${String(m+1).padStart(2,'0')}`)
    }
  } else {
    // default to last 7 days
    for (let i=6;i>=0;i--) {
      const d = new Date(now)
      d.setDate(now.getDate() - i)
      labels.push(d.toLocaleDateString())
      keys.push(d.toISOString().slice(0,10))
    }
  }
  return { labels, keys }
}

const includedSeverities = computed(() => {
  const s = String(props.severity || 'all').toLowerCase()
  return s === 'all' ? [...SEVERITY_ORDER] : [normSeverity(s)]
})

const chartData = computed(() => {
  const { labels, keys } = buildBuckets(props.range)
  // Aggregate counts per key per severity
  const buckets = new Map(keys.map(k => [k, { Critical: 0, Major: 0, Minor: 0 }]))
  for (const rec of props.records || []) {
    const ms = recTimeMs(rec)
    if (!ms) continue
    const d = new Date(ms)
    const dayKey = d.toISOString().slice(0,10)
    const monthKey = `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}`
    const key = keys.length === 1 ? dayKey : (keys.length === 12 ? monthKey : dayKey)
    if (!buckets.has(key)) continue
    const sev = recSeverity(rec)
    const row = buckets.get(key)
    row[sev] = (row[sev] || 0) + 1
  }

  const datasets = includedSeverities.value.map(sev => ({
    label: sev,
    data: keys.map(k => buckets.get(k)?.[sev] ?? 0),
    backgroundColor: severityBg(sev, 0.85),
    borderColor: severityHex(sev),
    borderWidth: 1,
    borderRadius: 6,
  }))

  return { labels, datasets }
})
</script>

<template>
  <div class="h-full w-full">
    <BarChart :data="chartData" :options="{ responsive: true, maintainAspectRatio: false, plugins: { colors: false } }" />
  </div>
</template>

