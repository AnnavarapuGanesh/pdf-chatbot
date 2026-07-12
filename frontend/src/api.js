import axios from 'axios';

// All requests are proxied via Vite config to http://localhost:8000
const API = axios.create({
  baseURL: '/api',
});

/**
 * Uploads a list of PDF files to the backend.
 * Uses multipart/form-data.
 */
export const uploadPDFs = async (files) => {
  const formData = new FormData();
  files.forEach((file) => {
    formData.append('files', file);
  });
  
  const response = await API.post('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

/**
 * Sends a question and optional base64 image to the RAG backend.
 */
export const askQuestion = async (question, imageBase64 = null) => {
  const response = await API.post('/ask', {
    question,
    image: imageBase64,
  });
  return response.data;
};

/**
 * Retrieves the names of currently indexed PDF documents.
 */
export const getFiles = async () => {
  const response = await API.get('/files');
  return response.data;
};

/**
 * Clears the RAG index, conversational memory, and uploaded files.
 */
export const clearAll = async () => {
  const response = await API.delete('/clear');
  return response.data;
};
