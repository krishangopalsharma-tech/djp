import { defineStore } from 'pinia'

export const useAppStore = defineStore('app', {
  state: () => ({
    appName: 'Railway Failure System',
  }),
  actions: {
    setAppName(name) { this.appName = name }
  }
})
