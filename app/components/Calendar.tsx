import React, { useState } from 'react';
import { Calendar as BigCalendar, momentLocalizer, Views } from 'react-big-calendar';
import moment from 'moment';
import 'react-big-calendar/lib/css/react-big-calendar.css';

// Setup the localizer for BigCalendar
const localizer = momentLocalizer(moment);

interface Event {
  id: number;
  title: string;
  start: Date;
  end: Date;
}

const Calendar: React.FC = () => {
  const [view, setView] = useState(Views.MONTH);
  const [date, setDate] = useState(new Date());

  // Sample events (replace with your actual events data)
  const [events] = useState<Event[]>([
    {
      id: 1,
      title: 'Meeting with Client',
      start: new Date(2023, 4, 15, 10, 0),
      end: new Date(2023, 4, 15, 11, 0),
    },
    {
      id: 2,
      title: 'Team Lunch',
      start: new Date(2023, 4, 16, 12, 0),
      end: new Date(2023, 4, 16, 13, 0),
    },
  ]);

  const handleNavigate = (newDate: Date) => setDate(newDate);
  const handleViewChange = (newView: string) => setView(newView);

  return (
    <div className="h-full">
      <BigCalendar
        localizer={localizer}
        events={events}
        startAccessor="start"
        endAccessor="end"
        view={view}
        onView={handleViewChange}
        date={date}
        onNavigate={handleNavigate}
        className="bg-white shadow-lg rounded-lg overflow-hidden"
        // Custom styling
        formats={{
          monthHeaderFormat: 'MMMM YYYY',
          weekdayFormat: 'ddd',
          dayHeaderFormat: 'dddd, MMMM D',
        }}
        // Custom components
        components={{
          toolbar: CustomToolbar,
          event: CustomEvent,
        }}
      />
    </div>
  );
};

// Custom toolbar component
const CustomToolbar: React.FC<any> = (toolbar) => {
  const goToBack = () => {
    toolbar.onNavigate('PREV');
  };

  const goToNext = () => {
    toolbar.onNavigate('NEXT');
  };

  const goToCurrent = () => {
    toolbar.onNavigate('TODAY');
  };

  return (
    <div className="flex justify-between items-center p-4 bg-primary-600 text-white">
      <div>
        <button onClick={goToBack} className="mr-2 px-3 py-1 rounded hover:bg-primary-700 transition">
          &lt;
        </button>
        <button onClick={goToNext} className="px-3 py-1 rounded hover:bg-primary-700 transition">
          &gt;
        </button>
      </div>
      <h2 className="text-xl font-semibold">{toolbar.label}</h2>
      <div>
        <button onClick={goToCurrent} className="mr-2 px-3 py-1 rounded hover:bg-primary-700 transition">
          Today
        </button>
        <select
          value={toolbar.view}
          onChange={(e) => toolbar.onView(e.target.value)}
          className="bg-primary-600 border border-primary-400 rounded px-2 py-1"
        >
          <option value="month">Month</option>
          <option value="week">Week</option>
          <option value="day">Day</option>
        </select>
      </div>
    </div>
  );
};

// Custom event component
const CustomEvent: React.FC<any> = ({ event }) => (
  <div className="p-1 bg-accent-500 text-white rounded">
    <strong>{event.title}</strong>
  </div>
);

export default Calendar;
