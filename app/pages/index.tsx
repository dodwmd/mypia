import React from 'react';
import Layout from '../components/Layout';
import Dashboard from '../components/Dashboard';

const Home: React.FC = () => {
  return (
    <Layout>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Dashboard />
      </div>
    </Layout>
  );
};

export default Home;
