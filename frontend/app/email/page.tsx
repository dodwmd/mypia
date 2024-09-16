'use client';

import React from 'react';
import EmailList from '../../src/components/email/EmailList';
import EmailComposer from '../../src/components/email/EmailComposer';

export default function EmailPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold mb-8">Email</h1>
      <EmailComposer />
      <EmailList />
    </div>
  );
}
