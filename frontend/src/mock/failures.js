// Minimal mock dataset used by Dashboard until backend/API is wired.
// You can freely add fields your UI expects (status, station, etc.).
export const failures = [
  {
    id: "RF001",
    circuit: "CKT-001",
    station: "Bandra",
    section: "Western Line",
    status: "Active",
    reportedAt: new Date().toISOString(),
    priority: "High",
  },
  {
    id: "RF002",
    circuit: "CKT-002",
    station: "Andheri",
    section: "Western Line",
    status: "In Progress",
    reportedAt: new Date(Date.now() - 3600_000).toISOString(),
    priority: "Medium",
  },
  {
    id: "RF003",
    circuit: "CKT-003",
    station: "Dadar",
    section: "Central Line",
    status: "Resolved",
    reportedAt: new Date(Date.now() - 6 * 3600_000).toISOString(),
    priority: "Low",
  },
];
