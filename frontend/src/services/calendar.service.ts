import api from '../utils/api';

export interface CalendarEvent {
  id: string;
  title: string;
  start: Date;
  end: Date;
  description?: string;
}

export async function getCalendarEvents(): Promise<CalendarEvent[]> {
  try {
    const response = await api.get<{ events: CalendarEvent[] }>('/v1/calendar/events');
    return response.data.events.map(event => ({
      ...event,
      start: new Date(event.start),
      end: new Date(event.end)
    }));
  } catch (error) {
    console.error('Error fetching calendar events:', error);
    throw error;
  }
}

export async function createCalendarEvent(event: Omit<CalendarEvent, 'id'>): Promise<CalendarEvent> {
  try {
    const response = await api.post<{ event: CalendarEvent }>('/v1/calendar/events', {
      ...event,
      start: event.start.toISOString(),
      end: event.end.toISOString()
    });
    return {
      ...response.data.event,
      start: new Date(response.data.event.start),
      end: new Date(response.data.event.end)
    };
  } catch (error) {
    console.error('Error creating calendar event:', error);
    throw error;
  }
}
