'use client';

import React from 'react';
import CalendarEventList from '../../src/components/calendar/CalendarEventList';
import CalendarEventCreator from '../../src/components/calendar/CalendarEventCreator';

export default function CalendarPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold mb-8">Calendar</h1>
      <CalendarEventList />
      <CalendarEventCreator />
    </div>
  );
}
