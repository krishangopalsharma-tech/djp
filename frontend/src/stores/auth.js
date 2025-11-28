import { defineStore } from 'pinia'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,   // { username }
    token: null,  // placeholder until backend
  }),
  actions: {
    initFromStorage() {
      const token = localStorage.getItem('auth_token')
      const userRaw = localStorage.getItem('auth_user')
      if (token) this.token = token
      if (userRaw) this.user = JSON.parse(userRaw)
    },
    async login({ username, password }) {
      if (!username || !password) throw new Error('Missing credentials')
      // Mock success; later replace with real API call
      this.user = { username }
      this.token = 'dev-token'
      localStorage.setItem('auth_token', this.token)
      localStorage.setItem('auth_user', JSON.stringify(this.user))
    },
    logout() {
      this.user = null
      this.token = null
      localStorage.removeItem('auth_token')
      localStorage.removeItem('auth_user')
    }
  }
})
