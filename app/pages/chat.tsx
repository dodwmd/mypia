import React from 'react';
import Layout from '../components/Layout';
import ChatInterface from '../components/ChatInterface';

const ChatPage: React.FC = () => {
  return (
    <Layout>
      <div className="h-full flex flex-col">
        <h1 className="text-2xl font-bold mb-4 px-4 py-2 bg-white dark:bg-secondary-800 shadow">Chat with AI Assistant</h1>
        <div className="flex-1 overflow-hidden">
          <ChatInterface />
        </div>
      </div>
    </Layout>
  );
};

export default ChatPage;
