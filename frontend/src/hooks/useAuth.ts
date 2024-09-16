import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { login, logout, checkAuthStatus, User } from '../services/auth.service';

export function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    async function checkAuth() {
      const user = await checkAuthStatus();
      setUser(user);
      setLoading(false);
    }
    checkAuth();
  }, []);

  const loginUser = async (username: string, password: string) => {
    try {
      const response = await login(username, password);
      localStorage.setItem('token', response.access_token);
      const user = await checkAuthStatus();
      setUser(user);
      router.push('/');
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  };

  const logoutUser = async () => {
    await logout();
    setUser(null);
    router.push('/login');
  };

  return { user, loading, login: loginUser, logout: logoutUser };
}
