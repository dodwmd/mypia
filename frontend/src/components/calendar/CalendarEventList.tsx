'use client';
import React, { useState, useEffect } from 'react';
import { Calendar, momentLocalizer } from 'react-big-calendar';
import moment from 'moment';
import 'react-big-calendar/lib/css/react-big-calendar.css';
import { getCalendarEvents, CalendarEvent } from '../../services/calendar.service';

// Setup the localizer for react-big-calendar
const localizer = momentLocalizer(moment);

const CalendarEventList: React.FC = () => {
    const [events, setEvents] = useState<CalendarEvent[]>([]);

  useEffect(() => {
    fetchEvents();
  }, []);

  const fetchEvents = async () => {
    try {
      const fetchedEvents = await getCalendarEvents();
      setEvents(fetchedEvents);
    } catch (error) {
      console.error('Error fetching calendar events:', error);
    }
  };

  return (
    <div className="h-screen p-4">
      <h2 className="text-2xl font-bold mb-4">Calendar</h2>
      <Calendar
        localizer={localizer}
        events={events}
        startAccessor="start"
        endAccessor="end"
        style={{ height: 'calc(100% - 80px)' }}
        views={['month', 'week', 'day']}
        defaultView='month'
      />
    </div>
  );
};

export default CalendarEventList;
