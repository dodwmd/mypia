import create from 'zustand';
import { persist } from 'zustand/middleware';

interface User {
  id: string;
  username: string;
  email: string;
}

interface Settings {
  language: string;
  theme: 'light' | 'dark' | 'system';
  notifications: boolean;
  emailFrequency: 'daily' | 'weekly' | 'monthly';
  aiModel: string;
  privacyLevel: 'high' | 'balanced' | 'low';
}

interface AppState {
  user: User | null;
  settings: Settings;
  isAuthenticated: boolean;
  isDarkMode: boolean;
  setUser: (user: User | null) => void;
  setSettings: (settings: Partial<Settings>) => void;
  setIsAuthenticated: (isAuthenticated: boolean) => void;
  toggleDarkMode: () => void;
  logout: () => void;
  notifications: Notification[];
  addNotification: (notification: Omit<Notification, 'id' | 'read' | 'createdAt'>) => void;
  markNotificationAsRead: (id: string) => void;
  clearNotifications: () => void;
}

export interface Notification {
  id: string;
  title: string;
  message: string;
  type: 'info' | 'success' | 'warning' | 'error';
  read: boolean;
  createdAt: Date;
}

const useStore = create<AppState>()(
  persist(
    (set) => ({
      user: null,
      settings: {
        language: 'en',
        theme: 'system',
        notifications: true,
        emailFrequency: 'daily',
        aiModel: 'gpt-3.5-turbo',
        privacyLevel: 'balanced',
      },
      isAuthenticated: false,
      isDarkMode: false,
      setUser: (user) => set({ user }),
      setSettings: (newSettings) =>
        set((state) => ({ settings: { ...state.settings, ...newSettings } })),
      setIsAuthenticated: (isAuthenticated) => set({ isAuthenticated }),
      toggleDarkMode: () => set((state) => ({ isDarkMode: !state.isDarkMode })),
      logout: () => set({ user: null, isAuthenticated: false }),
      notifications: [],
      addNotification: (notification) =>
        set((state) => ({
          notifications: [
            {
              ...notification,
              id: Date.now().toString(),
              read: false,
              createdAt: new Date(),
            },
            ...state.notifications,
          ],
        })),
      markNotificationAsRead: (id) =>
        set((state) => ({
          notifications: state.notifications.map((n) =>
            n.id === id ? { ...n, read: true } : n
          ),
        })),
      clearNotifications: () => set({ notifications: [] }),
    }),
    {
      name: 'mypia-storage',
      getStorage: () => localStorage,
    }
  )
);

export default useStore;
