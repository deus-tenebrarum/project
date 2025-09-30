import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  HomeIcon,
  CloudArrowUpIcon,
  MapIcon,
  DocumentChartBarIcon,
  Cog6ToothIcon,
} from '@heroicons/react/24/outline';

const navigation = [
  { name: 'Аналитика', href: '/dashboard', icon: HomeIcon },
  { name: 'Загрузка данных', href: '/upload', icon: CloudArrowUpIcon },
  { name: 'Регионы', href: '/regions', icon: MapIcon },
  { name: 'Отчеты', href: '/reports', icon: DocumentChartBarIcon },
  { name: 'Настройки', href: '/settings', icon: Cog6ToothIcon },
];

const Sidebar = () => {
  return (
    <aside className="w-64 bg-white shadow-sm min-h-screen">
      <nav className="px-2 py-4 space-y-1">
        {navigation.map((item) => (
          <NavLink
            key={item.name}
            to={item.href}
            className={({ isActive }) =>
              `group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                isActive
                  ? 'bg-blue-50 text-blue-700'
                  : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'
              }`
            }
          >
            <item.icon className="mr-3 h-5 w-5" />
            {item.name}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
};

export default Sidebar;