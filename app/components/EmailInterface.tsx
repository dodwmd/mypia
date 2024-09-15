import React, { useState } from 'react';

interface Email {
  id: string;
  from: string;
  subject: string;
  body: string;
  date: string;
  read: boolean;
}

const mockEmails: Email[] = [
  {
    id: '1',
    from: 'john@example.com',
    subject: 'Project Update',
    body: 'Here\'s the latest update on our project...',
    date: '2023-05-10T10:30:00Z',
    read: false,
  },
  {
    id: '2',
    from: 'sarah@example.com',
    subject: 'Meeting Reminder',
    body: 'Don\'t forget about our team meeting tomorrow at 2 PM.',
    date: '2023-05-09T15:45:00Z',
    read: true,
  },
  {
    id: '3',
    from: 'client@example.com',
    subject: 'New Feature Request',
    body: 'We\'d like to discuss adding a new feature to the platform...',
    date: '2023-05-08T09:15:00Z',
    read: false,
  },
];

const EmailInterface: React.FC = () => {
  const [emails, setEmails] = useState<Email[]>(mockEmails);
  const [selectedEmail, setSelectedEmail] = useState<Email | null>(null);
  const [composing, setComposing] = useState(false);
  const [newEmail, setNewEmail] = useState({ to: '', subject: '', body: '' });

  const handleEmailClick = (email: Email) => {
    setSelectedEmail(email);
    setEmails(emails.map(e => e.id === email.id ? { ...e, read: true } : e));
  };

  const handleCompose = () => {
    setSelectedEmail(null);
    setComposing(true);
  };

  const handleSend = () => {
    // In a real application, you would send the email here
    console.log('Sending email:', newEmail);
    setComposing(false);
    setNewEmail({ to: '', subject: '', body: '' });
  };

  return (
    <div className="flex h-full">
      {/* Inbox */}
      <div className="w-1/3 border-r border-secondary-200 overflow-y-auto">
        <div className="p-4">
          <button
            onClick={handleCompose}
            className="w-full bg-primary-600 text-white py-2 px-4 rounded hover:bg-primary-700 transition duration-150 ease-in-out"
          >
            Compose
          </button>
        </div>
        <ul>
          {emails.map(email => (
            <li
              key={email.id}
              onClick={() => handleEmailClick(email)}
              className={`p-4 border-b border-secondary-200 cursor-pointer ${
                email.read ? 'bg-white' : 'bg-primary-50'
              } hover:bg-secondary-100`}
            >
              <div className="font-semibold">{email.from}</div>
              <div className="text-sm text-secondary-600">{email.subject}</div>
              <div className="text-xs text-secondary-500">{new Date(email.date).toLocaleString()}</div>
            </li>
          ))}
        </ul>
      </div>

      {/* Email preview or composition */}
      <div className="w-2/3 p-4">
        {composing ? (
          <div>
            <h2 className="text-2xl font-bold mb-4">New Email</h2>
            <input
              type="text"
              placeholder="To"
              value={newEmail.to}
              onChange={e => setNewEmail({ ...newEmail, to: e.target.value })}
              className="w-full mb-2 p-2 border border-secondary-300 rounded"
            />
            <input
              type="text"
              placeholder="Subject"
              value={newEmail.subject}
              onChange={e => setNewEmail({ ...newEmail, subject: e.target.value })}
              className="w-full mb-2 p-2 border border-secondary-300 rounded"
            />
            <textarea
              placeholder="Body"
              value={newEmail.body}
              onChange={e => setNewEmail({ ...newEmail, body: e.target.value })}
              className="w-full h-64 mb-2 p-2 border border-secondary-300 rounded"
            />
            <button
              onClick={handleSend}
              className="bg-primary-600 text-white py-2 px-4 rounded hover:bg-primary-700 transition duration-150 ease-in-out"
            >
              Send
            </button>
          </div>
        ) : selectedEmail ? (
          <div>
            <h2 className="text-2xl font-bold mb-2">{selectedEmail.subject}</h2>
            <div className="mb-4">
              <span className="font-semibold">From:</span> {selectedEmail.from}
            </div>
            <div className="mb-4">
              <span className="font-semibold">Date:</span> {new Date(selectedEmail.date).toLocaleString()}
            </div>
            <div className="whitespace-pre-wrap">{selectedEmail.body}</div>
          </div>
        ) : (
          <div className="text-center text-secondary-500">Select an email to read</div>
        )}
      </div>
    </div>
  );
};

export default EmailInterface;
