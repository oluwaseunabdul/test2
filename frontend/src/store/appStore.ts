import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface AppState {
  theme: 'light' | 'dark';
  toggleTheme: () => void;
  currentProject: number | null;
  setCurrentProject: (id: number | null) => void;
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      theme: 'light',
      toggleTheme: () => set((state) => ({ 
        theme: state.theme === 'light' ? 'dark' : 'light' 
      })),
      currentProject: null,
      setCurrentProject: (id) => set({ currentProject: id }),
    }),
    {
      name: 'app-storage',
    }
  )
);
