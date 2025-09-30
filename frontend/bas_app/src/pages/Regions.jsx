import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { MapPinIcon, TrophyIcon, ChartBarIcon } from '@heroicons/react/24/outline';
import api from '../services/api';
import { useStore } from '../store/useStore';

const Regions = () => {
  const dateRange = useStore((state) => state.dateRange);
  const [selectedRegion, setSelectedRegion] = useState(null);

  const { data: regions, isLoading } = useQuery(
    ['regions-rating', dateRange],
    async () => {
      const params = new URLSearchParams({
        start_date: dateRange.start,
        end_date: dateRange.end,
        limit: 20,
      });
      const { data } = await api.get(`/regions/rating?${params}`);
      return data;
    }
  );

  const { data: regionDetails } = useQuery(
    ['region-details', selectedRegion, dateRange],
    async () => {
      if (!selectedRegion) return null;
      const params = new URLSearchParams({
        start_date: dateRange.start,
        end_date: dateRange.end,
      });
      const { data } = await api.get(`/regions/${selectedRegion}/statistics?${params}`);
      return data;
    },
    {
      enabled: !!selectedRegion,
    }
  );

  const getMedalColor = (position) => {
    if (position === 1) return 'text-yellow-500';
    if (position === 2) return 'text-gray-400';
    if (position === 3) return 'text-orange-600';
    return 'text-gray-300';
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Региональная статистика</h2>
        <p className="mt-1 text-sm text-gray-600">
          Рейтинг субъектов РФ по полетной активности БАС
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Таблица рейтинга */}
        <div className="lg:col-span-2 bg-white shadow rounded-lg overflow-hidden">
          <div className="px-4 py-5 sm:px-6 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">
              Рейтинг регионов
            </h3>
          </div>
          
          {isLoading ? (
            <div className="p-8 text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Позиция
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Регион
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Полетов
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Время (ч)
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Операторов
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {regions?.map((region) => (
                    <tr
                      key={region.position}
                      className="hover:bg-gray-50 cursor-pointer"
                      onClick={() => setSelectedRegion(region.region)}
                    >
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          {region.position <= 3 ? (
                            <TrophyIcon className={`h-5 w-5 ${getMedalColor(region.position)}`} />
                          ) : (
                            <span className="text-gray-500 text-sm">{region.position}</span>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <MapPinIcon className="h-4 w-4 text-gray-400 mr-2" />
                          <span className="font-medium text-gray-900">{region.region}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="text-lg font-semibold text-blue-600">
                          {region.flight_count}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-gray-600">
                        {Math.round(region.total_duration_hours)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-gray-600">
                        {region.unique_operators}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Детали выбранного региона */}
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            {selectedRegion ? `Детали: ${selectedRegion}` : 'Выберите регион'}
          </h3>
          
          {regionDetails ? (
            <div className="space-y-4">
              <div className="border-b pb-4">
                <p className="text-sm text-gray-500">Всего полетов</p>
                <p className="text-2xl font-bold text-gray-900">
                  {regionDetails.total_flights}
                </p>
              </div>
              
              <div className="border-b pb-4">
                <p className="text-sm text-gray-500">Общее время полетов</p>
                <p className="text-xl font-semibold text-gray-900">
                  {Math.round(regionDetails.total_duration_hours)} ч
                </p>
              </div>
              
              <div className="border-b pb-4">
                <p className="text-sm text-gray-500">Уникальных операторов</p>
                <p className="text-xl font-semibold text-gray-900">
                  {regionDetails.unique_operators}
                </p>
              </div>
              
              <div className="border-b pb-4">
                <p className="text-sm text-gray-500">Типов БВС</p>
                <p className="text-xl font-semibold text-gray-900">
                  {regionDetails.unique_uav_types}
                </p>
              </div>
              
              <div className="border-b pb-4">
                <p className="text-sm text-gray-500">Пиковый час</p>
                <p className="text-xl font-semibold text-gray-900">
                  {regionDetails.peak_hour}:00
                </p>
                <p className="text-sm text-gray-500">
                  {regionDetails.peak_hour_flights} полетов
                </p>
              </div>
              
              <div>
                <p className="text-sm text-gray-500">Среднее в день</p>
                <p className="text-xl font-semibold text-gray-900">
                  {regionDetails.avg_flights_per_day?.toFixed(1)} полетов
                </p>
              </div>
            </div>
          ) : (
            <div className="text-center py-12 text-gray-500">
              <MapPinIcon className="h-12 w-12 mx-auto mb-4 text-gray-300" />
              <p>Выберите регион из таблицы</p>
              <p className="text-sm mt-2">для просмотра детальной статистики</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Regions;