'use client';
import React, { useState, useEffect } from 'react';
import { getTasks, updateTask, deleteTask } from '../../services/task.service';

interface Task {
  id: string;
  title: string;
  description: string;
  status: 'todo' | 'in_progress' | 'done';
  due_date: string;
}

const TaskList: React.FC = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchTasks();
  }, []);

  const fetchTasks = async () => {
    try {
      setLoading(true);
      const fetchedTasks = await getTasks();
      setTasks(fetchedTasks);
      setLoading(false);
    } catch (err) {
      setError('Failed to fetch tasks. Please try again.');
      setLoading(false);
    }
  };

  const handleStatusChange = async (taskId: string, newStatus: Task['status']) => {
    try {
      await updateTask(taskId, { status: newStatus });
      setTasks(tasks.map(task => 
        task.id === taskId ? { ...task, status: newStatus } : task
      ));
    } catch (err) {
      setError('Failed to update task status. Please try again.');
    }
  };

  const handleDeleteTask = async (taskId: string) => {
    try {
      await deleteTask(taskId);
      setTasks(tasks.filter(task => task.id !== taskId));
    } catch (err) {
      setError('Failed to delete task. Please try again.');
    }
  };

  if (loading) return <div>Loading tasks...</div>;
  if (error) return <div className="text-red-500">{error}</div>;

  return (
    <div>
      {tasks.map((task) => (
        <div key={task.id} className="mb-4 p-4 border rounded">
          <h3 className="text-xl font-bold">{task.title}</h3>
          <p className="mt-2">{task.description}</p>
          <p className="mt-2">Status: {task.status}</p>
          <p className="mt-2">Due: {new Date(task.due_date).toLocaleDateString()}</p>
          <div className="mt-4">
            <button
              onClick={() => handleStatusChange(task.id, 'in_progress')}
              className="mr-2 px-4 py-2 bg-blue-500 text-white rounded"
            >
              Start
            </button>
            <button
              onClick={() => handleStatusChange(task.id, 'done')}
              className="mr-2 px-4 py-2 bg-green-500 text-white rounded"
            >
              Complete
            </button>
            <button
              onClick={() => handleDeleteTask(task.id)}
              className="px-4 py-2 bg-red-500 text-white rounded"
            >
              Delete
            </button>
          </div>
        </div>
      ))}
    </div>
  );
};

export default TaskList;
