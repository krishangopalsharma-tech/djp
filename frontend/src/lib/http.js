import axios from 'axios'

// Read from env; fallback to same-origin /api
const baseURL = import.meta.env.VITE_API_BASE_URL || '/api'

export const http = axios.create({
  baseURL,
  timeout: 15000,
})

// Optional interceptor placeholders
http.interceptors.response.use(
  (r) => r,
  (err) => Promise.reject(err)
)
