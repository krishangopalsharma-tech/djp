// src/api/mock.js
const demoData = [
  { fail_id: 'AA-0001', status: 'Active',   severity: 'High',     circuit: 'CIR-12', reported_at: '2025-08-19 08:20', resolved_at: null, assigned_to: 'Supervisor A', station: 'Bandra',  section: 'Western Line' },
  { fail_id: 'AB-0342', status: 'Resolved', severity: 'Low',      circuit: 'CIR-05', reported_at: '2025-08-19 06:05', resolved_at: '2025-08-19 07:00', assigned_to: 'Supervisor B', station: 'Andheri', section: 'Western Line' },
  { fail_id: 'AC-1010', status: 'Resolved',   severity: 'Critical', circuit: 'CIR-77', reported_at: '2025-08-18 23:41', resolved_at: '2025-08-19 01:30', assigned_to: 'Supervisor C', station: 'Dadar',   section: 'Central Line' },
  // add a few more rows so filtering feels real
  { fail_id: 'AD-2001', status: 'Active',   severity: 'Low',      circuit: 'CIR-33', reported_at: '2025-08-18 20:10', resolved_at: null, assigned_to: 'Supervisor D', station: 'Virar',   section: 'Western Line' },
  { fail_id: 'AE-3302', status: 'Resolved', severity: 'High',     circuit: 'CIR-12', reported_at: '2025-08-18 14:25', resolved_at: '2025-08-18 15:00', assigned_to: 'Supervisor E', station: 'Churchgate', section: 'Western Line' },
]

export async function listFailures(params = {}) {
  // simulate network latency
  await new Promise(r => setTimeout(r, 400))
  // ignore params for now; return everything
  return { count: demoData.length, results: demoData }
}


  export async function getCircuits() {
  await new Promise(r => setTimeout(r, 100))
  const circuits = [...new Set(demoData.map(d => d.circuit))]
  return circuits.map(c => ({ label: c, value: c }))
}

export async function getSections() {
  await new Promise(r => setTimeout(r, 100))
  const sections = [...new Set(demoData.map(d => d.section))]
  return sections.map(s => ({ label: s, value: s }))
}

export async function getStations() {
  await new Promise(r => setTimeout(r, 100))
  const stations = [...new Set(demoData.map(d => d.station))]
  return stations.map(s => ({ label: s, value: s }))
}

export async function getSupervisors() {
  await new Promise(r => setTimeout(r, 100))
  const supervisors = [...new Set(demoData.map(d => d.assigned_to))]
  return supervisors.map(s => ({ label: s, value: s }))
}

export async function getStatuses() {
  await new Promise(r => setTimeout(r, 100))
  const statuses = [...new Set(demoData.map(d => d.status))]
  return statuses.map(s => ({ label: s, value: s }))
}

