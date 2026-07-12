import React from 'react';
import { Database, Trash2, FileText } from 'lucide-react';
import PDFUploader from './PDFUploader';

const Sidebar = ({ 
  files, 
  onUploadStart, 
  onUploadEnd, 
  isUploading, 
  uploadProgress, 
  onClearAll 
}) => {
  return (
    <div className="sidebar">
      <div className="sidebar-title">
        <Database size={22} style={{ color: 'var(--accent-blue)' }} />
        <span>Document Portal</span>
      </div>

      {/* PDF Uploader area */}
      <PDFUploader 
        onUploadStart={onUploadStart}
        onUploadEnd={onUploadEnd}
        isUploading={isUploading}
        uploadProgress={uploadProgress}
      />

      {/* Uploaded Files list */}
      <div className="file-list-section">
        <h3 className="section-label">Indexed Documents</h3>
        <div className="file-list">
          {files.length === 0 ? (
            <div className="empty-files">No documents uploaded yet.</div>
          ) : (
            files.map((file, index) => (
              <div key={index} className="file-item">
                <FileText size={16} style={{ color: 'var(--accent-blue)', flexShrink: 0 }} />
                <span>{file}</span>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Clear All action button */}
      <button 
        className="clear-button" 
        onClick={onClearAll}
        disabled={isUploading}
      >
        <Trash2 size={16} />
        <span>Clear Database</span>
      </button>
    </div>
  );
};

export default Sidebar;
