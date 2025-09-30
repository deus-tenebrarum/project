import React from 'react';
import { PaperAirplaneIcon, BellIcon, UserCircleIcon } from '@heroicons/react/24/outline';
import { useStore } from '../../store/useStore';

const Header = () => {
  const user = useStore((state) => state.user);

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center">
            <PaperAirplaneIcon className="h-8 w-8 text-blue-600 mr-3" />
            <div>
              <h1 className="text-xl font-semibold text-gray-900">
                Система анализа полетов БАС
              </h1>
              <p className="text-xs text-gray-500">Росавиация • ЕС ОрВД</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            <button className="p-2 text-gray-400 hover:text-gray-600">
              <BellIcon className="h-6 w-6" />
            </button>
            <div className="flex items-center space-x-2">
              <UserCircleIcon className="h-8 w-8 text-gray-400" />
              <span className="text-sm text-gray-700">{user?.name || 'Оператор'}</span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;