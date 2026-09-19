import React from 'react';
import ReactMarkdown from 'react-markdown';
import { GraduationCap, CheckCircle2, AlertTriangle, ShieldCheck, User } from 'lucide-react';
import SourceCard from './SourceCard';

export default function ChatMessage({ message }) {
  const isUser = message.role === 'user';
  const { content, found, sources, error } = message;

  if (isUser) {
    return (
      <div className="chat-row user-row">
        <div className="chat-bubble user-bubble">
          <div className="bubble-header">
            <div className="user-identity">
              <User size={14} className="mr-1" />
              <span className="sender-tag">You</span>
            </div>
          </div>
          <div className="bubble-content">{content}</div>
        </div>
      </div>
    );
  }

  // Assistant message
  return (
    <div className="chat-row assistant-row">
      <div className="chat-bubble assistant-bubble">
        <div className="bubble-header">
          <div className="assistant-identity">
            <div className="bot-icon-wrapper">
              <GraduationCap size={16} color="#6366f1" />
            </div>
            <span className="sender-tag">Regulation Assistant</span>
          </div>

          <div className="answer-badge-container">
            {found ? (
              <span className="grounded-badge">
                <CheckCircle2 size={12} color="#10b981" />
                Grounded in Regulations
              </span>
            ) : (
              <span className="not-found-badge">
                <AlertTriangle size={12} color="#f59e0b" />
                Not in Regulations
              </span>
            )}
          </div>
        </div>

        {error && (
          <div className="alert-box alert-error">
            <strong>Notice: </strong> {error}
          </div>
        )}

        <div className="bubble-content markdown-body">
          <ReactMarkdown>{content}</ReactMarkdown>
        </div>

        {/* Source Citations Section */}
        {sources && sources.length > 0 && (
          <div className="sources-container">
            <div className="sources-header">
              <div className="sources-title-group">
                <ShieldCheck size={14} color="#3b82f6" />
                <span className="sources-title">Authoritative Sources ({sources.length})</span>
              </div>
              <span className="sources-caption">Extracted from verified university documents</span>
            </div>
            <div className="sources-grid">
              {sources.map((src, i) => (
                <SourceCard key={i} source={src} />
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
