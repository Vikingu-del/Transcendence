<template>
  <div class="friends-container">
    <!-- Friends Section with Chat -->
    <div class="profile-section">
      <h2>Friends</h2>
      <div v-if="profile.friends && profile.friends.length > 0">
        <div v-for="friend in profile.friends" :key="friend.id" class="profile-item">
          <img :src="friend.avatar" :alt="friend.display_name" class="profile-avatar">
          <span class="profile-name">{{ friend.display_name }}</span>
          <span :class="['status', friend.is_online ? 'online' : 'offline']">
            {{ friend.is_online ? 'Online' : 'Offline' }}
          </span>
          <div class="friend-actions">
            <button @click="startChat(friend)" class="btn primary-btn">Chat</button>
            <button @click="removeFriend(friend.id)" class="btn secondary-btn">Remove</button>
          </div>
        </div>
      </div>
      <p v-else>No friends yet</p>
    </div>

    <!-- Chat Section -->
    <div v-if="showChat" class="chat-container">
      <div class="chat-header">
        <h4 class="chat-title">Chat with {{ activeChat }}</h4>
        <button @click="closeChat" class="btn secondary-btn">Close</button>
      </div>
      <div class="chat-messages" ref="chatMessages">
        <div v-for="message in messages" 
          :key="message.id" 
          :class="['message', { 
            'message-sent': message.sender === parseInt(currentUserId),
            'message-received': message.sender !== parseInt(currentUserId)
          }]">
          <div class="message-content" :class="{ 
            'content-sent': parseInt(message.sender) === parseInt(currentUserId),
            'content-received': parseInt(message.sender) !== parseInt(currentUserId)
          }">
            <div class="message-header">
              <small class="message-sender">
                {{ parseInt(message.sender) === parseInt(currentUserId) ? '' : activeChat }}
              </small>
            </div>
            <span class="message-text">{{ message.text }}</span>
            <div class="message-footer">
              <small class="message-time">{{ formatDate(message.created_at) }}</small>
            </div>
          </div>
        </div>
      </div>

      <div class="chat-input">
        <input 
          v-model="newMessage" 
          @keyup.enter="sendMessage" 
          placeholder="Type your message..."
          class="input-field"
        />
        <button @click="sendMessage" class="btn primary-btn">Send</button>
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex';

