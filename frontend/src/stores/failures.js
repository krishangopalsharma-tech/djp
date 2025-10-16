import { defineStore } from 'pinia';
import { useUIStore } from './ui';

export const useFailureStore = defineStore('failure', {
  state: () => ({
    failures: [
        { id: 1, fail_id: 'DUMMY-001', circuit: { name: 'CKT-01' }, station: { name: 'STN-A' }, section: { name: 'SEC-A' }, current_status: 'Active', severity: 'Critical', reported_at: new Date().toISOString() },
        { id: 2, fail_id: 'DUMMY-002', circuit: { name: 'CKT-02' }, station: { name: 'STN-B' }, section: { name: 'SEC-B' }, current_status: 'Resolved', severity: 'Minor', reported_at: new Date().toISOString(), resolved_at: new Date().toISOString() },
    ],
    currentFailure: null,
    loading: false,
    error: null,
    archivedFailures: [],
  }),
  actions: {
    async fetchFailures() { this.loading = false; },
    async fetchFailure(id) { this.currentFailure = this.failures.find(f => f.id === id); },
    async addFailure(payload) { console.log('Mock add failure:', payload); useUIStore().pushToast({type: 'success', message: 'Mock failure added.'}); },
    async updateFailure(id, payload) { console.log('Mock update failure:', id, payload); useUIStore().pushToast({type: 'success', message: 'Mock failure updated.'}); },
    // Keep other function names but with no API calls
  },
});