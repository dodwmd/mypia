import api from './api';

export const uploadToVectorDb = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post('/vectordb/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
};

export const queryVectorDb = async (collection: string, queryText: string) => {
  const response = await api.post('/vectordb/query', {
    collection_name: collection,
    query_text: queryText,
    n_results: 5,
  });

  return response.data;
};
