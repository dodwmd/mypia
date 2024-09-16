import React, { useState } from 'react';
import { fetchWebPage } from '../../services/web.service';

const WebBrowser: React.FC = () => {
  const [url, setUrl] = useState('');
  const [pageContent, setPageContent] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setPageContent('');

    try {
      const content = await fetchWebPage(url);
      setPageContent(content);
    } catch (err) {
      setError('Failed to load web page. Please check the URL and try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto mt-8">
      <h2 className="text-2xl font-bold mb-4">Web Browser</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="flex">
          <input
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            className="flex-grow border border-gray-300 rounded-l-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
            placeholder="https://example.com"
            required
          />
          <button
            type="submit"
            disabled={loading}
            className="flex-shrink-0 px-4 py-2 border border-transparent rounded-r-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            {loading ? 'Loading...' : 'Go'}
          </button>
        </div>
      </form>
      {error && <p className="mt-4 text-red-500">{error}</p>}
      {pageContent && (
        <div className="mt-6">
          <h3 className="text-lg font-medium text-gray-900">Web Page Content:</h3>
          <div className="mt-2 p-4 bg-white border border-gray-200 rounded-md">
            <iframe
              srcDoc={pageContent}
              title="Web Page Content"
              className="w-full h-96 border-none"
              sandbox="allow-scripts"
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default WebBrowser;
