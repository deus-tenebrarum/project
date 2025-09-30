import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

const useStore = create(
  devtools(
    persist(
      (set) => ({
        // Пользователь
        user: null,
        setUser: (user) => set({ user }),
        
        // Фильтры дат
        dateRange: {
          start: new Date().toISOString().split('T')[0],
          end: new Date().toISOString().split('T')[0],
        },
        setDateRange: (dateRange) => set({ dateRange }),
        
        // Статистика
        statistics: {
          totalFlights: 0,
          avgDuration: 0,
          uniqueOperators: 0,
          uavTypes: 0,
        },
        setStatistics: (statistics) => set({ statistics }),
        
        // Регионы
        regions: [],
        setRegions: (regions) => set({ regions }),
        
        // Настройки
        settings: {
          language: 'ru',
          theme: 'light',
          notifications: true,
        },
        updateSettings: (settings) => set((state) => ({
          settings: { ...state.settings, ...settings }
        })),
      }),
      {
        name: 'bas-storage',
      }
    )
  )
);

export { useStore };
