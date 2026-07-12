import React, { useState, useRef, useEffect } from 'react';
import { Send, Image, X, MessageSquare, Sparkles } from 'lucide-react';
import MessageBubble from './MessageBubble';
import TypingIndicator from './TypingIndicator';

const ChatWindow = ({ messages, onSendMessage, isWaiting }) => {
  const [inputText, setInputText] = useState('');
  const [attachedImage, setAttachedImage] = useState(null); // { preview: string, base64: string }
  
  const chatBottomRef = useRef(null);
  const fileInputRef = useRef(null);
  const textareaRef = useRef(null);

  // Auto-scroll to the bottom of the chat when messages or indicator changes
  useEffect(() => {
    chatBottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isWaiting]);

  // Auto-adjust textarea height on typing
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
    }
  }, [inputText]);

  // Handle Image Selection and Canvas-based 1024px compression
  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      const img = document.createElement('img');
      img.onload = () => {
        const canvas = document.createElement('canvas');
        let width = img.width;
        let height = img.height;
        const maxDimension = 1024;

        // Resize if exceeding max dimension
        if (width > maxDimension || height > maxDimension) {
          if (width > height) {
            height = Math.round((height * maxDimension) / width);
            width = maxDimension;
          } else {
            width = Math.round((width * maxDimension) / height);
            height = maxDimension;
          }
        }

        canvas.width = width;
        canvas.height = height;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(img, 0, 0, width, height);

        // Convert canvas image to compressed base64 JPEG
        const compressedBase64 = canvas.toDataURL('image/jpeg', 0.8);
        setAttachedImage({
          preview: compressedBase64,
          base64: compressedBase64.split(',')[1] // Strip base64 metadata header
        });
        
        // Reset file input value
        if (fileInputRef.current) fileInputRef.current.value = '';
      };
      img.src = event.target.result;
    };
    reader.readAsDataURL(file);
  };

  const handleSend = () => {
    if ((!inputText.trim() && !attachedImage) || isWaiting) return;
    
    // Pass question text and image base64 back to parent
    onSendMessage(inputText, attachedImage ? attachedImage.base64 : null);
    
    // Clear input states
    setInputText('');
    setAttachedImage(null);
    if (textareaRef.current) textareaRef.current.style.height = 'auto';
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="chat-container">
      {/* Scrollable Conversation View */}
      <div className="chat-window">
        {messages.length === 0 ? (
          <div className="empty-chat">
            <h2 className="empty-chat-title">Welcome to PDF QA Chatbot</h2>
            <p className="empty-chat-text">
              Upload PDF documents in the sidebar and ask questions about their content. 
              You can also attach an image to examine it with the model locally.
            </p>
          </div>
        ) : (
          messages.map((msg, index) => (
            <MessageBubble key={index} message={msg} />
          ))
        )}
        
        {/* Animated bounce indicator while LLM is generating */}
        {isWaiting && <TypingIndicator />}
        <div ref={chatBottomRef} />
      </div>

      {/* Input panel with dynamic mode label and compression */}
      <div className="input-area">
        {/* Dynamic Mode Indicator */}
        <div className={`mode-indicator ${attachedImage ? 'vision' : 'text'}`}>
          {attachedImage ? (
            <><Sparkles size={12} /> Vision Mode (LLaVA)</>
          ) : (
            <><MessageSquare size={12} /> Text Mode (Llama 3.2)</>
          )}
        </div>

        {/* Thumbnail preview above input area */}
        {attachedImage && (
          <div className="thumbnail-preview-container">
            <div className="thumbnail-preview">
              <img src={attachedImage.preview} className="thumbnail-image" alt="upload preview" />
              <button className="thumbnail-remove" onClick={() => setAttachedImage(null)}>
                <X size={10} />
              </button>
            </div>
          </div>
        )}

        {/* Form Controls */}
        <div className="input-row">
          {/* File Input for Attachments */}
          <input 
            type="file" 
            ref={fileInputRef} 
            onChange={handleImageChange} 
            accept="image/*" 
            style={{ display: 'none' }} 
          />
          <button 
            type="button" 
            className="icon-button" 
            onClick={() => fileInputRef.current?.click()}
            disabled={isWaiting}
            title="Attach image"
          >
            <Image size={20} />
          </button>

          {/* Text Area */}
          <textarea
            ref={textareaRef}
            className="chat-textarea"
            placeholder={attachedImage ? "Describe what to check in the image..." : "Ask a question about your documents..."}
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isWaiting}
          />

          {/* Send Action */}
          <button 
            type="button" 
            className="icon-button send-button" 
            onClick={handleSend}
            disabled={(!inputText.trim() && !attachedImage) || isWaiting}
            title="Send message"
          >
            <Send size={16} />
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatWindow;
