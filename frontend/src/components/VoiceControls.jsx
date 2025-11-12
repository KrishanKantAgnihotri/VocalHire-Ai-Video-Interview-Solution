/**
 * VoiceControls Component
 * 
 */
import React from 'react';

const VoiceControls = ({ 
  isListening, 
  isSpeaking, 
  onStartListening, 
  onStopListening,
  isWaitingForBot 
}) => {
  return (
    <div style={styles.container}>
      <div style={styles.controls}>
        {!isListening && !isSpeaking && !isWaitingForBot && (
          <button 
            onClick={onStartListening}
            style={{...styles.button, ...styles.primaryButton}}
          >
            Start Speaking
          </button>
        )}
        
        {isListening && (
          <button 
            onClick={onStopListening}
            style={{...styles.button, ...styles.dangerButton}}
          >
            Stop Recording
          </button>
        )}
        
        {isSpeaking && (
          <div style={styles.status}>
            <div style={styles.spinner}></div>
            <span>Bot is speaking...</span>
          </div>
        )}
        
        {isWaitingForBot && !isSpeaking && (
          <div style={styles.status}>
            <div style={styles.spinner}></div>
            <span>Processing your answer...</span>
          </div>
        )}
      </div>
      
      {isListening && (
        <div style={styles.recordingIndicator}>
          <div style={styles.pulse}></div>
          <span style={styles.recordingText}>Recording... Speak now</span>
        </div>
      )}
    </div>
  );
};

const styles = {
  container: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: '20px',
    marginTop: '20px'
  },
  controls: {
    display: 'flex',
    gap: '15px',
    alignItems: 'center'
  },
  button: {
    padding: '15px 30px',
    fontSize: '18px',
    borderRadius: '50px',
    border: 'none',
    cursor: 'pointer',
    fontWeight: '600',
    transition: 'all 0.3s ease',
    boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
  },
  primaryButton: {
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    color: 'white',
  },
  dangerButton: {
    background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    color: 'white',
  },
  status: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    fontSize: '16px',
    color: '#666',
  },
  spinner: {
    width: '20px',
    height: '20px',
    border: '3px solid #f3f3f3',
    borderTop: '3px solid #667eea',
    borderRadius: '50%',
    animation: 'spin 1s linear infinite',
  },
  recordingIndicator: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    padding: '10px 20px',
    background: 'rgba(255, 0, 0, 0.1)',
    borderRadius: '25px',
  },
  pulse: {
    width: '12px',
    height: '12px',
    borderRadius: '50%',
    background: 'red',
    animation: 'pulse 1.5s ease-in-out infinite',
  },
  recordingText: {
    color: '#d32f2f',
    fontWeight: '600',
  }
};

// Add CSS animations via style tag
if (typeof document !== 'undefined') {
  const styleSheet = document.createElement('style');
  styleSheet.textContent = `
    @keyframes spin {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }
    @keyframes pulse {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.3; }
    }
  `;
  document.head.appendChild(styleSheet);
}

export default VoiceControls;

