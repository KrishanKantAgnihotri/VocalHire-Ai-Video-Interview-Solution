/**
 * InterviewSession Component
 * Main component managing the interview flow
 */
import React, { useState, useEffect, useRef } from 'react';
import VoiceControls from './VoiceControls';
import FeedbackDisplay from './FeedbackDisplay';
import speechService from '../services/speechService';
import wsService from '../services/websocket';
import { FiCpu } from 'react-icons/fi';
import { FiEye } from 'react-icons/fi';
import { FiBookOpen } from 'react-icons/fi';

const InterviewSession = () => {
  const [isConnected, setIsConnected] = useState(false);
  const [isInterviewStarted, setIsInterviewStarted] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isWaitingForBot, setIsWaitingForBot] = useState(false);
  const [currentQuestion, setCurrentQuestion] = useState('');
  const [progress, setProgress] = useState('');
  const [conversation, setConversation] = useState([]);
  const [feedback, setFeedback] = useState(null);
  const [showFeedback, setShowFeedback] = useState(false);
  const [error, setError] = useState('');
  
  const conversationEndRef = useRef(null);
  
  // Auto-scroll to bottom of conversation
  useEffect(() => {
    conversationEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [conversation]);
  
  // Cleanup on unmount
  useEffect(() => {
    return () => {
      // Cleanup WebSocket handlers and connections
      if (isInterviewStarted) {
        wsService.disconnect();
        speechService.stopSpeaking();
        speechService.stopListening();
      }
    };
  }, [isInterviewStarted]);
  
  // Initialize WebSocket connection
  const startInterview = async () => {
    try {
      setError('');
      
      // Check browser support
      if (!speechService.isRecognitionSupported()) {
        setError('Speech recognition is not supported in your browser. Please use Chrome or Edge.');
        return;
      }
      
      // Connect to WebSocket
      await wsService.connect('ws://localhost:8000/ws/interview');
      setIsConnected(true);
      setIsInterviewStarted(true);
      
      // Setup message handlers
      wsService.on('session_start', handleSessionStart);
      wsService.on('question', handleQuestion);
      wsService.on('feedback', handleFeedback);
      wsService.on('session_end', handleSessionEnd);
      wsService.on('status', handleStatus);
      wsService.on('error', handleError);
      
    } catch (error) {
      console.error('Failed to start interview:', error);
      setError('Failed to connect to server. Please make sure the backend is running.');
    }
  };
  
  // Handle session start
  const handleSessionStart = (message) => {
    console.log('Session started:', message.content);
    addToConversation('system', 'Interview session started');
  };
  
  // Handle question from bot
  const handleQuestion = (message) => {
    const questionText = message.content;
    setCurrentQuestion(questionText);
    setIsWaitingForBot(false);
    
    // Update progress if available
    if (message.metadata?.progress) {
      setProgress(message.metadata.progress);
    }
    
    // Add to conversation
    const isGreeting = message.metadata?.is_greeting;
    const isFollowUp = message.metadata?.is_follow_up;
    
    let label = 'Interviewer';
    if (isGreeting) label = 'Interviewer (Welcome)';
    if (isFollowUp) label = 'Interviewer (Follow-up)';
    
    addToConversation('bot', questionText, label);
    
    // Speak the question
    setIsSpeaking(true);
    speechService.speak(questionText, () => {
      setIsSpeaking(false);
    });
  };
  
  // Handle feedback
  const handleFeedback = (message) => {
    setFeedback(message);
    setShowFeedback(true);
    addToConversation('bot', 'Interview completed! View your feedback.', 'System');
    
    // Speak feedback summary
    const summary = "Interview completed! You can now view your detailed feedback.";
    speechService.speak(summary);
  };
  
  // Handle session end
  const handleSessionEnd = (message) => {
    addToConversation('system', message.content);
  };
  
  // Handle status updates
  const handleStatus = (message) => {
    addToConversation('system', message.content);
  };
  
  // Handle errors
  const handleError = (message) => {
    setError(message.content);
    setIsWaitingForBot(false);
  };
  
  // Start listening for user's answer
  const startListening = () => {
    if (isSpeaking) {
      speechService.stopSpeaking();
      setIsSpeaking(false);
    }
    
    speechService.startListening(
      (transcript, confidence) => {
        // Got speech result
        setIsListening(false);
        handleUserAnswer(transcript);
      },
      (error) => {
        // Error in recognition
        setIsListening(false);
        setError(`Speech recognition error: ${error}`);
      }
    );
    
    setIsListening(true);
  };
  
  // Stop listening
  const stopListening = () => {
    speechService.stopListening();
    setIsListening(false);
  };
  
  // Handle user's answer
  const handleUserAnswer = (answer) => {
    if (!answer || !answer.trim()) {
      setError('No speech detected. Please try again.');
      return;
    }
    
    // Add to conversation
    addToConversation('user', answer);
    
    // Send to backend
    wsService.sendAnswer(answer);
    setIsWaitingForBot(true);
  };
  
  // Add message to conversation
  const addToConversation = (type, content, label = null) => {
    setConversation(prev => [...prev, {
      type,
      content,
      label: label || (type === 'bot' ? 'Interviewer' : type === 'user' ? 'You' : 'System'),
      timestamp: new Date().toLocaleTimeString()
    }]);
  };
  
  // End interview
  const endInterview = () => {
    wsService.disconnect();
    speechService.stopSpeaking();
    speechService.stopListening();
    setIsConnected(false);
    setIsInterviewStarted(false);
    setConversation([]);
    setFeedback(null);
    setShowFeedback(false);
  };
  
  // Restart interview
  const restartInterview = () => {
    endInterview();
    setTimeout(() => startInterview(), 500);
  };
  
  if (!isInterviewStarted) {
    return (
      <div style={styles.container}>
        <div style={styles.welcomeCard}>
          <h1 style={styles.welcomeTitle}>Welcome to VocalHire</h1>
          <p style={styles.welcomeText}>
            Your AI-powered mock interview practice platform. Practice your interview skills 
            with realistic voice-based conversations and receive personalized feedback.
          </p>
          
          <div style={styles.features}>
            <div style={styles.feature}>
              <span style={styles.featureIcon}><FiCpu/></span>
              <span style={styles.featureText}>Voice-based interaction</span>
            </div>
            <div style={styles.feature}>
              <span style={styles.featureIcon}><FiEye/></span>
              <span style={styles.featureText}>AI interviewer</span>
            </div>
            <div style={styles.feature}>
              <span style={styles.featureIcon}><FiBookOpen/></span>
              <span style={styles.featureText}>Detailed feedback</span>
            </div>
          </div>
          
          {error && (
            <div style={styles.errorBox}>
              {error}
            </div>
          )}
          
          <button onClick={startInterview} style={styles.startButton}>
            Start Interview Practice
          </button>
          
          <p style={styles.note}>
            Note: This application uses your browser's speech recognition. 
            Please allow microphone access when prompted.
          </p>
        </div>
      </div>
    );
  }
  
  return (
    <div style={styles.container}>
      <div style={styles.interviewCard}>
        {/* Header */}
        <div style={styles.header}>
          <div>
            <h2 style={styles.title}>Mock Interview Session</h2>
            {progress && <p style={styles.progress}>{progress}</p>}
          </div>
          <button onClick={endInterview} style={styles.endButton}>
            End Interview
          </button>
        </div>
        
        {/* Error Display */}
        {error && (
          <div style={styles.errorBox}>
             {error}
          </div>
        )}
        
        {/* Conversation Display */}
        <div style={styles.conversationContainer}>
          {conversation.map((msg, idx) => (
            <div 
              key={idx} 
              style={{
                ...styles.message,
                ...(msg.type === 'user' ? styles.userMessage : 
                    msg.type === 'bot' ? styles.botMessage : 
                    styles.systemMessage)
              }}
            >
              <div style={styles.messageLabel}>{msg.label}</div>
              <div style={styles.messageContent}>{msg.content}</div>
              <div style={styles.messageTime}>{msg.timestamp}</div>
            </div>
          ))}
          <div ref={conversationEndRef} />
        </div>
        
        {/* Voice Controls */}
        <VoiceControls 
          isListening={isListening}
          isSpeaking={isSpeaking}
          isWaitingForBot={isWaitingForBot}
          onStartListening={startListening}
          onStopListening={stopListening}
        />
      </div>
      
      {/* Feedback Modal */}
      {showFeedback && (
        <FeedbackDisplay 
          feedback={feedback}
          onClose={() => {
            setShowFeedback(false);
            endInterview();
          }}
        />
      )}
    </div>
  );
};

