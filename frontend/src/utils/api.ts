import axios, { AxiosError } from 'axios';
import { isOffline } from './offline';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/v1',
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (isOffline()) {
      return Promise.reject(new Error('You are currently offline. Please check your internet connection and try again.'));
    }
    if (error.response?.status === 401) {
      // Handle unauthorized access (e.g., redirect to login)
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
