import React from 'react';

const TypingIndicator = () => {
  return (
    <div className="typing-bubble-container">
      <div className="typing-indicator-bubble">
        <div className="typing-dot dot-bounce"></div>
        <div className="typing-dot dot-bounce"></div>
        <div className="typing-dot dot-bounce"></div>
      </div>
    </div>
  );
};

export default TypingIndicator;
