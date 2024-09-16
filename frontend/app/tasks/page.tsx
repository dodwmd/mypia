'use client';

import React, { useState } from 'react';
import TaskList from '../../src/components/tasks/TaskList';
import TaskCreator from '../../src/components/tasks/TaskCreator';

export default function TasksPage() {
  const [refreshKey, setRefreshKey] = useState(0);

  const handleTaskCreated = () => {
    setRefreshKey(prev => prev + 1);
  };

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-3xl mb-8">Tasks</h1>
      <div className="bg-white shadow-md rounded-lg p-6 mb-8">
        <h2 className="text-xl mb-4">Create New Task</h2>
        <TaskCreator onTaskCreated={handleTaskCreated} />
      </div>
      <div className="bg-white shadow-md rounded-lg p-6">
        <h2 className="text-xl mb-4">Task List</h2>
        <TaskList key={refreshKey} />
      </div>
    </div>
  );
}
