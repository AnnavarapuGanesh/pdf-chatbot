import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload } from 'lucide-react';

const PDFUploader = ({ onUploadStart, onUploadEnd, isUploading, uploadProgress }) => {
  const onDrop = useCallback(
    async (acceptedFiles) => {
      if (acceptedFiles.length === 0 || isUploading) return;
      onUploadStart(acceptedFiles);
    },
    [isUploading, onUploadStart]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
    },
    disabled: isUploading,
    multiple: true,
  });

  return (
    <div 
      {...getRootProps()} 
      className={`upload-zone ${isDragActive ? 'active' : ''}`}
    >
      <input {...getInputProps()} />
      <Upload className="upload-icon" size={28} />
      {isUploading ? (
        <div style={{ width: '100%' }}>
          <p className="upload-text" style={{ fontWeight: 600, color: 'var(--text-primary)' }}>
            Processing documents...
          </p>
          <div className="progress-bar-container">
            <div 
              className="progress-bar" 
              style={{ width: `${uploadProgress}%` }}
            ></div>
          </div>
        </div>
      ) : (
        <p className="upload-text">
          {isDragActive ? (
            <strong>Drop the PDFs here...</strong>
          ) : (
            <>
              Drag & drop **PDF files** here,<br />
              or click to browse
            </>
          )}
        </p>
      )}
    </div>
  );
};

export default PDFUploader;
