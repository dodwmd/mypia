import React, { useState, useEffect } from 'react';
import { getEmails, Email } from '../../services/email.service';

const EmailList: React.FC = () => {
  const [emails, setEmails] = useState<Email[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchEmails();
  }, []);

  const fetchEmails = async () => {
    try {
      const fetchedEmails = await getEmails();
      setEmails(fetchedEmails);
    } catch (error) {
      console.error('Error fetching emails:', error);
    }
  };

  if (loading) return <div>Loading emails...</div>;
  if (error) return <div className="text-red-500">{error}</div>;

  return (
    <div className="space-y-4">
      {emails.map((email) => (
        <div key={email.id} className="border p-4 rounded-md">
          <h3 className="text-lg font-semibold">{email.subject}</h3>
          <p className="text-sm text-gray-600">From: {email.sender}</p>
          <p className="text-sm text-gray-600">Date: {new Date(email.date).toLocaleString()}</p>
          <p className="mt-2">{email.preview}</p>
        </div>
      ))}
    </div>
  );
};

export default EmailList;
