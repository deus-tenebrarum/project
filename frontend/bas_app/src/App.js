import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { Toaster } from 'react-hot-toast';
//import Settings from './pages/Settings';
//<Route path="/settings" element={<Settings />} />

import Layout from './components/Layout/Layout';
import Dashboard from './pages/Dashboard';
import Upload from './pages/Upload';
import Regions from './pages/Regions';
import Reports from './pages/Reports';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60 * 1000,
      cacheTime: 5 * 60 * 1000,
      refetchOnWindowFocus: false,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/upload" element={<Upload />} />
            <Route path="/regions" element={<Regions />} />
            <Route path="/reports" element={<Reports />} />
          </Routes>
        </Layout>
      </Router>
      <Toaster position="bottom-right" />
    </QueryClientProvider>
  );
}

export default App;