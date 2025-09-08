// frontend/src/stores/reports.js
import { defineStore } from 'pinia'

// Safe ID generator (works even if crypto.randomUUID is unavailable)
const uid = () =>
  (typeof crypto !== 'undefined' && crypto.randomUUID)
    ? crypto.randomUUID()
    : `${Math.random().toString(36).slice(2)}${Date.now().toString(36)}`

export const useReportsStore = defineStore('reports', {
  state: () => ({
    items: [
      {
        id: uid(),
        name: 'Daily Failure Summary',
        templateName: 'failure_summary.xlsx',     // UI only; not uploaded
        schedule: { freq: 'daily', dow: 'Mon', dom: '1', time: '09:00' },
        sendEmail: true,
        sendTelegram: false,
        telegramGroupKey: 'reports',
      },
      {
        id: uid(),
        name: 'Weekly Section KPIs',
        templateName: 'section_kpis.xlsx',
        schedule: { freq: 'weekly', dow: 'Mon', dom: '1', time: '08:30' },
        sendEmail: true,
        sendTelegram: true,
        telegramGroupKey: 'reports',
      },
    ],
  }),
  actions: {
    addEmpty() {
      this.items.push({
        id: uid(),
        name: '',
        templateName: '',
        schedule: { freq: 'daily', dow: 'Mon', dom: '1', time: '09:00' },
        sendEmail: false,
        sendTelegram: false,
        telegramGroupKey: 'reports',
      })
    },
    remove(id) {
      this.items = this.items.filter(r => r.id !== id)
    },
    update(id, patch) {
      const i = this.items.findIndex(r => r.id === id)
      if (i !== -1) this.items[i] = { ...this.items[i], ...patch }
    },
    updateSchedule(id, schedPatch) {
      const i = this.items.findIndex(r => r.id === id)
      if (i !== -1) this.items[i].schedule = { ...this.items[i].schedule, ...schedPatch }
    },
  },
})