export default {
  name: 'Friends',
  
  data() {
    return {
      profile: {
        friends: []
      },
      showChat: false,
      activeChat: null,
      chatId: null,
      chatSocket: null,
      currentUserId: null,
      messages: [],
      newMessage: '',
      notificationSocket: null,
      wsConnected: false,
    };
  },

  computed: {
    ...mapGetters(['getToken']),
  },

  async created() {
    await this.fetchProfile();
    this.currentUserId = this.profile.id;
    this.initNotificationSocket();
  },

  methods: {
    async fetchProfile() {
      try {
        const response = await fetch('http://localhost:8000/api/profile/', {
          headers: {
            'Authorization': `Token ${this.getToken}`,
            'Content-Type': 'application/json'
          },
        });
        
        if (!response.ok) throw new Error('Failed to fetch profile');
        this.profile = await response.json();
      } catch (error) {
        console.error('Profile fetch error:', error);
      }
    },

    async startChat(friend) {
      try {
        this.activeChat = friend.display_name;
        this.showChat = true;

        // Get chat ID by combining sorted user IDs
        const chatId = [this.currentUserId.toString(), friend.id.toString()]
          .sort()
          .join('_');

        if (!chatId.includes('_')) {
          throw new Error('Invalid chat ID format');
        }

        this.chatId = chatId;

        // Fetch existing messages
        const response = await fetch(`http://localhost:8001/api/chats/${chatId}/`, {
          method: 'GET',
          headers: {
            'Authorization': `Token ${this.getToken}`,
            'Content-Type': 'application/json'
          }
        });


        // Parse and set existing messages
        
        // Parse and set existing messages
        const data = await response.json();
        console.log('Messages data:', {
          currentUserId: this.currentUserId,
          friendId: friend.id,
          messages: data.messages
        });
        
        this.messages = data.messages.map(msg => ({
          id: msg.id,
          chat: msg.chat,
          sender: msg.sender,
          text: msg.text,
          created_at: msg.created_at
        }));
        // Initialize WebSocket connection
        if (this.chatSocket) {
          this.chatSocket.close();
        }

        const wsScheme = window.location.protocol === 'https:' ? 'wss' : 'ws';
        const wsUrl = `${wsScheme}://localhost:8001/ws/chat/${this.chatId}/?token=${this.getToken}`;
    
        console.log('Chat WebSocket URL:', wsUrl);
        
        this.chatSocket = new WebSocket(wsUrl);
        
        // Handle incoming messages with correct structure
        this.chatSocket.onmessage = (event) => {
          const data = JSON.parse(event.data);
          if (data.type === 'chat.message') {
            // Format incoming message to match loaded messages structure
            const newMessage = {
              id: data.message.id,
              chat: data.message.chat,
              sender: parseInt(data.message.sender),
              text: data.message.text,
              created_at: data.message.created_at || new Date().toISOString()
            };
            
            console.log('Received WebSocket message:', {
              message: newMessage,
              currentUserId: this.currentUserId
            });

            this.messages.push(newMessage);
            this.$nextTick(() => {
              this.scrollToBottom();
            });
          }
        };

        this.chatSocket.onerror = (error) => {
          console.error('WebSocket error:', error);
        };
      } catch (error) {
        console.error('Error starting chat:', error);
        this.showStatus('Failed to start chat', {}, 'error');
      }
    },

    closeChat() {
      if (this.chatSocket) {
        this.chatSocket.close();
        this.chatSocket = null;
        //Console log to check if chatSocket is closed
        console.log('Chat socket closed');
      }

      
      this.showChat = false;
      this.activeChat = null;
      this.chatId = null;
      this.messages = [];
      this.newMessage = '';
    },

    async sendMessage() {
      if (!this.newMessage.trim() || !this.chatSocket) return;
      
      if (this.chatSocket.readyState !== WebSocket.OPEN) {
        console.error('WebSocket is not connected');
        return;
      }

      try {
        const messageData = {
          type: 'chat_message',
          message: {
            chat: this.chatId,
            text: this.newMessage,
            sender: this.currentUserId
          }
        };

        console.log('Sending message data:', {
          messageContent: messageData,
          socketState: this.chatSocket.readyState,
          currentUserId: this.currentUserId,
          chatId: this.chatId,
          timestamp: new Date().toISOString()
        });

        this.chatSocket.send(JSON.stringify(messageData));
        this.scrollToBottom();
        this.newMessage = '';
      } catch (error) {
        console.error('Error sending message:', error);
      }
    },

    async removeFriend(friendId) {
      try {
        const friend = this.profile.friends.find(f => f.id === friendId);
        const response = await fetch('/api/profile/remove_friend/', {
          method: 'POST',
          headers: {
            'Authorization': `Token ${this.getToken}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ friend_profile_id: friendId }),
        });
          
        if (response.ok) {
          this.showStatus('Friend {name} removed successfully', { name: friend.display_name }, 'success');
          
          await this.fetchProfile(); // Refresh sender's profile
        } else {
          console.error('Failed to remove friend');
        }
      } catch (error) {
        console.error('Error removing friend:', error);
      }
    },

	initNotificationSocket() {
      //Get token from store
      const token = this.getToken;
      const wsScheme = window.location.protocol === 'https:' ? 'wss' : 'ws';
      const wsUrl = `${wsScheme}://${window.location.host}/ws/profile/notifications/?token=${this.$store.state.token}`;
      this.notificationSocket = new WebSocket(wsUrl);
      this.notificationSocket.onopen = () => {
        this.wsConnected = true;
      };
      this.notificationSocket.onmessage = (e) => {
        console.log('WebSocket message received:', e.data);  // Debug logging
        const data = JSON.parse(e.data);
        // Handle incoming messages
        switch (data.type) {
          case 'friend_request':
            this.incomingFriendRequests.push({
                id: Date.now(), // Generate temporary ID
                from_user: {
                    id: data.from_user_id,
                    display_name: data.from_user_name,
                    avatar: this.buildAvatarUrl(data.from_user_avatar, 'http://localhost:8000'),
                    is_online: true // Assume online since they just sent request
                }
            });
            this.showStatus(`New friend request from ${data.from_user_name}`, {}, 'success');
            break;

            case 'friend_status':
              const friendId = data.user_id;
              const status = data.status;
              // First try to find friend in the profile.friends array
              const friend = this.profile.friends.find(f => 
                  f.user_id === friendId || // Check user_id
                  f.id === friendId || // Check profile id
                  (f.user && f.user.id === friendId) // Check nested user object
              );
              
              if (friend) {
                  friend.is_online = (status === 'online');
                  console.log(`Updated status for friend ${friend.display_name} to ${status}`);
              } else {
                  console.log('Friend status update failed:', {
                      receivedId: friendId,
                      status: status,
                      friendsList: this.profile.friends
                  });
              }
              break;

          case 'friend_request_accepted':
            this.fetchProfile();
            break;

          case 'friend_request_declined':
            this.fetchProfile();
            break;

          case 'friend_removed':
            this.fetchProfile(); // Refresh receiver's profile
            break;

          default:
            console.warn('Unhandled WebSocket message type:', data.type);
            break;
        }
      };
      this.notificationSocket.onclose = () => {
        this.wsConnected = false;
      };
    },

    scrollToBottom() {
      this.$nextTick(() => {
        const chatMessages = this.$refs.chatMessages;
        if (chatMessages) {
          chatMessages.scrollTop = chatMessages.scrollHeight;
        }
      });
    },
  },

  beforeDestroy() {
    if (this.notificationSocket) {
      this.notificationSocket.close();
    }
    if (this.chatSocket) {
      this.chatSocket.close();
    }
  }
};
</script>

<style scoped>
.friends-container {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.profile-section {
  margin-bottom: 20px;
}

.profile-item {
  display: flex;
  align-items: center;
  margin-bottom: 1%;
  padding: 10px;
  border-radius: 8px;
  background: #1a1a1a;
}

.profile-avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  margin-right: 5%;
}

.profile-name {
  font-size: 16px;
  flex-grow: 1;
  color: #ffffff;
}

.status {
  padding: 0 15px;
}

.status.online {
  color: #03a670;
}

.status.offline {
  color: #a60303;
}

.friend-actions {
  display: flex;
  gap: 10px;
}

.btn {
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  border: none;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.primary-btn {
  background: #03a670;
  color: white;
}

.secondary-btn {
  background: #333333;
  color: #ffffff;
}

.secondary-btn:hover {
  background: #a60303;
}

.chat-container {
  height: 500px;
  display: flex;
  flex-direction: column;
  border-radius: 10px;
  box-shadow: 2px 2px 30px #03a670;
  margin-top: 20px;
}

.chat-header {
  padding: 1rem;
  background: #2d2d2d;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #ffffff;
  border-radius: 10px 10px 0 0;
}

.chat-messages {
  flex-grow: 1;
  overflow: auto;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  background: #1a1a1a;
}

.message {
  display: flex;
  max-width: 70%;
  margin-bottom: 1rem;
}

.message-sent {
  margin-left: auto;
}

.message-received {
  margin-right: auto;
}

.message-content {
  padding: 1rem;
  border-radius: 1rem;
  position: relative;
}

.content-sent {
  background: #03a670;
  color: #ffffff;
  border-radius: 1rem 1rem 0 1rem;
}

.content-received {
  background: #333333;
  color: #ffffff;
  border-radius: 1rem 1rem 1rem 0;
}

.message-time {
  font-size: 0.7rem;
  color: rgba(255, 255, 255, 0.7);
  margin-top: 0.5rem;
}

.chat-input {
  padding: 1rem;
  background: #2d2d2d;
  border-top: 1px solid #404040;
  display: flex;
  gap: 0.5rem;
}

.input-field {
  flex-grow: 1;
  border: 1px solid #404040;
  padding: 0.75rem 1rem;
  border-radius: 4px;
  background: #1a1a1a;
  color: #ffffff;
}

.input-field::placeholder {
  color: #808080;
}
</style>