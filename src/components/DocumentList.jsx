import React from 'react';
import { FileText, ExternalLink, Trash2 } from 'lucide-react';
import { getDocumentUrl } from '../api';

export default function DocumentList({ documents, onDelete, deletingFile }) {
  if (!documents || documents.length === 0) {
    return (
      <div className="doc-list-empty">
        <p>No documents uploaded yet.</p>
        <span className="empty-subtext">Upload university PDFs above to build your regulation knowledge base.</span>
      </div>
    );
  }

  return (
    <div className="doc-list-container">
      <div className="doc-list-scroll">
        {documents.map((doc) => {
          const isDeleting = deletingFile === doc.filename;
          const pdfUrl = getDocumentUrl(doc.filename);

          return (
            <div key={doc.filename} className="doc-item">
              <div className="doc-item-icon">
                <FileText size={18} color="#818cf8" />
              </div>

              <div className="doc-item-details">
                <span className="doc-item-name" title={doc.filename}>
                  {doc.filename}
                </span>
                <div className="doc-item-meta">
                  <span className="doc-size">{doc.size_kb} KB</span>
                  <span className={`doc-index-indicator ${doc.indexed ? 'indicator-indexed' : 'indicator-unindexed'}`}>
                    {doc.indexed ? 'Indexed' : 'Pending Rebuild'}
                  </span>
                </div>
              </div>

              <div className="doc-item-actions">
                <a
                  href={pdfUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn-icon"
                  title="View PDF document"
                >
                  <ExternalLink size={13} />
                </a>

                <button
                  className="btn-icon btn-icon-danger"
                  onClick={() => onDelete(doc.filename)}
                  disabled={isDeleting}
                  title="Delete document"
                >
                  {isDeleting ? (
                    <span className="btn-spinner-sm"></span>
                  ) : (
                    <Trash2 size={13} />
                  )}
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
