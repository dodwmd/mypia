import React, { useState } from 'react';
import { summarizeText } from '../../services/nlp.service';

const TextSummarizer: React.FC = () => {
  const [inputText, setInputText] = useState('');
  const [summary, setSummary] = useState('');
  const [maxLength, setMaxLength] = useState(100);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSummary('');

    try {
      const result = await summarizeText(inputText, maxLength);
      setSummary(result.summary);
    } catch (err) {
      setError('Failed to summarize text. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto mt-8">
      <h2 className="text-2xl font-bold mb-4">Text Summarizer</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="inputText" className="block text-sm font-medium text-gray-700">
            Input Text
          </label>
          <textarea
            id="inputText"
            rows={6}
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
            placeholder="Enter the text you want to summarize..."
            required
          ></textarea>
        </div>
        <div>
          <label htmlFor="maxLength" className="block text-sm font-medium text-gray-700">
            Maximum Summary Length
          </label>
          <input
            type="number"
            id="maxLength"
            value={maxLength}
            onChange={(e) => setMaxLength(Number(e.target.value))}
            min={10}
            max={500}
            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
          />
        </div>
        <button
          type="submit"
          disabled={loading}
          className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
        >
          {loading ? 'Summarizing...' : 'Summarize'}
        </button>
      </form>
      {error && <p className="mt-4 text-red-500">{error}</p>}
      {summary && (
        <div className="mt-6">
          <h3 className="text-lg font-medium text-gray-900">Summary:</h3>
          <p className="mt-2 text-gray-600">{summary}</p>
        </div>
      )}
    </div>
  );
};

export default TextSummarizer;
