'use client';
import React, { useState, useEffect, useCallback } from 'react';
import { getGithubIssues } from '../../services/github.service';
import Image from 'next/image';

interface Issue {
  id: number;
  number: number;
  title: string;
  state: string;
  html_url: string;
  user: {
    login: string;
    avatar_url: string;
  };
  created_at: string;
  comments: number;
}

const GithubIssueList: React.FC = () => {
  const [issues, setIssues] = useState<Issue[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [repoFullName, setRepoFullName] = useState('');

  const fetchIssues = useCallback(async () => {
    if (!repoFullName) return;
    setLoading(true);
    setError('');
    try {
      const fetchedIssues = await getGithubIssues(repoFullName);
      setIssues(fetchedIssues);
    } catch (err) {
      setError('Failed to fetch issues. Please try again.');
    } finally {
      setLoading(false);
    }
  }, [repoFullName]);

  useEffect(() => {
    if (repoFullName) {
      fetchIssues();
    }
  }, [repoFullName, fetchIssues]);

  return (
    <div className="max-w-4xl mx-auto mt-8">
      <h2 className="text-2xl font-bold mb-4">GitHub Issues</h2>
      <div className="mb-4">
        <input
          type="text"
          value={repoFullName}
          onChange={(e) => setRepoFullName(e.target.value)}
          placeholder="Enter repo full name (e.g., owner/repo)"
          className="px-3 py-2 border border-gray-300 rounded-md mr-2 w-64"
        />
        <button
          onClick={fetchIssues}
          className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600"
        >
          Fetch Issues
        </button>
      </div>
      {loading && <p>Loading issues...</p>}
      {error && <p className="text-red-500">{error}</p>}
      {issues.length > 0 && (
        <ul className="space-y-4">
          {issues.map((issue) => (
            <li key={issue.id} className="border p-4 rounded-md">
              <h3 className="text-xl font-semibold">
                <a href={issue.html_url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                  #{issue.number} {issue.title}
                </a>
              </h3>
              <div className="mt-2 flex items-center space-x-4">
                <Image src={issue.user.avatar_url} alt={issue.user.login} width={32} height={32} className="rounded-full" />
                <span>{issue.user.login}</span>
                <span className={`px-2 py-1 rounded-full text-sm ${issue.state === 'open' ? 'bg-green-200 text-green-800' : 'bg-red-200 text-red-800'}`}>
                  {issue.state}
                </span>
                <span>💬 {issue.comments}</span>
                <span>🕒 {new Date(issue.created_at).toLocaleDateString()}</span>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default GithubIssueList;
