import { useQuery, useMutation, useQueryClient } from 'react-query';
import api from '../services/api';
import { useStore } from '../store/useStore';

export const useFlights = () => {
  const dateRange = useStore((state) => state.dateRange);
  
  return useQuery(
    ['flights', dateRange],
    async () => {
      const params = new URLSearchParams({
        start_date: dateRange.start,
        end_date: dateRange.end,
      });
      const { data } = await api.get(`/flights?${params}`);
      return data;
    },
    {
      staleTime: 5 * 60 * 1000, // 5 минут
    }
  );
};

export const useFlightStatistics = () => {
  const dateRange = useStore((state) => state.dateRange);
  const setStatistics = useStore((state) => state.setStatistics);
  
  return useQuery(
    ['statistics', dateRange],
    async () => {
      const params = new URLSearchParams({
        start_date: dateRange.start,
        end_date: dateRange.end,
      });
      const { data } = await api.get(`/flights/statistics?${params}`);
      setStatistics(data);
      return data;
    }
  );
};

export const useUploadFlights = () => {
  const queryClient = useQueryClient();
  
  return useMutation(
    ({ file, type }) => {
      const formData = new FormData();
      formData.append('file', file);
      const endpoint = type === 'excel' ? '/flights/upload/excel' : '/flights/upload/shr';
      return api.post(endpoint, formData);
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries('flights');
        queryClient.invalidateQueries('statistics');
      },
    }
  );
};
