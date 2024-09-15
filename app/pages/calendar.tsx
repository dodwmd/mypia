import React from 'react';
import Layout from '../components/Layout';
import Calendar from '../components/Calendar';

const CalendarPage: React.FC = () => {
  return (
    <Layout>
      <div className="h-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h1 className="text-3xl font-bold mb-6 text-secondary-900 font-display">Calendar</h1>
        <div className="h-[calc(100vh-12rem)]">
          <Calendar />
        </div>
      </div>
    </Layout>
  );
};

export default CalendarPage;
