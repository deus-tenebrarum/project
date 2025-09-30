import React from 'react';
import { CalendarIcon } from '@heroicons/react/24/outline';
import { useStore } from '../../store/useStore';

const DateFilter = () => {
  const { dateRange, setDateRange } = useStore();

  const handleDateChange = (field, value) => {
    setDateRange({
      ...dateRange,
      [field]: value,
    });
  };

  return (
    <div className="bg-white border-b border-gray-200 px-6 py-3">
      <div className="flex items-center space-x-4">
        <CalendarIcon className="h-5 w-5 text-gray-400" />
        <input
          type="date"
          value={dateRange.start}
          onChange={(e) => handleDateChange('start', e.target.value)}
          className="px-3 py-1.5 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <span className="text-gray-500">—</span>
        <input
          type="date"
          value={dateRange.end}
          onChange={(e) => handleDateChange('end', e.target.value)}
          className="px-3 py-1.5 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button className="px-4 py-1.5 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700">
          Применить
        </button>
      </div>
    </div>
  );
};

export default DateFilter;