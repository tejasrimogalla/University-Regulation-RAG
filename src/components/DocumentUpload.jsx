import React, { useState, useRef } from 'react';
import { UploadCloud, FileCheck, X, AlertCircle } from 'lucide-react';

export default function DocumentUpload({ onUpload, uploading }) {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [uploadError, setUploadError] = useState(null);
  const fileInputRef = useRef(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const validateAndAddFiles = (fileList) => {
    setUploadError(null);
    const validPdfs = [];
    const rejected = [];

    Array.from(fileList).forEach((file) => {
      if (file.name.toLowerCase().endsWith('.pdf')) {
        validPdfs.push(file);
      } else {
        rejected.push(file.name);
      }
    });

    if (rejected.length > 0) {
      setUploadError(`Rejected non-PDF files: ${rejected.join(', ')}. Only .pdf files are accepted.`);
    }

    if (validPdfs.length > 0) {
      setSelectedFiles((prev) => [...prev, ...validPdfs]);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      validateAndAddFiles(e.dataTransfer.files);
    }
  };

  const handleFileInput = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      validateAndAddFiles(e.target.files);
    }
  };

  const handleRemoveFile = (index) => {
    setSelectedFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const handleStartUpload = async () => {
    if (selectedFiles.length === 0 || uploading) return;
    try {
      await onUpload(selectedFiles);
      setSelectedFiles([]);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (err) {
      setUploadError(err.message || 'Failed to upload files.');
    }
  };

  return (
    <div className="document-upload-card">
      <div
        className={`dropzone ${dragActive ? 'dropzone-active' : ''}`}
        onDragEnter={handleDrag}
        onDragOver={handleDrag}
        onDragLeave={handleDrag}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".pdf,application/pdf"
          onChange={handleFileInput}
          style={{ display: 'none' }}
        />
        <div className="dropzone-content">
          <UploadCloud size={24} className="dropzone-icon text-indigo" />
          <p className="dropzone-text">
            <strong>Click to upload</strong> or drag & drop PDFs
          </p>
          <span className="dropzone-subtext">University regulations, handbooks, rules</span>
        </div>
      </div>

      {uploadError && (
        <div className="upload-error-banner">
          <AlertCircle size={14} className="mr-1 flex-shrink-0" />
          <span>{uploadError}</span>
        </div>
      )}

      {selectedFiles.length > 0 && (
        <div className="selected-files-list">
          <div className="selected-files-header">
            <span>Selected ({selectedFiles.length}):</span>
            <button
              className="btn-link text-danger"
              onClick={() => setSelectedFiles([])}
              disabled={uploading}
            >
              Clear
            </button>
          </div>
          <div className="selected-files-scroll">
            {selectedFiles.map((file, idx) => (
              <div key={idx} className="selected-file-chip">
                <FileCheck size={12} className="text-emerald mr-1 flex-shrink-0" />
                <span className="file-name" title={file.name}>{file.name}</span>
                <span className="file-size">({(file.size / 1024).toFixed(1)} KB)</span>
                <button
                  className="btn-remove-chip"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleRemoveFile(idx);
                  }}
                  disabled={uploading}
                >
                  <X size={12} />
                </button>
              </div>
            ))}
          </div>

          <button
            className="btn-primary btn-block mt-2"
            onClick={handleStartUpload}
            disabled={uploading}
          >
            {uploading ? (
              <>
                <span className="btn-spinner"></span>
                <span>Uploading PDFs...</span>
              </>
            ) : (
              `Upload ${selectedFiles.length} File${selectedFiles.length > 1 ? 's' : ''}`
            )}
          </button>
        </div>
      )}
    </div>
  );
}
