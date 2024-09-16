import React, { useState } from 'react';
import { queryVectorDb } from '../../services/vectordb.service';

interface QueryResult {
  title: string;
  content: string;
  similarity: number;
}

const VectorDbQuerier: React.FC = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<QueryResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResults([]);

    try {
      const queryResults = await queryVectorDb(query);
      setResults(queryResults);
    } catch (err) {
      setError('Failed to query vector database. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto mt-8">
      <h2 className="text-2xl font-bold mb-4">Query Vector Database</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="query" className="block text-sm font-medium text-gray-700">
            Query
          </label>
          <input
            type="text"
            id="query"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
            placeholder="Enter your query here"
            required
          />
        </div>
        <button
          type="submit"
          disabled={loading}
          className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
        >
          {loading ? 'Querying...' : 'Query'}
        </button>
      </form>
      {error && <p className="mt-4 text-red-500">{error}</p>}
      {results.length > 0 && (
        <div className="mt-6">
          <h3 className="text-lg font-medium text-gray-900">Results:</h3>
          <ul className="mt-2 divide-y divide-gray-200">
            {results.map((result, index) => (
              <li key={index} className="py-4">
                <p className="text-sm font-medium text-gray-900">{result.title}</p>
                <p className="mt-1 text-sm text-gray-600">{result.content}</p>
                <p className="mt-1 text-xs text-gray-500">Similarity: {result.similarity.toFixed(4)}</p>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default VectorDbQuerier;