const styles = {
  container: {
    minHeight: '100vh',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '20px',
  },
  welcomeCard: {
    background: 'white',
    borderRadius: '20px',
    padding: '50px',
    maxWidth: '600px',
    textAlign: 'center',
    boxShadow: '0 20px 60px rgba(0, 0, 0, 0.2)',
  },
  welcomeTitle: {
    fontSize: '36px',
    marginBottom: '20px',
    color: '#333',
  },
  welcomeText: {
    fontSize: '18px',
    lineHeight: '1.6',
    color: '#666',
    marginBottom: '30px',
  },
  features: {
    display: 'flex',
    justifyContent: 'space-around',
    marginBottom: '40px',
    flexWrap: 'wrap',
    gap: '20px',
  },
  feature: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: '10px',
  },
  featureIcon: {
    fontSize: '32px',
  },
  featureText: {
    fontSize: '14px',
    color: '#666',
  },
  startButton: {
    padding: '18px 40px',
    fontSize: '20px',
    borderRadius: '50px',
    border: 'none',
    cursor: 'pointer',
    fontWeight: '600',
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    color: 'white',
    boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
    marginBottom: '20px',
  },
  note: {
    fontSize: '14px',
    color: '#999',
    marginTop: '20px',
  },
  interviewCard: {
    background: 'white',
    borderRadius: '20px',
    padding: '30px',
    maxWidth: '900px',
    width: '100%',
    minHeight: '600px',
    display: 'flex',
    flexDirection: 'column',
    boxShadow: '0 20px 60px rgba(0, 0, 0, 0.2)',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '20px',
    paddingBottom: '20px',
    borderBottom: '1px solid #e0e0e0',
  },
  title: {
    margin: 0,
    fontSize: '24px',
    color: '#333',
  },
  progress: {
    margin: '5px 0 0 0',
    fontSize: '14px',
    color: '#667eea',
  },
  endButton: {
    padding: '10px 20px',
    fontSize: '14px',
    borderRadius: '25px',
    border: '1px solid #ddd',
    background: 'white',
    cursor: 'pointer',
    color: '#666',
  },
  conversationContainer: {
    flex: 1,
    overflowY: 'auto',
    marginBottom: '20px',
    padding: '10px',
    minHeight: '300px',
  },
  message: {
    marginBottom: '20px',
    padding: '15px',
    borderRadius: '15px',
    maxWidth: '80%',
  },
  userMessage: {
    background: 'linear-gradient(135deg, #667eea15 0%, #764ba215 100%)',
    marginLeft: 'auto',
  },
  botMessage: {
    background: '#f5f5f5',
    marginRight: 'auto',
  },
  systemMessage: {
    background: '#fff3cd',
    marginLeft: 'auto',
    marginRight: 'auto',
    textAlign: 'center',
    maxWidth: '60%',
    fontSize: '14px',
  },
  messageLabel: {
    fontSize: '12px',
    fontWeight: '600',
    color: '#667eea',
    marginBottom: '5px',
  },
  messageContent: {
    fontSize: '16px',
    color: '#333',
    lineHeight: '1.5',
  },
  messageTime: {
    fontSize: '11px',
    color: '#999',
    marginTop: '5px',
  },
  errorBox: {
    background: '#ffebee',
    color: '#c62828',
    padding: '15px',
    borderRadius: '10px',
    marginBottom: '15px',
    fontSize: '14px',
  },
};

export default InterviewSession;

