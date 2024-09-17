import api from '../utils/api';

export interface Email {
  id: string;
  subject: string;
  sender: string;
  recipient: string;
  body: string;
  date: string;
  preview: string;  // Add this line
}

export interface EmailToSend {
  to: string;
  subject: string;
  body: string;
}

export async function getEmails(): Promise<Email[]> {
  try {
    const response = await api.get<{ emails: Email[] }>('/v1/emails');
    return response.data.emails.map(email => ({
      ...email,
      preview: email.body.substring(0, 100) + '...'  // Generate preview from body
    }));
  } catch (error) {
    console.error('Error fetching emails:', error);
    throw error;
  }
}

export async function sendEmail(email: EmailToSend): Promise<void> {
  try {
    await api.post('/v1/emails/send', email);
  } catch (error) {
    console.error('Error sending email:', error);
    throw error;
  }
}
