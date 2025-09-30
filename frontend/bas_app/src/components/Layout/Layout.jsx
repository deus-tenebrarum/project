import React from 'react';
import Header from './Header';
import Sidebar from './Sidebar';
import DateFilter from '../common/DateFilter';

const Layout = ({ children }) => {
  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <div className="flex">
        <Sidebar />
        <main className="flex-1">
          <DateFilter />
          <div className="p-6">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
};

export default Layout;