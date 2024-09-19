'use client';
import React, { useState } from 'react';
import { uploadToVectorDb } from '../../services/vectordb.service';

const VectorDbAdder: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState('');

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFile(e.target.files[0]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      setMessage('Please select a file');
      return;
    }

    setUploading(true);
    setMessage('');

    try {
      await uploadToVectorDb(file);
      setMessage('File uploaded successfully');
      setFile(null);
    } catch (error) {
      setMessage('Error uploading file');
      console.error('Error uploading file:', error);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="mt-4">
      <h2 className="text-xl font-bold mb-2">Add to Vector Database</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="file"
          onChange={handleFileChange}
          accept=".pdf,.txt,.doc,.docx"
          className="mb-2"
        />
        <button
          type="submit"
          disabled={uploading || !file}
          className="bg-blue-500 text-white px-4 py-2 rounded disabled:bg-gray-400"
        >
          {uploading ? 'Uploading...' : 'Upload'}
        </button>
      </form>
      {message && <p className="mt-2">{message}</p>}
    </div>
  );
};

export default VectorDbAdder;
