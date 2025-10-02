import axios from 'axios';

// This creates an Axios instance that will correctly use the Vite proxy
// and handle Django's CSRF tokens automatically.
export const http = axios.create({
  baseURL: '/api/v1',
  timeout: 35000,
  withCredentials: true,
  xsrfCookieName: 'csrftoken',
  xsrfHeaderName: 'X-CSRFToken',
});

// Optional interceptor placeholders
http.interceptors.response.use(
  (r) => r,
  (err) => Promise.reject(err)
);