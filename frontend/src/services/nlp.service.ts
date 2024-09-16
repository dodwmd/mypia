import api from './api';

export const summarizeText = async (text: string, maxLength: number = 100) => {
  try {
    const response = await api.post('/summarize', { text, max_length: maxLength });
    return response.data;
  } catch (error) {
    console.error('Error summarizing text:', error);
    throw error;
  }
};

export const generateText = async (prompt: string, maxLength: number = 100) => {
  try {
    const response = await api.post('/generate', { prompt, max_length: maxLength });
    return response.data;
  } catch (error) {
    console.error('Error generating text:', error);
    throw error;
  }
};
