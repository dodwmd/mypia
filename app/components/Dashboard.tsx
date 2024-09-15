import React from 'react';
import Analytics from './Analytics';

const Dashboard: React.FC = () => {
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-secondary-900 dark:text-secondary-100">Dashboard</h1>
      <Analytics />
      {/* You can add more dashboard components here */}
    </div>
  );
};

export default Dashboard;
