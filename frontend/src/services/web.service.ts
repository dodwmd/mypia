import api from './api';

export const scrapeWebsite = async (url: string): Promise<string> => {
  try {
    const response = await api.post('/web/scrape', { url });
    return response.data.content;
  } catch (error) {
    console.error('Error scraping website:', error);
    throw error;
  }
};

export const fetchWebPage = async (url: string): Promise<string> => {
  try {
    const response = await api.post('/web/fetch', { url });
    return response.data.content;
  } catch (error) {
    console.error('Error fetching web page:', error);
    throw error;
  }
};
