// src/data/mockFailures.js
const now = new Date()
const ms = (h) => h * 3600 * 1000
const startOfToday = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime()

export const failures = [
  // Today
  { id: 'RF001', section: 'Section A', status: 'Active',      severity: 'Critical', reportedAt: now.getTime() - ms(2) },
  { id: 'RF002', section: 'Section B', status: 'In Progress', severity: 'Major',    reportedAt: now.getTime() - ms(5) },
  { id: 'RF003', section: 'Section C', status: 'Resolved',    severity: 'Minor',    reportedAt: startOfToday - ms(6), resolvedAt: startOfToday + ms(2) },
  { id: 'RF004', section: 'Section D', status: 'Resolved',    severity: 'Major',    reportedAt: startOfToday - ms(12), resolvedAt: startOfToday + ms(6) },

  // Last 7 days
  { id: 'RF005', section: 'Section A', status: 'Active',      severity: 'Minor',    reportedAt: startOfToday - ms(24) * 2 },
  { id: 'RF006', section: 'Section B', status: 'On Hold',     severity: 'Major',    reportedAt: startOfToday - ms(24) * 3 },
  { id: 'RF007', section: 'Section C', status: 'Resolved',    severity: 'Critical', reportedAt: startOfToday - ms(24) * 4, resolvedAt: startOfToday - ms(24) * 3.5 },
  { id: 'RF008', section: 'Section D', status: 'Resolved',    severity: 'Minor',    reportedAt: startOfToday - ms(24) * 5, resolvedAt: startOfToday - ms(24) * 4.8 },

  // Last 30 days
  { id: 'RF009',  section: 'Section A', status: 'Resolved',    severity: 'Minor',    reportedAt: startOfToday - ms(24) * 10, resolvedAt: startOfToday - ms(24) * 9.7 },
  { id: 'RF010',  section: 'Section B', status: 'Resolved',    severity: 'Major',    reportedAt: startOfToday - ms(24) * 15, resolvedAt: startOfToday - ms(24) * 14.5 },
  { id: 'RF011',  section: 'Section C', status: 'Active',      severity: 'Major',    reportedAt: startOfToday - ms(24) * 18 },
  { id: 'RF012',  section: 'Section D', status: 'In Progress', severity: 'Minor',    reportedAt: startOfToday - ms(24) * 20 },
  { id: 'RF013',  section: 'Section B', status: 'Resolved',    severity: 'Critical', reportedAt: startOfToday - ms(24) * 22, resolvedAt: startOfToday - ms(24) * 21.4 },
  { id: 'RF014',  section: 'Section C', status: 'On Hold',     severity: 'Major',    reportedAt: startOfToday - ms(24) * 25 },
]
