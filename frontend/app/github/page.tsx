'use client';
import React from 'react';
import GithubRepoList from '../../src/components/github/GithubRepoList';
import GithubIssueList from '../../src/components/github/GithubIssueList';

export default function GitHubPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold mb-8">GitHub</h1>
      <GithubRepoList />
      <GithubIssueList />
    </div>
  );
}
