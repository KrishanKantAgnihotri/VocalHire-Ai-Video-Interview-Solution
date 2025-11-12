/**
 * Speech Service - Web Speech API Wrapper
 * Handles speech recognition (STT) and speech synthesis (TTS)
 */

class SpeechService {
  constructor() {
    // Check for Web Speech API support
    this.recognition = null;
    this.synthesis = window.speechSynthesis;
    this.isListening = false;
    this.onResultCallback = null;
    this.onErrorCallback = null;
    
    // Initialize Speech Recognition
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      this.recognition = new SpeechRecognition();
      
      // Configure recognition
      this.recognition.continuous = false; // Stop after one result
      this.recognition.interimResults = false; // Only final results
      this.recognition.lang = 'en-IN'; // Indian English
      this.recognition.maxAlternatives = 1;
      
      // Setup event handlers
      this.recognition.onresult = this._handleResult.bind(this);
      this.recognition.onerror = this._handleError.bind(this);
      this.recognition.onend = this._handleEnd.bind(this);
    }
  }
  
  /**
   * Check if speech recognition is supported
   */
  isRecognitionSupported() {
    return this.recognition !== null;
  }
  
  /**
   * Check if speech synthesis is supported
   */
  isSynthesisSupported() {
    return this.synthesis !== null;
  }
  
  /**
   * Start listening for speech input
   * @param {Function} onResult - Callback for speech results
   * @param {Function} onError - Callback for errors
   */
  startListening(onResult, onError) {
    if (!this.recognition) {
      onError && onError('Speech recognition not supported');
      return;
    }
    
    if (this.isListening) {
      console.log('Already listening');
      return;
    }
    
    this.onResultCallback = onResult;
    this.onErrorCallback = onError;
    
    try {
      this.recognition.start();
      this.isListening = true;
      console.log('Started listening...');
    } catch (error) {
      console.error('Error starting recognition:', error);
      onError && onError(error.message);
    }
  }
  
  /**
   * Stop listening for speech input
   */
  stopListening() {
    if (!this.recognition || !this.isListening) {
      return;
    }
    
    try {
      this.recognition.stop();
      this.isListening = false;
      console.log('Stopped listening');
    } catch (error) {
      console.error('Error stopping recognition:', error);
    }
  }
  
  /**
   * Speak text using speech synthesis
   * @param {string} text - Text to speak
   * @param {Function} onEnd - Callback when speech ends
   */
  speak(text, onEnd) {
    if (!this.synthesis) {
      console.error('Speech synthesis not supported');
      onEnd && onEnd();
      return;
    }
    
    // Cancel any ongoing speech
    this.synthesis.cancel();
    
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'en-IN'; // Indian English
    utterance.rate = 0.9; // Slightly slower for clarity
    utterance.pitch = 1.0;
    utterance.volume = 1.0;
    
    utterance.onend = () => {
      console.log('Finished speaking');
      onEnd && onEnd();
    };
    
    utterance.onerror = (event) => {
      console.error('Speech synthesis error:', event);
      onEnd && onEnd();
    };
    
    this.synthesis.speak(utterance);
    console.log('Speaking:', text.substring(0, 50) + '...');
  }
  
  /**
   * Stop any ongoing speech
   */
  stopSpeaking() {
    if (this.synthesis) {
      this.synthesis.cancel();
    }
  }
  
  /**
   * Check if currently speaking
   */
  isSpeaking() {
    return this.synthesis && this.synthesis.speaking;
  }
  
  /**
   * Handle speech recognition result
   * @private
   */
  _handleResult(event) {
    const transcript = event.results[0][0].transcript;
    const confidence = event.results[0][0].confidence;
    
    console.log('Recognized:', transcript, 'Confidence:', confidence);
    
    if (this.onResultCallback) {
      this.onResultCallback(transcript, confidence);
    }
  }
  
  /**
   * Handle speech recognition error
   * @private
   */
  _handleError(event) {
    console.error('Speech recognition error:', event.error);
    this.isListening = false;
    
    if (this.onErrorCallback) {
      this.onErrorCallback(event.error);
    }
  }
  
  /**
   * Handle speech recognition end
   * @private
   */
  _handleEnd() {
    console.log('Speech recognition ended');
    this.isListening = false;
  }
}

// Export singleton instance
export default new SpeechService();

