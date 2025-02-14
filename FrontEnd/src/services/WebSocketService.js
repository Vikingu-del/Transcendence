export class WebSocketService {
    constructor() {
      this.userSocket = null;
      this.chatSocket = null;
      this.listeners = new Map();
    }
  
    connect(token) {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const host = window.location.host;
  
      // Initialize User WebSocket
      this.userSocket = new WebSocket(
        `${protocol}//${host}/api/user/ws/?token=${token}`
      );
  
      // Initialize Chat WebSocket
      this.chatSocket = new WebSocket(
        `${protocol}//${host}/api/chat/ws/?token=${token}`
      );
  
      this.setupUserSocketListeners();
      this.setupChatSocketListeners();
    }
  
    setupUserSocketListeners() {
      this.userSocket.onopen = () => {
        console.log('User WebSocket connected');
        this.notifyListeners('user', 'connected');
      };
  
      this.userSocket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.notifyListeners('user', 'message', data);
        } catch (error) {
          console.error('Error parsing user socket message:', error);
        }
      };
  
      this.userSocket.onclose = () => {
        console.log('User WebSocket disconnected');
        this.notifyListeners('user', 'disconnected');
      };
    }
  
    setupChatSocketListeners() {
      this.chatSocket.onopen = () => {
        console.log('Chat WebSocket connected');
        this.notifyListeners('chat', 'connected');
      };
  
      this.chatSocket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.notifyListeners('chat', 'message', data);
        } catch (error) {
          console.error('Error parsing chat socket message:', error);
        }
      };
  
      this.chatSocket.onclose = () => {
        console.log('Chat WebSocket disconnected');
        this.notifyListeners('chat', 'disconnected');
      };
    }
  
    addListener(type, event, callback) {
      const key = `${type}:${event}`;
      if (!this.listeners.has(key)) {
        this.listeners.set(key, new Set());
      }
      this.listeners.get(key).add(callback);
    }
  
    removeListener(type, event, callback) {
      const key = `${type}:${event}`;
      if (this.listeners.has(key)) {
        this.listeners.get(key).delete(callback);
      }
    }
  
    notifyListeners(type, event, data = null) {
      const key = `${type}:${event}`;
      if (this.listeners.has(key)) {
        this.listeners.get(key).forEach(callback => callback(data));
      }
    }
  
    sendUserMessage(message) {
      if (this.userSocket?.readyState === WebSocket.OPEN) {
        this.userSocket.send(JSON.stringify(message));
      }
    }
  
    sendChatMessage(message) {
      if (this.chatSocket?.readyState === WebSocket.OPEN) {
        this.chatSocket.send(JSON.stringify(message));
      }
    }
  
    disconnect() {
      if (this.userSocket) {
        this.userSocket.close();
      }
      if (this.chatSocket) {
        this.chatSocket.close();
      }
    }
  }