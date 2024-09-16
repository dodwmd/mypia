'use client';
import React, { useState, useEffect, useCallback } from 'react';
import { getGithubRepos } from '../../services/github.service';

interface Repo {
  id: number;
  name: string;
  full_name: string;
  html_url: string;
  description: string | null;
  stargazers_count: number;
  forks_count: number;
  language: string | null;  // Add this line
}

const GithubRepoList: React.FC = () => {
  const [repos, setRepos] = useState<Repo[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [username, setUsername] = useState('');

  const fetchRepos = useCallback(async () => {
    if (!username) return;
    setLoading(true);
    setError('');
    try {
      const fetchedRepos = await getGithubRepos(username);
      setRepos(fetchedRepos);
    } catch (err) {
      setError('Failed to fetch repositories. Please try again.');
    } finally {
      setLoading(false);
    }
  }, [username]);

  useEffect(() => {
    if (username) {
      fetchRepos();
    }
  }, [username, fetchRepos]);

  return (
    <div className="max-w-4xl mx-auto mt-8">
      <h2 className="text-2xl font-bold mb-4">GitHub Repositories</h2>
      <div className="mb-4">
        <input
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="Enter GitHub username"
          className="px-3 py-2 border border-gray-300 rounded-md mr-2"
        />
        <button
          onClick={fetchRepos}
          className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600"
        >
          Fetch Repos
        </button>
      </div>
      {loading && <p>Loading repositories...</p>}
      {error && <p className="text-red-500">{error}</p>}
      {repos.length > 0 && (
        <ul className="space-y-4">
          {repos.map((repo) => (
            <li key={repo.id} className="border p-4 rounded-md">
              <h3 className="text-xl font-semibold">
                <a href={repo.html_url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                  {repo.name}
                </a>
              </h3>
              <p className="text-gray-600">{repo.description}</p>
              <div className="mt-2 flex space-x-4">
                <span>⭐ {repo.stargazers_count}</span>
                <span>🍴 {repo.forks_count}</span>
                {repo.language && <span>🔤 {repo.language}</span>}
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default GithubRepoList;
