// frontend/src/stores/supervisorMovements.js
import { defineStore } from 'pinia'

const uid = () =>
  (typeof crypto !== 'undefined' && crypto.randomUUID)
    ? crypto.randomUUID()
    : `${Math.random().toString(36).slice(2)}${Date.now().toString(36)}`

export const useSupervisorMovements = defineStore('supervisorMovements', {
  state: () => ({
    rows: [
      {
        id: uid(),
        // NEW fields
        dept: 'S&T',
        name: 'A. Sharma',            // Name of supervisor
        designation: 'Senior Section Engineer',
        location: 'Ahmedabad',        // base location
        onLeave: false,
        leaveFrom: '',                // YYYY-MM-DD
        leaveTo: '',                  // YYYY-MM-DD
        lookAfterId: '',              // supervisor id who looks after
        purpose: 'Site inspection',
        notes: '',
      },
    ],
  }),
  actions: {
    addEmpty() {
      this.rows.push({
        id: uid(),
        dept: '',
        name: '',
        designation: '',
        location: '',
        onLeave: false,
        leaveFrom: '',
        leaveTo: '',
        lookAfterId: '',
        purpose: '',
        notes: '',
      })
    },
    remove(id) {
      this.rows = this.rows.filter(r => r.id !== id)
    },
    update(id, patch) {
      const i = this.rows.findIndex(r => r.id === id)
      if (i !== -1) this.rows[i] = { ...this.rows[i], ...patch }
    },
  },
})
