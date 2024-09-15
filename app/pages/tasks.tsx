import React from 'react';
import Layout from '../components/Layout';
import TaskManagement from '../components/TaskManagement';

const TasksPage: React.FC = () => {
  return (
    <Layout>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <TaskManagement />
      </div>
    </Layout>
  );
};

export default TasksPage;
