// frontend/src/stores/email.js
import { defineStore } from 'pinia'

export const useEmailStore = defineStore('email', {
  state: () => ({
    smtp: {
      host: '',
      port: 587,
      encryption: 'STARTTLS', // 'STARTTLS' | 'SSL/TLS' | 'None'
      username: '',
      password: '',
      fromName: 'RFMS Notifications',
      fromAddress: 'no-reply@example.com',
    },
    // Default recipients for automatic emails (To/CC/BCC)
    recipients: {
      to: ['ops@example.com'],
      cc: [],
      bcc: [],
    },
    test: { to: '' }, // for “Send Test Email”
  }),
  actions: {
    updateSMTP(patch) { this.smtp = { ...this.smtp, ...patch } },
    addRecipient(kind, email) {
      if (!email) return
      if (!this.recipients[kind]) this.recipients[kind] = []
      if (!this.recipients[kind].includes(email)) this.recipients[kind].push(email)
    },
    removeRecipient(kind, email) {
      if (!this.recipients[kind]) return
      this.recipients[kind] = this.recipients[kind].filter(x => x !== email)
    },
  },
})

