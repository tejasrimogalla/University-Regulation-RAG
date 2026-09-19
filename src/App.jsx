import React, { useState, useEffect, useCallback } from 'react';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import Chat from './components/Chat';
import {
  getDocuments,
  uploadDocuments,
  deleteDocument,
  rebuildIndex,
  getIndexStatus,
  askQuestion,
  getHealth
} from './api';
import './App.css';

export default function App() {
  const [documents, setDocuments] = useState([]);
  const [indexStatus, setIndexStatus] = useState(null);
  const [health, setHealth] = useState(null);

  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState('');
  const [uploading, setUploading] = useState(false);
  const [indexing, setIndexing] = useState(false);
  const [deletingFile, setDeletingFile] = useState(null);
  const [error, setError] = useState(null);
  const [loadingSamples, setLoadingSamples] = useState(false);

  // Initial load
  const fetchData = useCallback(async () => {
    try {
      const [docsRes, statusRes, healthRes] = await Promise.allSettled([
        getDocuments(),
        getIndexStatus(),
        getHealth()
      ]);

      if (docsRes.status === 'fulfilled') {
        setDocuments(docsRes.value.documents || []);
      }
      if (statusRes.status === 'fulfilled') {
        setIndexStatus(statusRes.value);
      }
      if (healthRes.status === 'fulfilled') {
        setHealth(healthRes.value);
      }
    } catch (err) {
      console.error('Error fetching initial app data:', err);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Handle PDF upload
  const handleUpload = async (files) => {
    setUploading(true);
    setError(null);
    try {
      const result = await uploadDocuments(files);
      await fetchData();
      // Auto prompt user to rebuild index if documents added
      if (result.uploaded_count > 0) {
        handleRebuildIndex();
      }
    } catch (err) {
      setError(err.message || 'Failed to upload documents.');
    } finally {
      setUploading(false);
    }
  };

  // Handle document deletion
  const handleDelete = async (filename) => {
    if (!window.confirm(`Are you sure you want to delete "${filename}"?`)) return;
    setDeletingFile(filename);
    setError(null);
    try {
      await deleteDocument(filename);
      await fetchData();
      // Automatically re-index remaining documents
      handleRebuildIndex();
    } catch (err) {
      setError(err.message || 'Failed to delete document.');
    } finally {
      setDeletingFile(null);
    }
  };

  // Handle index rebuild
  const handleRebuildIndex = async () => {
    setIndexing(true);
    setError(null);
    try {
      await rebuildIndex();
      await fetchData();
    } catch (err) {
      setError(err.message || 'Failed to rebuild FAISS index.');
    } finally {
      setIndexing(false);
    }
  };

  // Handle user question submission
  const handleSendMessage = async (questionText) => {
    if (!questionText || loading) return;

    setError(null);
    const userMessage = { role: 'user', content: questionText };
    const updatedMessages = [...messages, userMessage];
    setMessages(updatedMessages);

    setLoading(true);
    setLoadingStep('Searching university regulations...');

    // Simulate progressive status updates for better UX
    const stepTimer1 = setTimeout(() => {
      setLoadingStep('Retrieving relevant sections and checking similarity...');
    }, 450);

    const stepTimer2 = setTimeout(() => {
      setLoadingStep('Generating grounded answer with citations via NVIDIA API...');
    }, 950);

    try {
      // Build conversation history for API (last 6 turns excluding current query)
      const history = messages.slice(-6).map((m) => ({
        role: m.role,
        content: m.content
      }));

      const res = await askQuestion(questionText, history);

      clearTimeout(stepTimer1);
      clearTimeout(stepTimer2);

      const assistantMessage = {
        role: 'assistant',
        content: res.answer,
        found: res.found,
        sources: res.sources || [],
        error: res.error
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      clearTimeout(stepTimer1);
      clearTimeout(stepTimer2);

      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: 'Unable to retrieve an answer due to an error.',
          found: false,
          sources: [],
          error: err.message || 'Error communicating with the backend.'
        }
      ]);
    } finally {
      setLoading(false);
      setLoadingStep('');
    }
  };

  // Handle load sample regulations (triggers server endpoint or file generation)
  const handleLoadSampleDocs = async () => {
    setLoadingSamples(true);
    setError(null);
    try {
      const res = await fetch('/api/load-sample-data', { method: 'POST' });
      if (!res.ok) {
        // If endpoint doesn't exist, trigger rebuild directly
        await rebuildIndex();
      }
      await fetchData();
    } catch (err) {
      console.warn('Sample load endpoint:', err);
      // Fallback rebuild
      await handleRebuildIndex();
    } finally {
      setLoadingSamples(false);
    }
  };

  const handleClearChat = () => {
    setMessages([]);
    setError(null);
  };

  return (
    <div className="app-layout">
      <Sidebar
        documents={documents}
        indexStatus={indexStatus}
        indexing={indexing}
        uploading={uploading}
        deletingFile={deletingFile}
        onUpload={handleUpload}
        onDelete={handleDelete}
        onRebuildIndex={handleRebuildIndex}
        onLoadSampleDocs={handleLoadSampleDocs}
        loadingSamples={loadingSamples}
      />

      <main className="app-main">
        <Header
          health={health}
          indexStatus={indexStatus}
          onClearChat={handleClearChat}
          hasMessages={messages.length > 0}
        />

        <Chat
          messages={messages}
          loading={loading}
          loadingStep={loadingStep}
          error={error}
          onSendMessage={handleSendMessage}
          indexStatus={indexStatus}
        />
      </main>
    </div>
  );
}
