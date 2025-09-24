import axios from 'axios';

// This creates an Axios instance that will correctly use the Vite proxy.
// All requests to '/api/...' will be automatically forwarded to your backend.
export const http = axios.create({
  baseURL: '/api/v1', // This must include the '/v1' part
  timeout: 15000,
});

// Optional interceptor placeholders
http.interceptors.response.use(
  (r) => r,
  (err) => Promise.reject(err)
);