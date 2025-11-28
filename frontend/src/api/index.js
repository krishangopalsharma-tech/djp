import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1', // Assuming your Django backend serves API at /api/v1
  headers: {
    'Content-Type': 'application/json',
  },
})

export default api
