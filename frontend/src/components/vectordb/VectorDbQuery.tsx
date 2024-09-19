import React, { useState } from 'react';
import { queryVectorDb } from '../../services/vectordb.service';

const VectorDbQuery: React.FC = () => {
  const [query, setQuery] = useState('');
  const [collection, setCollection] = useState('default_collection');
  const [results, setResults] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await queryVectorDb(collection, query);
      setResults(response);
      setError(null);
    } catch (err) {
      setError('Error querying vector database');
      setResults(null);
    }
  };

  return (
    <div className="max-w-2xl mx-auto mt-8">
      <h2 className="text-2xl font-bold mb-4">Query Vector Database</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="collection" className="block mb-1">Collection:</label>
          <input
            type="text"
            id="collection"
            value={collection}
            onChange={(e) => setCollection(e.target.value)}
            className="w-full px-3 py-2 border rounded"
            required
          />
        </div>
        <div>
          <label htmlFor="query" className="block mb-1">Query:</label>
          <textarea
            id="query"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="w-full px-3 py-2 border rounded"
            rows={4}
            required
          />
        </div>
        <button type="submit" className="bg-blue-500 text-white px-4 py-2 rounded">
          Submit Query
        </button>
      </form>

      {error && <p className="text-red-500 mt-4">{error}</p>}

      {results && (
        <div className="mt-8">
          <h3 className="text-xl font-bold mb-2">Results:</h3>
          <pre className="bg-gray-100 p-4 rounded overflow-x-auto">
            {JSON.stringify(results, null, 2)}
          </pre>
        </div>
      )}

      <div className="mt-8">
        <h3 className="text-xl font-bold mb-2">Query Examples:</h3>
        <ul className="list-disc pl-5">
          <li>Simple keyword search: "artificial intelligence"</li>
          <li>Phrase search: "machine learning applications"</li>
          <li>Multiple concepts: "climate change renewable energy"</li>
          <li>Question: "What are the benefits of electric vehicles?"</li>
        </ul>
      </div>

      <div className="mt-8">
        <h3 className="text-xl font-bold mb-2">About ChromaDB:</h3>
        <p>
          ChromaDB is an open-source embedding database designed for building AI applications with embeddings and natural language processing. It offers:
        </p>
        <ul className="list-disc pl-5 mt-2">
          <li>Fast similarity search</li>
          <li>Support for various embedding models</li>
          <li>Easy integration with machine learning workflows</li>
          <li>Scalability for large datasets</li>
          <li>Support for metadata filtering</li>
        </ul>
      </div>
    </div>
  );
};

export default VectorDbQuery;
