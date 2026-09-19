import axios from 'axios';

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '');

// Centralized Axios API client for University Regulation RAG Assistant
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 60000, // 60s timeout
});

// Response interceptor to format error messages
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    let message = 'An unexpected error occurred.';
    if (error.response?.data) {
      message = error.response.data.detail || error.response.data.error || error.response.data.message || message;
    } else if (error.message) {
      message = error.message;
    }
    return Promise.reject(new Error(message));
  }
);

/**
 * Upload multiple PDF documents.
 * @param {FileList|File[]} files
 */
export async function uploadDocuments(files) {
  const formData = new FormData();
  for (let i = 0; i < files.length; i++) {
    formData.append('files', files[i]);
  }

  return api.post('/documents/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
}

/**
 * Fetch list of all uploaded PDF documents.
 */
export async function getDocuments() {
  return api.get('/documents');
}

/**
 * Delete a specific document by filename.
 * @param {string} filename
 */
export async function deleteDocument(filename) {
  return api.delete(`/documents/${encodeURIComponent(filename)}`);
}

/**
 * Trigger full index rebuild from stored PDFs.
 */
export async function rebuildIndex() {
  return api.post('/index/rebuild');
}

/**
 * Fetch current FAISS index status and metrics.
 */
export async function getIndexStatus() {
  return api.get('/index/status');
}

/**
 * Submit question to RAG pipeline with optional conversation history.
 * @param {string} question
 * @param {Array<{role: string, content: string}>} conversationHistory
 */
export async function askQuestion(question, conversationHistory = []) {
  return api.post('/chat', {
    question,
    conversation_history: conversationHistory,
  });
}

/**
 * Fetch system health and configuration status.
 */
export async function getHealth() {
  return api.get('/health');
}

/**
 * Trigger generation of sample university regulations and automatic index rebuild.
 */
export async function loadSampleRegulations() {
  return api.post('/load-sample-data');
}

/**
 * Returns the URL to open/view a PDF at a specific page.
 * @param {string} filename
 * @param {number} page
 */
export function getDocumentUrl(filename, page = 1) {
  return `${API_BASE_URL}/documents/${encodeURIComponent(filename)}#page=${page}`;
}

export default api;
