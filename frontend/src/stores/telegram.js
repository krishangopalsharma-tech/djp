// src/stores/telegram.js
import { defineStore } from 'pinia'

export const useTelegramStore = defineStore('telegram', {
  state: () => ({
    groups: {
      alert:   { key: 'alert',   name: 'Alert Group',        chat_id: '', link: '' },
      files:   { key: 'files',   name: 'File Upload Group',  chat_id: '', link: '' },
      reports: { key: 'reports', name: 'Reports Group',      chat_id: '', link: '' },
    },
  }),
  getters: {
    list: (s) => Object.values(s.groups),
  },
  actions: {
    rename(key, name) { if (this.groups[key]) this.groups[key].name = name },
    setChatId(key, chat_id) { if (this.groups[key]) this.groups[key].chat_id = chat_id },
    setLink(key, link) { if (this.groups[key]) this.groups[key].link = link },
  },
})
