import React from 'react';
import { 
  LineChart, Line, BarChart, Bar, PieChart, Pie, 
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer 
} from 'recharts';

const userActivityData = [
  { date: '2023-05-01', interactions: 23 },
  { date: '2023-05-02', interactions: 45 },
  { date: '2023-05-03', interactions: 32 },
  { date: '2023-05-04', interactions: 50 },
  { date: '2023-05-05', interactions: 38 },
  { date: '2023-05-06', interactions: 42 },
  { date: '2023-05-07', interactions: 55 },
];

const aiPerformanceData = [
  { metric: 'Response Time', score: 95 },
  { metric: 'Accuracy', score: 88 },
  { metric: 'User Satisfaction', score: 92 },
  { metric: 'Task Completion', score: 85 },
];

const taskDistributionData = [
  { name: 'Email Management', value: 30 },
  { name: 'Scheduling', value: 25 },
  { name: 'Research', value: 20 },
  { name: 'Data Analysis', value: 15 },
  { name: 'Other', value: 10 },
];

const Analytics: React.FC = () => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div className="bg-white dark:bg-secondary-800 p-4 rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-4 text-secondary-900 dark:text-secondary-100">User Activity</h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={userActivityData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="interactions" stroke="#8884d8" />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="bg-white dark:bg-secondary-800 p-4 rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-4 text-secondary-900 dark:text-secondary-100">AI Assistant Performance</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={aiPerformanceData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="metric" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="score" fill="#82ca9d" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="bg-white dark:bg-secondary-800 p-4 rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-4 text-secondary-900 dark:text-secondary-100">Task Distribution</h3>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={taskDistributionData}
              dataKey="value"
              nameKey="name"
              cx="50%"
              cy="50%"
              outerRadius={80}
              fill="#8884d8"
              label
            />
            <Tooltip />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default Analytics;
