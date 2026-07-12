import React, { useState, useEffect } from 'react';
import { Sun, Moon } from 'lucide-react';
import Sidebar from './components/Sidebar';
import ChatWindow from './components/ChatWindow';
import { uploadPDFs, askQuestion, getFiles, clearAll } from './api';

function App() {
  const [messages, setMessages] = useState([]);
  const [files, setFiles] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isWaiting, setIsWaiting] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(true);

  // Sync theme class to document body
  useEffect(() => {
    if (isDarkMode) {
      document.body.classList.remove('light-theme');
    } else {
      document.body.classList.add('light-theme');
    }
  }, [isDarkMode]);

  // Load indexed files list on startup
  useEffect(() => {
    const loadFiles = async () => {
      try {
        const data = await getFiles();
        if (data && data.files) {
          setFiles(data.files);
        }
      } catch (err) {
        console.error('Failed to load initial file list:', err);
      }
    };
    loadFiles();
  }, []);

  // Handle PDF file ingestion
  const handleUploadStart = async (acceptedFiles) => {
    setIsUploading(true);
    setUploadProgress(10);
    
    // Simulate upload progress
    const progressInterval = setInterval(() => {
      setUploadProgress((prev) => {
        if (prev >= 90) {
          clearInterval(progressInterval);
          return 90;
        }
        return prev + 15;
      });
    }, 200);

    try {
      await uploadPDFs(acceptedFiles);
      
      clearInterval(progressInterval);
      setUploadProgress(100);
      
      // Fetch updated files list
      const data = await getFiles();
      setFiles(data.files || []);
      
      // Reset progress
      setTimeout(() => {
        setIsUploading(false);
        setUploadProgress(0);
      }, 500);

      // Add success confirmation message
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: `✅ Successfully indexed **${acceptedFiles.length} file(s)** to the RAG database. You can now ask questions about them!`,
          sources: [],
        },
      ]);
    } catch (err) {
      clearInterval(progressInterval);
      setIsUploading(false);
      setUploadProgress(0);
      alert('Error uploading PDF files. Make sure the backend server is running.');
      console.error(err);
    }
  };

  // Handle user Q&A submission
  const handleSendMessage = async (text, imageBase64) => {
    // 1. Add user message locally
    const userMsg = {
      role: 'user',
      content: text,
      // Store preview url locally to render thumbnail in bubble
      image: imageBase64 ? `data:image/jpeg;base64,${imageBase64}` : null,
    };
    setMessages((prev) => [...prev, userMsg]);
    setIsWaiting(true);

    try {
      // 2. Query FastAPI backend
      const response = await askQuestion(text, imageBase64);
      
      // 3. Add bot message response
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: response.answer,
          sources: response.sources || [],
        },
      ]);
    } catch (err) {
      console.error(err);
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: `❌ Error communicating with the RAG backend. Please verify your local Uvicorn server is running on port 8000 and Ollama is active.`,
          sources: [],
        },
      ]);
    } finally {
      setIsWaiting(false);
    }
  };

  // Clear application state
  const handleClearAll = async () => {
    if (window.confirm('Are you sure you want to clear all indexed documents and chat history?')) {
      try {
        await clearAll();
        setMessages([]);
        setFiles([]);
      } catch (err) {
        console.error(err);
        alert('Failed to clear local indices.');
      }
    }
  };

  return (
    <div className="app-container">
      {/* Sidebar document manager */}
      <Sidebar 
        files={files}
        onUploadStart={handleUploadStart}
        isUploading={isUploading}
        uploadProgress={uploadProgress}
        onClearAll={handleClearAll}
      />

      {/* Main chat window */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        <div className="chat-header">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <h1 className="chat-title-gradient">PDF Q&A Chatbot v2.0</h1>
              <div className="chat-subtitle">
                Local & offline Retrieval-Augmented Generation powered by Ollama Llama 3.2 and LLaVA
              </div>
            </div>
            <button 
              onClick={() => setIsDarkMode(!isDarkMode)} 
              className="theme-toggle-btn"
              title={isDarkMode ? "Switch to Light Mode" : "Switch to Dark Mode"}
            >
              {isDarkMode ? <Sun size={20} /> : <Moon size={20} />}
            </button>
          </div>
        </div>
        
        <ChatWindow 
          messages={messages}
          onSendMessage={handleSendMessage}
          isWaiting={isWaiting}
        />
      </div>
    </div>
  );
}

export default App;
