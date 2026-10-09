import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { ChevronDown, ChevronUp, FileText } from 'lucide-react';

const MessageBubble = ({ message }) => {
  const isUser = message.role === 'user';
  const [showSources, setShowSources] = useState(false);

  return (
    <div className={`message-row ${isUser ? 'user' : 'bot'}`}>
      <div className="message-bubble">
        {/* Render uploaded image if present in the message */}
        {message.image && (
          <img 
            src={message.image.startsWith('data:') ? message.image : `data:image/jpeg;base64,${message.image}`} 
            className="chat-bubble-image" 
            alt="Attached upload" 
          />
        )}
        
        {/* Render markdown content */}
        {isUser ? (
          <div>{message.content}</div>
        ) : (
          <ReactMarkdown>{message.content}</ReactMarkdown>
        )}

        {/* Citations & Confidence Info */}
        {!isUser && ((message.sources && message.sources.length > 0) || (message.confidence !== undefined && message.confidence !== null)) && (
          <div className="citations-wrapper">
            <div className="bot-meta-footer">
              {message.sources && message.sources.length > 0 && (
                <button 
                  className="citations-trigger" 
                  onClick={() => setShowSources(!showSources)}
                >
                  {showSources ? (
                    <>Hide Sources <ChevronUp size={14} /></>
                  ) : (
                    <>View Sources ({message.sources.length}) <ChevronDown size={14} /></>
                  )}
                </button>
              )}
              {message.confidence !== undefined && message.confidence !== null && (
                <div className="overall-confidence-badge">
                  Answer Confidence: <span className="confidence-value">{message.confidence}%</span>
                </div>
              )}
            </div>
            
            {message.sources && message.sources.length > 0 && (
              <div className={`citations-drawer ${showSources ? 'open' : ''}`}>
                {message.sources.map((src, idx) => (
                  <div key={idx} className="citation-card">
                    <div className="citation-meta">
                      <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                        <FileText size={12} /> {src.source}
                      </span>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        {src.score !== undefined && src.score !== null && (
                          <span className="relevance-score-badge">
                            {src.score}% Match
                          </span>
                        )}
                        <span>Page {src.page}</span>
                      </div>
                    </div>
                    <div className="citation-text">"{src.text}"</div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default MessageBubble;
