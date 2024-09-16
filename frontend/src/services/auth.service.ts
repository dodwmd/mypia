import api from '../utils/api';

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface User {
  id: string;
  username: string;
  email: string;
}

export async function login(username: string, password: string): Promise<LoginResponse> {
  try {
    const response = await api.post<LoginResponse>('/auth/token', { username, password });
    return response.data;
  } catch (error) {
    console.error('Login failed:', error);
    throw error;
  }
}

export async function register(username: string, email: string, password: string): Promise<void> {
  try {
    await api.post('/auth/register', { username, email, password });
  } catch (error) {
    console.error('Registration failed:', error);
    throw error;
  }
}

export async function logout(): Promise<void> {
  localStorage.removeItem('token');
}

export async function checkAuthStatus(): Promise<User | null> {
  const token = localStorage.getItem('token');
  if (!token) {
    return null;
  }

  try {
    const response = await api.get<User>('/user/info');
    return response.data;
  } catch (error) {
    console.error('Failed to check auth status:', error);
    localStorage.removeItem('token');
    return null;
  }
}
