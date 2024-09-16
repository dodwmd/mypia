import api from './api';

export const getGithubRepos = async (username: string) => {
  try {
    const response = await api.get(`/github/repos`, { params: { username } });
    return response.data;
  } catch (error) {
    console.error('Error fetching GitHub repos:', error);
    throw error;
  }
};

export const getGithubIssues = async (repoFullName: string) => {
  try {
    const response = await api.get(`/github/issues`, { params: { repo_full_name: repoFullName } });
    return response.data;
  } catch (error) {
    console.error('Error fetching GitHub issues:', error);
    throw error;
  }
};
