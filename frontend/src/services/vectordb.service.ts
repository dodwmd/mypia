import api from '../utils/api';

export const queryVectorDb = async (query: string) => {
  try {
    const response = await api.post('/v1/vectordb/query', { query });
    return response.data;
  } catch (error) {
    console.error('Error querying vector database:', error);
    throw error;
  }
};

export const uploadToVectorDb = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await api.post('/v1/vectordb/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error uploading to vector database:', error);
    throw error;
  }
};
