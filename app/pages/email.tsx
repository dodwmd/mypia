import React from 'react';
import Layout from '../components/Layout';
import EmailInterface from '../components/EmailInterface';

const EmailPage: React.FC = () => {
  return (
    <Layout>
      <div className="h-full">
        <EmailInterface />
      </div>
    </Layout>
  );
};

export default EmailPage;
