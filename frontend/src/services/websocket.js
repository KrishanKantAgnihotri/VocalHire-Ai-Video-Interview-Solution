/**
 * WebSocket Service
 *
 */

class WebSocketService {
  constructor() {
    this.ws = null;
    this.sessionId = null;
    this.isConnected = false;
    this.messageHandlers = new Map();
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 3;
  }
  
  /**
   * Connect to WebSocket server
   * @param {string} url - WebSocket URL
   * @returns {Promise} Resolves when connected
   */
  connect(url = 'ws://localhost:8000/ws/interview') {
    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(url);
        
        this.ws.onopen = () => {
          console.log('WebSocket connected');
          this.isConnected = true;
          this.reconnectAttempts = 0;
          resolve();
        };
        
        this.ws.onmessage = (event) => {
          this._handleMessage(event);
        };
        
        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          this.isConnected = false;
          reject(error);
        };
        
        this.ws.onclose = () => {
          console.log('🔌 WebSocket disconnected');
          this.isConnected = false;
          this._handleDisconnect();
        };
        
      } catch (error) {
        console.error('Failed to connect:', error);
        reject(error);
      }
    });
  }
  
  /**
   * Disconnect from WebSocket server
   */
  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
      this.isConnected = false;
      this.sessionId = null;
    }
  }
  
  /**
   * Send message to server
   * @param {Object} message - Message object to send
   */
  send(message) {
    // Check actual WebSocket state instead of just flag
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.error('WebSocket not connected or not ready');
      return false;
    }
    
    try {
      const messageStr = typeof message === 'string' 
        ? message 
        : JSON.stringify(message);
      
      this.ws.send(messageStr);
      console.log('📤 Sent:', message);
      return true;
    } catch (error) {
      console.error('Error sending message:', error);
      return false;
    }
  }
  
  /**
   * Send answer to interview question
   * @param {string} answer - User's answer text
   */
  sendAnswer(answer) {
    this.send({
      type: 'answer',
      content: answer,
      session_id: this.sessionId,
      timestamp: new Date().toISOString()
    });
  }
  
  /**
   * Register handler for specific message type
   * @param {string} type - Message type
   * @param {Function} handler - Handler function
   */
  on(type, handler) {
    this.messageHandlers.set(type, handler);
  }
  
  /**
   * Remove handler for specific message type
   * @param {string} type - Message type
   */
  off(type) {
    this.messageHandlers.delete(type);
  }
  
  /**
   * Handle incoming message
   * @private
   */
  _handleMessage(event) {
    try {
      const message = JSON.parse(event.data);
      console.log('📥 Received:', message.type, message);
      
      // Store session ID from session_start message
      if (message.type === 'session_start') {
        this.sessionId = message.content;
      }
      
      // Call registered handler for this message type
      const handler = this.messageHandlers.get(message.type);
      if (handler) {
        handler(message);
      }
      
      // Call generic message handler if registered
      const allHandler = this.messageHandlers.get('*');
      if (allHandler) {
        allHandler(message);
      }
      
    } catch (error) {
      console.error('Error parsing message:', error);
    }
  }
  
  /**
   * Handle disconnection
   * @private
   */
  _handleDisconnect() {
    // Could implement reconnection logic here
    const disconnectHandler = this.messageHandlers.get('disconnect');
    if (disconnectHandler) {
      disconnectHandler();
    }
  }
  
  /**
   * Check if connected
   * @returns {boolean}
   */
  isWebSocketConnected() {
    return this.isConnected && this.ws && this.ws.readyState === WebSocket.OPEN;
  }
}

// Export singleton instance
export default new WebSocketService();

