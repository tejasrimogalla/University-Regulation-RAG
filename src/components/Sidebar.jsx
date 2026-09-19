import React from 'react';
import {
  GraduationCap,
  UploadCloud,
  FileText,
  RefreshCw,
  Sparkles,
  Layers,
  Database
} from 'lucide-react';
import DocumentUpload from './DocumentUpload';
import DocumentList from './DocumentList';

export default function Sidebar({
  documents,
  indexStatus,
  indexing,
  uploading,
  deletingFile,
  onUpload,
  onDelete,
  onRebuildIndex,
  onLoadSampleDocs,
  loadingSamples
}) {
  const isReady = indexStatus?.status === 'READY';
  const isIndexing = indexing || indexStatus?.status === 'INDEXING...';
  const chunkCount = indexStatus?.indexed_chunks || 0;
  const docCount = documents.length;

  return (
    <aside className="app-sidebar">
      <div className="sidebar-brand">
        <div className="brand-icon">
          <GraduationCap size={24} color="#818cf8" />
        </div>
        <div className="brand-text">
          <h2>UniRAG</h2>
          <span className="brand-tagline">Regulation Engine</span>
        </div>
      </div>

      <div className="sidebar-section">
        <div className="section-title-row">
          <div className="title-with-icon">
            <UploadCloud size={14} className="section-title-icon" />
            <h3>Upload Documents</h3>
          </div>
          <span className="section-count">{docCount} Docs</span>
        </div>
        <DocumentUpload onUpload={onUpload} uploading={uploading} />
      </div>

      <div className="sidebar-section doc-list-section">
        <div className="section-title-row">
          <div className="title-with-icon">
            <FileText size={14} className="section-title-icon" />
            <h3>Knowledge Base</h3>
          </div>
        </div>
        <DocumentList
          documents={documents}
          onDelete={onDelete}
          deletingFile={deletingFile}
        />
      </div>

      <div className="sidebar-footer">
        {/* Index Action & Status */}
        <div className="index-card">
          <div className="index-stats-row">
            <div className="stat-block">
              <span className="stat-label">Documents</span>
              <span className="stat-value">{docCount}</span>
            </div>
            <div className="stat-block">
              <span className="stat-label">Chunks</span>
              <span className="stat-value">{chunkCount.toLocaleString()}</span>
            </div>
            <div className="stat-block">
              <span className="stat-label">Status</span>
              <span className={`status-pill ${isReady ? 'pill-ready' : isIndexing ? 'pill-indexing' : 'pill-warning'}`}>
                {isIndexing ? 'Indexing...' : isReady ? 'Ready' : 'Not Indexed'}
              </span>
            </div>
          </div>

          <button
            className="btn-primary btn-rebuild btn-block mt-2"
            onClick={onRebuildIndex}
            disabled={isIndexing || docCount === 0}
          >
            {isIndexing ? (
              <>
                <span className="btn-spinner"></span>
                <span>Indexing Chunks...</span>
              </>
            ) : (
              <>
                <RefreshCw size={13} className="mr-1" />
                <span>Rebuild FAISS Index</span>
              </>
            )}
          </button>

          {docCount === 0 && (
            <button
              className="btn-secondary btn-block mt-2 btn-sm"
              onClick={onLoadSampleDocs}
              disabled={loadingSamples || isIndexing}
            >
              <Sparkles size={13} className="mr-1 text-amber" />
              <span>{loadingSamples ? 'Loading Samples...' : 'Load Sample Regulations'}</span>
            </button>
          )}
        </div>
      </div>
    </aside>
  );
}
