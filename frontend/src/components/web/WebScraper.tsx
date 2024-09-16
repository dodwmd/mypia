import React, { useState } from 'react';
import { scrapeWebsite } from '../../services/web.service';

const WebScraper: React.FC = () => {
  const [url, setUrl] = useState('');
  const [scrapedContent, setScrapedContent] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setScrapedContent('');

    try {
      const content = await scrapeWebsite(url);
      setScrapedContent(content);
    } catch (err) {
      setError('Failed to scrape website. Please check the URL and try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto mt-8">
      <h2 className="text-2xl font-bold mb-4">Web Scraper</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="url" className="block text-sm font-medium text-gray-700">
            Website URL
          </label>
          <input
            type="url"
            id="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
            placeholder="https://example.com"
            required
          />
        </div>
        <button
          type="submit"
          disabled={loading}
          className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
        >
          {loading ? 'Scraping...' : 'Scrape Website'}
        </button>
      </form>
      {error && <p className="mt-4 text-red-500">{error}</p>}
      {scrapedContent && (
        <div className="mt-6">
          <h3 className="text-lg font-medium text-gray-900">Scraped Content:</h3>
          <div className="mt-2 p-4 bg-gray-100 rounded-md">
            <pre className="whitespace-pre-wrap">{scrapedContent}</pre>
          </div>
        </div>
      )}
    </div>
  );
};

export default WebScraper;
