import React from 'react';
import { useQuery } from 'react-query';
import {
  PaperAirplaneIcon,
  ClockIcon,
  UsersIcon,
  CubeIcon,
  TrendingUpIcon,
  MapPinIcon,
} from '@heroicons/react/24/outline';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import api from '../services/api';
import { useStore } from '../store/useStore';
import StatCard from '../components/common/StatCard';

const Dashboard = () => {
  const dateRange = useStore((state) => state.dateRange);

  const { data: statistics, isLoading: statsLoading } = useQuery(
    ['statistics', dateRange],
    async () => {
      const params = new URLSearchParams({
        start_date: dateRange.start,
        end_date: dateRange.end,
      });
      const { data } = await api.get(`/flights/statistics?${params}`);
      return data;
    }
  );

  const { data: chartData } = useQuery(
    ['chart-data', dateRange],
    async () => {
      // Симуляция данных для графиков
      return {
        daily: [
          { date: '01.09', flights: 45 },
          { date: '02.09', flights: 52 },
          { date: '03.09', flights: 38 },
          { date: '04.09', flights: 65 },
          { date: '05.09', flights: 48 },
          { date: '06.09', flights: 71 },
          { date: '07.09', flights: 55 },
        ],
        regions: [
          { name: 'Москва', value: 450, color: '#3B82F6' },
          { name: 'СПб', value: 380, color: '#10B981' },
          { name: 'Красноярск', value: 210, color: '#F59E0B' },
          { name: 'Тюмень', value: 180, color: '#8B5CF6' },
          { name: 'Другие', value: 280, color: '#EF4444' },
        ],
        hourly: Array.from({ length: 24 }, (_, i) => ({
          hour: `${i}:00`,
          flights: Math.floor(Math.random() * 20) + 5,
        })),
      };
    }
  );

  const stats = [
    {
      title: 'Всего полетов',
      value: statistics?.total_flights || 0,
      icon: PaperAirplaneIcon,
      color: 'blue',
      trend: '+12%',
    },
    {
      title: 'Средняя длительность',
      value: `${Math.round(statistics?.avg_duration_minutes || 0)} мин`,
      icon: ClockIcon,
      color: 'green',
      trend: '+5%',
    },
    {
      title: 'Операторов',
      value: statistics?.unique_operators || 0,
      icon: UsersIcon,
      color: 'purple',
      trend: '+8%',
    },
    {
      title: 'Типов БВС',
      value: statistics?.unique_uav_types || 0,
      icon: CubeIcon,
      color: 'orange',
      trend: '+3%',
    },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Аналитическая панель</h2>
        <p className="mt-1 text-sm text-gray-600">
          Обзор полетной активности БАС за выбранный период
        </p>
      </div>

      {/* Карточки статистики */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => (
          <StatCard key={stat.title} {...stat} loading={statsLoading} />
        ))}
      </div>

      {/* Графики */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Динамика по дням */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Динамика полетов
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData?.daily || []}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Line
                type="monotone"
                dataKey="flights"
                stroke="#3B82F6"
                strokeWidth={2}
                dot={{ r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Распределение по регионам */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Топ регионов
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={chartData?.regions || []}
                cx="50%"
                cy="50%"
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
              >
                {chartData?.regions?.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Почасовая активность */}
        <div className="bg-white p-6 rounded-lg shadow lg:col-span-2">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Распределение полетов по часам
          </h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={chartData?.hourly || []}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="hour" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="flights" fill="#10B981" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
