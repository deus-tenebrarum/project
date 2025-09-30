import React from 'react';
import { ArrowUpIcon, ArrowDownIcon } from '@heroicons/react/20/solid';

const StatCard = ({ title, value, icon: Icon, color, trend, loading }) => {
  const colors = {
    blue: 'bg-blue-100 text-blue-600',
    green: 'bg-green-100 text-green-600',
    purple: 'bg-purple-100 text-purple-600',
    orange: 'bg-orange-100 text-orange-600',
  };

  const trendPositive = trend && trend.startsWith('+');

  return (
    <div className="bg-white rounded-lg shadow p-6">
      {loading ? (
        <div className="animate-pulse">
          <div className="h-12 w-12 bg-gray-200 rounded-lg mb-4"></div>
          <div className="h-8 bg-gray-200 rounded w-1/2 mb-2"></div>
          <div className="h-4 bg-gray-200 rounded w-3/4"></div>
        </div>
      ) : (
        <>
          <div className="flex items-center justify-between mb-4">
            <div className={`p-3 rounded-lg ${colors[color]}`}>
              <Icon className="h-6 w-6" />
            </div>
            {trend && (
              <span className={`flex items-center text-sm font-medium ${
                trendPositive ? 'text-green-600' : 'text-red-600'
              }`}>
                {trendPositive ? (
                  <ArrowUpIcon className="h-4 w-4 mr-1" />
                ) : (
                  <ArrowDownIcon className="h-4 w-4 mr-1" />
                )}
                {trend}
              </span>
            )}
          </div>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
          <p className="text-sm text-gray-600 mt-1">{title}</p>
        </>
      )}
    </div>
  );
};

export default StatCard;