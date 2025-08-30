// src/api/mock.js
const demoData = [
  { fail_id: 'AA-0001', status: 'Active',   severity: 'High',     circuit: 'CIR-12', reported_at: '2025-08-19 08:20', assigned_to: 'Supervisor A' },
  { fail_id: 'AB-0342', status: 'Resolved', severity: 'Low',      circuit: 'CIR-05', reported_at: '2025-08-19 06:05', assigned_to: 'Supervisor B' },
  { fail_id: 'AC-1010', status: 'Active',   severity: 'Critical', circuit: 'CIR-77', reported_at: '2025-08-18 23:41', assigned_to: 'Supervisor C' },
  // add a few more rows so filtering feels real
  { fail_id: 'AD-2001', status: 'Active',   severity: 'Low',      circuit: 'CIR-33', reported_at: '2025-08-18 20:10', assigned_to: 'Supervisor D' },
  { fail_id: 'AE-3302', status: 'Resolved', severity: 'High',     circuit: 'CIR-12', reported_at: '2025-08-18 14:25', assigned_to: 'Supervisor E' },
]

export async function listFailures(params = {}) {
  // simulate network latency
  await new Promise(r => setTimeout(r, 400))
  // ignore params for now; return everything
  return { count: demoData.length, results: demoData }
}