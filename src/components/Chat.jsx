import React, { useState, useEffect, useRef } from 'react';
import ChatMessage from './ChatMessage';
import EmptyState from './EmptyState';

export default function Chat({
  messages,
  loading,
  loadingStep,
  error,
  onSendMessage,
  indexStatus
}) {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading, loadingStep]);

  const handleSubmit = (e) => {
    e?.preventDefault();
    if (!input.trim() || loading) return;
    onSendMessage(input.trim());
    setInput('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleInput = (e) => {
    setInput(e.target.value);
    e.target.style.height = 'auto';
    e.target.style.height = `${Math.min(e.target.scrollHeight, 150)}px`;
  };

  const isIndexReady = indexStatus?.status === 'READY' && indexStatus?.indexed_chunks > 0;

  return (
    <div className="chat-container">
      <div className="chat-messages-scroll">
        {messages.length === 0 ? (
          <EmptyState onSelectExample={(q) => onSendMessage(q)} />
        ) : (
          <div className="messages-list">
            {messages.map((msg, idx) => (
              <ChatMessage key={idx} message={msg} />
            ))}

            {loading && (
              <div className="chat-row assistant-row">
                <div className="chat-bubble assistant-bubble loading-bubble">
                  <div className="loading-spinner-ring"></div>
                  <div className="loading-text-container">
                    <span className="loading-step-text">
                      {loadingStep || 'Processing your query...'}
                    </span>
                    <span className="loading-subtext">Searching verified document index</span>
                  </div>
                </div>
              </div>
            )}

            {error && (
              <div className="chat-error-toast">
                <span>⚠️ {error}</span>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      <div className="chat-input-area">
        {!isIndexReady && (
          <div className="index-warning-banner">
            <span>ℹ️ Note: No documents indexed yet. Upload PDFs and click "Rebuild Index" in the sidebar to begin.</span>
          </div>
        )}

        <form className="chat-input-form" onSubmit={handleSubmit}>
          <textarea
            ref={textareaRef}
            rows={1}
            value={input}
            onChange={handleInput}
            onKeyDown={handleKeyDown}
            placeholder="Ask a question about university regulations, attendance, grading, exams... (Enter to submit)"
            disabled={loading}
            className="chat-textarea"
          />

          <button
            type="submit"
            className="btn-send"
            disabled={!input.trim() || loading}
            title="Submit question (Enter)"
          >
            {loading ? (
              <div className="btn-spinner"></div>
            ) : (
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="22" y1="2" x2="11" y2="13"></line>
                <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
              </svg>
            )}
          </button>
        </form>
        <div className="input-hint">
          <span>Press <strong>Enter</strong> to send, <strong>Shift + Enter</strong> for a new line</span>
        </div>
      </div>
    </div>
  );
}
