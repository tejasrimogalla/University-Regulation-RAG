import React from 'react';
import { Zap, Database, RotateCcw } from 'lucide-react';

export default function Header({ health, indexStatus, onClearChat, hasMessages }) {
  const isNvidiaReady = health?.nvidia_configured;
  const isIndexReady = indexStatus?.status === 'READY';
  const chunkCount = indexStatus?.indexed_chunks || 0;

  return (
    <header className="app-header">
      <div className="header-left">
        <div className="header-title-group">
          <h1>University Regulation Assistant</h1>
          <p className="header-subtitle">
            Grounded AI for Academic Rules, Attendance, Examinations & Student Handbooks
          </p>
        </div>
      </div>

      <div className="header-right">
        <div className="status-chips">
          {/* Index Status Chip */}
          <div className={`status-chip ${isIndexReady ? 'chip-success' : 'chip-warning'}`}>
            <Database size={13} className="chip-icon" />
            <span className="chip-label">
              {isIndexReady ? `${chunkCount.toLocaleString()} Chunks Indexed` : 'Index: Not Ready'}
            </span>
          </div>

          {/* NVIDIA Model Chip */}
          <div className={`status-chip ${isNvidiaReady ? 'chip-info' : 'chip-neutral'}`}>
            <Zap size={13} className="chip-icon" />
            <span className="chip-label">
              {isNvidiaReady ? (health.nvidia_model || 'NVIDIA API') : 'NVIDIA: Key Needed'}
            </span>
          </div>
        </div>

        {hasMessages && (
          <button
            className="btn-secondary btn-sm"
            onClick={onClearChat}
            title="Reset conversation"
          >
            <RotateCcw size={12} className="mr-1" />
            <span>Clear Chat</span>
          </button>
        )}
      </div>
    </header>
  );
}
