import React, { useState } from 'react';
import { FileText, ExternalLink, ChevronDown, ChevronUp } from 'lucide-react';
import { getDocumentUrl } from '../api';

export default function SourceCard({ source }) {
  const [expanded, setExpanded] = useState(false);

  const { document: docName, page, score, text } = source;
  const percentage = Math.round((score || 0) * 100);
  const pdfUrl = getDocumentUrl(docName, page);

  return (
    <div className="source-card">
      <div className="source-card-header">
        <div className="source-doc-info">
          <FileText size={15} color="#818cf8" />
          <span className="source-filename" title={docName}>{docName}</span>
          <span className="source-page-badge">Page {page}</span>
        </div>

        <div className="source-score-container">
          <span className="source-score-text">Relevance: {percentage}%</span>
          <div className="score-bar-bg" title={`Similarity Score: ${score}`}>
            <div
              className="score-bar-fill"
              style={{ width: `${Math.min(Math.max(percentage, 5), 100)}%` }}
            ></div>
          </div>
        </div>
      </div>

      <div className="source-preview">
        <p className={`source-text ${expanded ? 'expanded' : 'collapsed'}`}>
          "{text}"
        </p>
        {text && text.length > 180 && (
          <button
            className="btn-link expand-btn"
            onClick={() => setExpanded(!expanded)}
          >
            {expanded ? (
              <>Show Less <ChevronUp size={12} /></>
            ) : (
              <>Show More <ChevronDown size={12} /></>
            )}
          </button>
        )}
      </div>

      <div className="source-card-actions">
        <a
          href={pdfUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="btn-view-source"
        >
          <span>View Source (Page {page})</span>
          <ExternalLink size={12} />
        </a>
      </div>
    </div>
  );
}
