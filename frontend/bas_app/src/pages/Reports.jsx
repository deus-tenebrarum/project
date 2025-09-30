import React, { useState } from 'react';
import { useMutation } from 'react-query';
import toast from 'react-hot-toast';
import {
  DocumentTextIcon,
  ChartBarIcon,
  TableCellsIcon,
  ArrowDownTrayIcon,
  CalendarIcon,
} from '@heroicons/react/24/outline';
import api from '../services/api';
import { useStore } from '../store/useStore';

const Reports = () => {
  const dateRange = useStore((state) => state.dateRange);
  const [selectedRegions, setSelectedRegions] = useState([]);
  const [reportType, setReportType] = useState('json');

  const generateReport = useMutation(
    (params) => api.post('/reports/generate', params),
    {
      onSuccess: (data) => {
        toast.success('Отчет успешно сгенерирован');
        // В реальном приложении здесь был бы код для скачивания файла
        console.log('Report generated:', data.data);
      },
      onError: () => {
        toast.error('Ошибка генерации отчета');
      },
    }
  );

  const reportTypes = [
    {
      id: 'json',
      name: 'JSON отчет',
      description: 'Структурированные данные для интеграции с другими системами',
      icon: DocumentTextIcon,
      color: 'blue',
    },
    {
      id: 'png',
      name: 'Графический отчет',
      description: 'Визуализация статистики в формате PNG',
      icon: ChartBarIcon,
      color: 'green',
    },
    {
      id: 'xlsx',
      name: 'Excel таблица',
      description: 'Детальный отчет с возможностью дополнительного анализа',
      icon: TableCellsIcon,
      color: 'purple',
    },
  ];

  const handleGenerateReport = (format) => {
    generateReport.mutate({
      format,
      start_date: dateRange.start,
      end_date: dateRange.end,
      regions: selectedRegions.length > 0 ? selectedRegions : undefined,
      chart_type: format === 'png' ? 'bar' : undefined,
    });
  };

  const predefinedReports = [
    {
      name: 'Ежемесячный отчет',
      description: 'Стандартный отчет за месяц',
      action: () => {
        const date = new Date();
        const firstDay = new Date(date.getFullYear(), date.getMonth(), 1);
        const lastDay = new Date(date.getFullYear(), date.getMonth() + 1, 0);
        
        generateReport.mutate({
          format: 'xlsx',
          start_date: firstDay.toISOString().split('T')[0],
          end_date: lastDay.toISOString().split('T')[0],
        });
      },
    },
    {
      name: 'Квартальный анализ',
      description: 'Детальный анализ за квартал',
      action: () => {
        const date = new Date();
        const quarter = Math.floor(date.getMonth() / 3);
        const firstMonth = quarter * 3;
        const firstDay = new Date(date.getFullYear(), firstMonth, 1);
        const lastDay = new Date(date.getFullYear(), firstMonth + 3, 0);
        
        generateReport.mutate({
          format: 'json',
          start_date: firstDay.toISOString().split('T')[0],
          end_date: lastDay.toISOString().split('T')[0],
        });
      },
    },
    {
      name: 'Топ-10 регионов',
      description: 'Рейтинг регионов по активности',
      action: () => {
        generateReport.mutate({
          format: 'png',
          start_date: dateRange.start,
          end_date: dateRange.end,
          chart_type: 'bar',
        });
      },
    },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Генерация отчетов</h2>
        <p className="mt-1 text-sm text-gray-600">
          Создание отчетов и экспорт данных для анализа
        </p>
      </div>

      {/* Период отчета */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          Параметры отчета
        </h3>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Период
            </label>
            <div className="flex items-center space-x-2 text-sm">
              <CalendarIcon className="h-5 w-5 text-gray-400" />
              <span className="font-medium">
                {new Date(dateRange.start).toLocaleDateString('ru-RU')}
              </span>
              <span className="text-gray-500">—</span>
              <span className="font-medium">
                {new Date(dateRange.end).toLocaleDateString('ru-RU')}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Типы отчетов */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          Выберите формат отчета
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {reportTypes.map((report) => (
            <div
              key={report.id}
              className="border rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
              onClick={() => setReportType(report.id)}
            >
              <div className={`inline-flex p-3 rounded-lg bg-${report.color}-100 mb-3`}>
                <report.icon className={`h-6 w-6 text-${report.color}-600`} />
              </div>
              <h4 className="font-medium text-gray-900">{report.name}</h4>
              <p className="text-sm text-gray-600 mt-1">{report.description}</p>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  handleGenerateReport(report.id);
                }}
                disabled={generateReport.isLoading}
                className={`mt-4 w-full px-4 py-2 bg-${report.color}-600 text-white rounded-md hover:bg-${report.color}-700 transition-colors text-sm font-medium disabled:opacity-50`}
              >
                {generateReport.isLoading ? (
                  <span className="flex items-center justify-center">
                    <svg className="animate-spin h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                    </svg>
                    Генерация...
                  </span>
                ) : (
                  <span className="flex items-center justify-center">
                    <ArrowDownTrayIcon className="h-4 w-4 mr-2" />
                    Сгенерировать
                  </span>
                )}
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Готовые шаблоны */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          Готовые шаблоны отчетов
        </h3>
        <div className="space-y-3">
          {predefinedReports.map((template, index) => (
            <div
              key={index}
              className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50"
            >
              <div>
                <h4 className="font-medium text-gray-900">{template.name}</h4>
                <p className="text-sm text-gray-600">{template.description}</p>
              </div>
              <button
                onClick={template.action}
                disabled={generateReport.isLoading}
                className="px-4 py-2 text-sm font-medium text-blue-600 hover:text-blue-700 disabled:opacity-50"
              >
                Создать
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Reports;