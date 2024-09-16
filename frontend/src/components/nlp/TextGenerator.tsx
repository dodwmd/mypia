import React, { useState } from 'react';
import { generateText } from '../../services/nlp.service';

const TextGenerator: React.FC = () => {
  const [prompt, setPrompt] = useState('');
  const [generatedText, setGeneratedText] = useState('');
  const [maxLength, setMaxLength] = useState(100);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setGeneratedText('');

    try {
      const result = await generateText(prompt, maxLength);
      setGeneratedText(result.generated_text);
    } catch (err) {
      setError('Failed to generate text. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto mt-8">
      <h2 className="text-2xl font-bold mb-4">Text Generator</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="prompt" className="block text-sm font-medium text-gray-700">
            Prompt
          </label>
          <textarea
            id="prompt"
            rows={3}
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
            placeholder="Enter a prompt for text generation..."
            required
          ></textarea>
        </div>
        <div>
          <label htmlFor="maxLength" className="block text-sm font-medium text-gray-700">
            Maximum Generated Text Length
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
          {loading ? 'Generating...' : 'Generate Text'}
        </button>
      </form>
      {error && <p className="mt-4 text-red-500">{error}</p>}
      {generatedText && (
        <div className="mt-6">
          <h3 className="text-lg font-medium text-gray-900">Generated Text:</h3>
          <p className="mt-2 text-gray-600">{generatedText}</p>
        </div>
      )}
    </div>
  );
};

export default TextGenerator;
