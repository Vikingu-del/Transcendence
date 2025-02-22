<template>
  <div class="friends-container">
    <div class="friends-nav">
      <button 
        @click="activeTab = 'friends'"
        :class="['tab-btn', { active: activeTab === 'friends' }]"
      >
        Friends ({{ profile.friends?.length || 0 }})
      </button>
      <button 
        @click="activeTab = 'requests'"
        :class="['tab-btn', { active: activeTab === 'requests' }]"
      >
        Friend Requests ({{ incomingFriendRequests.length }})
      </button>
      <button 
        @click="activeTab = 'search'"
        :class="['tab-btn', { active: activeTab === 'search' }]"
      >
        Find Friends
      </button>
    </div>

    <!-- Friends List Section -->
    <div v-if="activeTab === 'friends'" class="section">
      <div v-if="profile.friends && profile.friends.length > 0">
        <div v-for="friend in profile.friends" :key="friend.id" class="profile-item">
          <div class="avatar-container" @click="showFriendInfo(friend)">
            <img :src="friend.avatar" :alt="friend.display_name" class="profile-avatar">
            <span :class="['status-dot', friend.is_online ? 'online' : 'offline']"></span>
          </div>
          <span class="profile-name">{{ friend.display_name }}</span>
          <div class="friend-actions">
            <button @click="showFriendInfo(friend)" class="btn primary-btn">Info</button>
            <button @click="removeFriend(friend.id)" class="btn secondary-btn">Remove</button>
          </div>
        </div>
      </div>
      <p v-else class="no-content">No friends yet</p>
    </div>

    <!-- Friend Requests Section -->
    <div v-if="activeTab === 'requests'" class="section">
      <div v-if="incomingFriendRequests.length > 0">
        <div v-for="request in incomingFriendRequests" :key="request.id" class="profile-item">
          <div class="user-info">
            <img 
              :src="request.from_user.avatar" 
              :alt="request.from_user.display_name"
              class="profile-avatar"
            >
            <span class="display-name">{{ request.from_user.display_name }}</span>
          </div>
          <div class="action-buttons">
            <button 
              @click="acceptFriendRequest(request)" 
              class="btn primary-btn"
            >
              Accept
            </button>
            <button 
              @click="declineFriendRequest(request)" 
              class="btn secondary-btn"
            >
              Decline
            </button>
          </div>
        </div>
      </div>
      <p v-else class="no-content">No pending friend requests</p>
    </div>

    <!-- Search Section -->
    <div v-if="activeTab === 'search'" class="section">
      <div class="search-box">
        <input 
          v-model="searchQuery" 
          @input="searchProfiles" 
          placeholder="Search for users..." 
          class="search-input"
        />
      </div>

      <div v-if="isSearching" class="loading">
        <span>Searching...</span>
      </div>
      
      <div v-else-if="searchError" class="error-message">
        {{ searchError }}
      </div>
      
      <!-- Update the search results section HTML -->
      <div v-else-if="searchResults.length > 0" class="search-results">
        <div v-for="profile in searchResults" :key="profile.id" class="profile-item">
          <!-- Left side: User info -->
          <div class="user-info">
            <img :src="profile.avatar" :alt="profile.display_name" class="profile-avatar">
            <span class="display-name">{{ profile.display_name }}</span>
          </div>
          
          <!-- Right side: Action buttons -->
          <div class="action-buttons">
            <!-- Add/Remove Friend button -->
            <button 
              v-if="canAddFriend(profile)" 
              @click="sendFriendRequest(profile.id)" 
              class="btn primary-btn"
            >
              Add Friend
            </button>
            <button 
              v-else-if="isFriend(profile)" 
              @click="removeFriend(profile.id)" 
              class="btn secondary-btn"
            >
              Remove Friend
            </button>
            <span 
              v-else-if="profile.friend_request_status === 'pending'" 
              class="status-text"
            >
              Request Pending
            </span>

            <!-- Block/Unblock button -->
            <button
              v-if="canShowBlockButton(profile)"
              @click="blockUser(profile.id)" 
              class="btn secondary-btn"
            >
              Block
            </button>
            <button 
              v-else-if="isBlocked(profile)"
              @click="unblockUser(profile.id)" 
              class="btn primary-btn"
            >
              Unblock
            </button>
          </div>
        </div>
      </div>
      <p v-else-if="searchQuery" class="no-content">No users found</p>
    </div>
    <div v-if="statusMessage":class="['status-message', statusMessage.type]">
      {{ statusMessage.text }}
    </div>



    <!-- Add this right before the closing </div> of friends-container -->
    <transition name="fade">
      <div v-if="showFriendProfile && selectedFriend" class="overlay">
        <div class="friend-profile-modal">
          <div class="friend-profile-header">
            <h3 class="profile-title">Profile Information</h3>
            <button @click="showFriendProfile = false" class="btn secondary-btn">Close</button>
          </div>

          <div class="profile-details">
            <!-- Avatar section -->
            <div class="detail-group avatar-group">
              <div class="profile-avatar-large">
                <img 
                  :src="selectedFriend.avatar" 
                  :alt="selectedFriend.display_name"
                  class="friend-avatar"
                >
                <span :class="['status-indicator', selectedFriend.is_online ? 'online' : 'offline']"></span>
              </div>
            </div>

            <div class="detail-group">
              <h5>Display Name</h5>
              <p>{{ selectedFriend.display_name }}</p>
            </div>
          </div>

          <div class="friend-profile-footer">
            <button @click="startChat(selectedFriend)" class="btn primary-btn">Chat</button>
          </div>
        </div>
      </div>
    </transition>

    <!-- Chat Section -->
    <transition name="fade">
      <div v-if="showChat" class="overlay">
        <div class="chat-container">
          <div class="chat-header">
            <button @click="sendGameInvite" class="btn primary-btn">
              <i class="game-icon"></i> Invite to Play
            </button>
            
            <h4 class="chat-title">Chat with {{ activeChat }}</h4>

            <button @click="closeChat" class="btn secondary-btn">Close</button>
          </div>
          <div class="chat-messages" ref="chatMessages">
            <div v-for="message in messages" 
              :key="message.id" 
              :class="['message', { 
                'message-sent': parseInt(message.sender_id) === parseInt(currentUserId),
                'message-received': parseInt(message.sender_id) !== parseInt(currentUserId)
              }]">
              <div class="message-content" :class="{ 
                  'content-sent': parseInt(message.sender_id) === currentUserId,
                  'content-received': parseInt(message.sender_id) !== currentUserId
                }">
                <div class="message-header">
                  <small 
                    class="message-sender" 
                    @click="showChatParticipantProfile(message)"
                    :class="{ 'clickable': parseInt(message.sender_id) !== currentUserId }"
                  >
                    {{ parseInt(message.sender_id) === currentUserId ? '' : activeChat }}
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
    </transition>
  
  </div>

  <!-- Debugging -->
  <div>
    <pre>{{ profile }}</pre>
    <pre>{{ incomingFriendRequests }}</pre>
    <pre>{{ searchResults }}</pre>
  </div>

</template>

<script>
import { SERVICE_URLS } from '@/config/services';

export default {
  name: 'Friends',
  
  data() {
    return {
      profile: {
        friends: []
      },
  
      notificationSocket: null,
      wsConnected: false,
      searchQuery: '',
      searchResults: [],
      isSearching: false,
      searchError: null,
      searchTimeout: null,
      incomingFriendRequests: JSON.parse(localStorage.getItem('incomingRequests') || '[]'),

      //Friends Profile View
      selectedFriend: null,
      showFriendProfile: false,

      // Tab state
      activeTab: 'friends',

      // Auth token
      token: localStorage.getItem('token'),

      //Status message
      statusMessage: null,

      //Current User ID
      currentUserId: null,
      chatSocket: null,
      messages: [],
      newMessage: '',
      showChat: false,
      activeChat: null,
      chatId: null,
    };
  },

  computed: {
    getToken() {
      return this.token;
    },
    isAuthenticated() {
      return !!this.token;
    },
  },

  async created() {
    try {
      const token = localStorage.getItem('token');
      console.log('Initial token:', token);
      
      if (!token) {
        await this.$router.push('/login');
        return;
      }
      
      // Fetch both profile and friend requests
      await Promise.all([
        this.fetchProfile(),
        this.fetchIncomingRequests()
      ]);
      
      // this.initNotificationSocket();
    } catch (error) {
      console.error('Initialization error:', error);
      this.$router.push('/login');
    }
  },

  methods: {

    // Authentication & Profile Methods
    async fetchProfile() {
      try {
        const token = this.getToken;
        if (!token) throw new Error('No auth token found');

        const response = await fetch('/api/user/profile/', {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
        });

        if (!response.ok) {
          const errorText = await response.text();
          throw new Error(errorText);
        }

        const data = await response.json();
        this.profile = data;
        // Set the currentUserId from the profile data
        this.currentUserId = data.id; // Uncomment and update this line
        this.loading = false;
      } catch (error) {
        console.error('Profile fetch error:', error);
        if (error.message.includes('token_not_valid')) {
          this.$router.push('/login');
        }
        throw error;
      }
    },

    // Friend Request Methods
    async fetchIncomingRequests() {
      try {
        const token = this.getToken;
        if (!token) throw new Error('No auth token found');

        const response = await fetch('/api/user/profile/friend-requests/', {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });

        if (!response.ok) throw new Error('Failed to fetch friend requests');

        const data = await response.json();
        this.incomingFriendRequests = data;
        localStorage.setItem('incomingRequests', JSON.stringify(data));
      } catch (error) {
        console.error('Error fetching friend requests:', error);
        this.showStatus('Failed to load friend requests', {}, 'error');
      }
    },

    async sendFriendRequest(friendId) {
      try {
        const token = this.getToken;
        if (!token) throw new Error('No auth token found');

        const friend = this.searchResults.find(p => p.id === friendId);
        if (!friend) throw new Error('Friend not found in search results');

        const response = await fetch('/api/user/profile/add_friend/', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          },
          body: JSON.stringify({ friend_profile_id: friendId })
        });

        const data = await response.json();
        if (!response.ok) throw new Error(data.error || 'Failed to send friend request');

        this.updateSearchResultStatus(friendId, 'pending');
        this.showStatus('Friend request sent to {name}', { name: friend.display_name }, 'success');
        await this.fetchProfile();
      } catch (error) {
        console.error('Error sending friend request:', error);
        this.showStatus(error.message || 'Failed to send friend request', {}, 'error');
      }
    },

    async acceptFriendRequest(request) {
      try {
        const response = await fetch('/api/user/profile/friend-requests/accept/', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${this.getToken}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ from_user_id: request.from_user.id })
        });

        if (!response.ok) throw new Error('Failed to accept friend request');

        this.updateLocalRequests(request.id);
        this.showStatus(
          'Friend request from {name} accepted', 
          { name: request.from_user.display_name }, 
          'success'
        );
        await this.fetchProfile();
      } catch (error) {
        console.error('Error accepting friend request:', error);
        this.showStatus('Failed to accept friend request', {}, 'error');
      }
    },

    async declineFriendRequest(request) {
      try {
        const response = await fetch('/api/user/profile/friend-requests/decline/', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${this.getToken}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ from_user_id: request.from_user.id })
        });

        if (!response.ok) throw new Error('Failed to decline friend request');

        this.updateLocalRequests(request.id);
        this.showStatus(
          'Friend request from {name} declined', 
          { name: request.from_user.display_name }, 
          'success'
        );
      } catch (error) {
        console.error('Error declining friend request:', error);
        this.showStatus('Failed to decline friend request', {}, 'error');
      }
    },

    // Friend Management Methods
    async removeFriend(friendId) {
      try {
        const friend = this.profile.friends.find(f => f.id === friendId);
        if (!friend) {
          this.showStatus('Friend not found', {}, 'error');
          return;
        }

        const response = await fetch('/api/user/profile/remove_friend/', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${this.getToken}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ friend_profile_id: friendId })
        });

        const data = await response.json();
        if (response.ok) {
          this.showStatus('Friend {name} removed successfully', { name: friend.display_name }, 'success');
          await this.fetchProfile();
        } else {
          this.showStatus(data.message || 'Failed to remove friend', {}, 'error');
        }
      } catch (error) {
        console.error('Error removing friend:', error);
        this.showStatus('Error removing friend', {}, 'error');
      }
    },

    // Search Methods
    async searchProfiles() {
      if (!this.getToken) {
        this.showStatus('Please log in to search', {}, 'warning');
        return;
      }

      try {
        if (!this.searchQuery.trim()) {
          this.searchResults = [];
          this.showStatus('Please enter a search term', {}, 'warning');
          return;
        }

        this.isSearching = true;
        this.searchError = null;

        const response = await fetch(
          `/api/user/profile/search/?q=${encodeURIComponent(this.searchQuery.trim())}`,
          {
            headers: {
              'Authorization': `Bearer ${this.getToken}`,
              'Content-Type': 'application/json',
              'Accept': 'application/json'
            }
          }
        );

        if (!response.ok) throw new Error('Search failed');

        const data = await response.json();
        this.searchResults = data;
        this.handleSearchResults(data);
      } catch (error) {
        console.error('Search error:', error);
        this.searchError = error.message;
        this.searchResults = [];
      } finally {
        this.isSearching = false;
      }
    },

    // Block/Unblock Methods
    async blockUser(profileId) {
      try {
        const profile = this.searchResults.find(p => p.id === profileId);
        const response = await fetch(`/api/user/profile/${profileId}/block/`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${this.getToken}`,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          }
        });

        if (!response.ok) throw new Error('Failed to block user');
        
        this.updateSearchResultStatus(profileId, null, true);
        this.showStatus('User {name} has been blocked', { name: profile.display_name }, 'warning');
      } catch (error) {
        this.showStatus(error.message, 'error');
      }
    },

    async unblockUser(profileId) {
      try {
        const profile = this.searchResults.find(p => p.id === profileId);
        const response = await fetch(`/api/user/profile/${profileId}/block/`, {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${this.getToken}`,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          }
        });

        if (!response.ok) throw new Error('Failed to unblock user');

        this.updateSearchResultStatus(profileId, null, false);
        this.showStatus('User {name} has been unblocked', { name: profile.display_name }, 'success');
      } catch (error) {
        this.showStatus(error.message, 'error');
      }
    },

    // Helper Methods
    updateLocalRequests(requestId) {
      this.incomingFriendRequests = this.incomingFriendRequests
        .filter(req => req.id !== requestId);
      localStorage.setItem('incomingRequests', 
        JSON.stringify(this.incomingFriendRequests));
    },

    updateSearchResultStatus(profileId, friendRequestStatus = null, isBlocked = null) {
      this.searchResults = this.searchResults.map(profile => {
        if (profile.id === profileId) {
          return {
            ...profile,
            ...(friendRequestStatus && { friend_request_status: friendRequestStatus }),
            ...(isBlocked !== null && { isBlocked }),
            ...(friendRequestStatus === 'pending' && { requested_by_current_user: true })
          };
        }
        return profile;
      });
    },

    handleSearchResults(data) {
      if (data.length === 0) {
        this.showStatus('No users found for "{query}"', { query: this.searchQuery }, 'warning');
      } else {
        this.showStatus('Found {count} users', { count: data.length }, 'success');
      }
    },

    showStatus(message, variables = {}, type = 'success') {
      // Validate message type
      const validTypes = ['success', 'warning', 'error'];
      if (!validTypes.includes(type)) {
        type = 'success'; // Default fallback
      }

      // Interpolate variables into message
      let text = message;
      Object.entries(variables).forEach(([key, value]) => {
        text = text.replace(`{${key}}`, value);
      });
      this.statusMessage = { text, type };

      // Clear after timeout
      setTimeout(() => {
        this.statusMessage = null;
      }, 3000);
    },

    // Add a method to check if a user can be added as a friend
    canAddFriend(profile) {
      return !this.isFriend(profile) && 
            !profile.friend_request_status && 
            !this.isBlocked(profile) &&
            !profile.isBlocked;
    },

    // Add a method to check if the block button should be shown
    canShowBlockButton(profile) {
      return !this.isFriend(profile) && 
            !profile.friend_request_status && 
            !this.isBlocked(profile);
    },

    // State Checks
    isFriend(profile) {
      return this.profile?.friends?.some(friend => friend.id === profile.id);
    },

    isBlocked(profile) {
      return profile.isBlocked;
    },

    getFriendRequestStatus(profile) {
      return profile.friend_request_status;
    },

    reconnectWebSocket(chatId) {
      if (!this.showChat) return; // Don't reconnect if chat is closed
      
      console.log('Attempting to reconnect WebSocket...');
      
      // Wait 3 seconds before attempting to reconnect
      setTimeout(() => {
        this.initWebSocket(chatId);
      }, 3000);
    },

    // Split into these methods:

    async startChat(friend) {
      try {
        await this.validateChatPrerequisites(friend);
        this.updateChatUI(friend);
        const chatId = this.generateChatId(friend.id);
        await this.fetchChatHistory(chatId);
        await this.initializeChatWebSocket(chatId);
        this.scrollToBottom();
      } catch (error) {
        this.handleChatError(error);
      }
    },

    validateChatPrerequisites(friend) {
      if (!this.currentUserId) {
        throw new Error('Current user ID is not set');
      }

      if (!this.getToken) {
        throw new Error('No authentication token available');
      }

      console.log('Starting chat with:', {
        friendId: friend.id,
        currentUserId: this.currentUserId,
        token: this.getToken ? 'Token present' : 'No token'
      });
    },

    updateChatUI(friend) {
      this.activeChat = friend.display_name;
      this.showFriendProfile = false;
      this.showChat = true;
    },

    generateChatId(friendId) {
      const chatId = [this.currentUserId, friendId]
        .sort((a, b) => a - b)
        .join('_');
      console.log('Generated chat ID:', chatId);
      return chatId;
    },

    async fetchChatHistory(chatId) {
      const response = await fetch(`/api/chats/${chatId}/`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${this.getToken}`,
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        credentials: 'include'
      });

      console.log('Chat fetch response:', {
        status: response.status,
        statusText: response.statusText,
        headers: Object.fromEntries(response.headers.entries())
      });

      await this.processChatResponse(response);
      this.chatId = chatId;
    },

    async processChatResponse(response) {
      if (!response.ok) {
        const errorText = await response.text();
        console.error('Chat error response:', errorText);
        
        if (response.status === 404) {
          this.messages = [];
        } else {
          throw new Error(errorText || `Chat service error: ${response.status}`);
        }
      } else {
        const data = await response.json();
        console.log('Received chat data:', data);

        if (!data || !Array.isArray(data.messages)) {
          throw new Error('Invalid chat data received');
        }

        this.messages = data.messages.map(msg => ({
          id: msg.id,
          chat: msg.chat,
          sender_id: String(msg.sender_id || msg.sender),
          text: msg.text,
          created_at: msg.created_at || new Date().toISOString()
        }));
      }
    },

    async initializeChatWebSocket(chatId) {
      if (this.chatSocket && this.chatSocket.readyState === WebSocket.OPEN) {
        this.chatSocket.close();
      }

      const wsUrl = this.buildWebSocketUrl(chatId);
      console.log('Connecting WebSocket to:', wsUrl);
      
      this.chatSocket = new WebSocket(wsUrl);
      this.setupWebSocketEventHandlers(chatId);
    },

    buildWebSocketUrl(chatId) {
      const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsHost = window.location.host;
      return `${wsProtocol}//${wsHost}/ws/chat/${chatId}/?token=${this.getToken}`;
    },

    setupWebSocketEventHandlers(chatId) {
      this.chatSocket.onopen = () => {
        console.log('WebSocket connection established');
        this.wsConnected = true;
      };

      this.chatSocket.onerror = (error) => {
        console.error('WebSocket error:', error);
        this.wsConnected = false;
        this.showStatus('Chat connection error. Attempting to reconnect...', {}, 'warning');
        setTimeout(() => this.reconnectWebSocket(chatId), 3000);
      };

      this.chatSocket.onclose = (event) => {
        console.log('WebSocket connection closed:', event);
        this.wsConnected = false;
        if (this.showChat) {
          setTimeout(() => this.reconnectWebSocket(chatId), 3000);
        }
      };

      this.chatSocket.onmessage = this.handleWebSocketMessage;
    },

    handleWebSocketMessage(event) {
      try {
        const data = JSON.parse(event.data);
        console.log('Received WebSocket message:', data);
        
        if (data.type === 'chat.message') {
          const newMessage = {
            id: data.message.id,
            chat: data.message.chat,
            sender_id: String(data.message.sender_id || data.message.sender),
            text: data.message.text,
            created_at: data.message.created_at || new Date().toISOString()
          };

          this.messages.push(newMessage);
          this.$nextTick(() => {
            this.scrollToBottom();
          });
        }
      } catch (error) {
        console.error('Error processing message:', error);
      }
    },

    handleChatError(error) {
      console.error('Error starting chat:', error);
      this.showStatus(
        `Chat error: ${error.message || 'Unable to connect to chat service'}`, 
        {}, 
        'error'
      );
      this.showChat = false;
      this.activeChat = null;
    },
        
    showFriendInfo(friend) {
      this.selectedFriend = friend;
      this.showFriendProfile = true;
      this.showChat = false;
    },

    showChatParticipantProfile(message) {
      // Only show profile for messages from other users
      if (parseInt(message.sender_id) === parseInt(this.currentUserId)) {
        return;
      }

      // Find the friend from your friends list
      const friend = this.profile.friends.find(f => f.id === parseInt(message.sender_id));
      
      if (friend) {
        this.selectedFriend = friend;
        this.showFriendProfile = true;
        // Close the chat when showing profile
        this.showChat = false;
        
        // Optional: Close WebSocket connection
        if (this.chatSocket) {
          this.chatSocket.close();
          this.chatSocket = null;
        }
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
            sender_id: this.currentUserId  // Change 'sender' to 'sender_id'
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

    formatDate(timestamp) {
      if (!timestamp) return '';
      const date = new Date(timestamp);
      const options = { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric',
        hour: '2-digit', 
        minute: '2-digit'
      };
      return new Date(timestamp).toLocaleDateString(undefined, options);
    },
    
    scrollToBottom() {
      this.$nextTick(() => {
        const chatMessages = this.$refs.chatMessages;
        if (chatMessages) {
          chatMessages.scrollTop = chatMessages.scrollHeight;
        }
      });
    },

    showStatus(message, variables = {}, type = 'success') {
      // Validate message type
      const validTypes = ['success', 'warning', 'error'];
      if (!validTypes.includes(type)) {
        type = 'success'; // Default fallback
      }

      // Interpolate variables into message
      let text = message;
      Object.entries(variables).forEach(([key, value]) => {
        text = text.replace(`{${key}}`, value);
      });

      // Set status message
      this.statusMessage = { text, type };

      // Clear after timeout
      setTimeout(() => {
        this.statusMessage = null;
      }, 3000);
    },

    buildAvatarUrl(avatarPath, baseUrl) {
        // If no avatar path provided, return default avatar
        if (!avatarPath) return this.defaultAvatarUrl;
        
        // If it's already a full URL, return it
        if (avatarPath.startsWith('http')) return avatarPath;
        
        // If it's a path starting with /media
        if (avatarPath.startsWith('/media')) {
            return `${baseUrl}${avatarPath}`;
        }
        
        // For relative paths in the avatars directory
        return `${baseUrl}/media/${avatarPath}`;
    },
  },

  messages: {
    handler() {
      this.scrollToBottom();
    },
    deep: true
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
friends-nav {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.tab-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  background: #333333;
  color: white;
  cursor: pointer;
  transition: background-color 0.2s;
}

.tab-btn.active {
  background: #03a670;
}

.section {
  background: #1a1a1a;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
}

.no-content {
  text-align: center;
  color: #666;
  padding: 20px;
}

.search-box {
  margin-bottom: 20px;
}

.search-input {
  width: 100%;
  padding: 10px;
  border: 1px solid #404040;
  border-radius: 4px;
  background: #2d2d2d;
  color: white;
}

.friends-container {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.friends-nav {
  width: 100%;
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-bottom: 20px;
}

.section {
  width: 100%;
  background: #1a1a1a;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  box-sizing: border-box;
}

.search-box {
  width: 100%;
  max-width: 600px;
  margin: 0 auto 20px auto;
}

.search-results {
  width: 100%;
}

.profile-section {
  margin-bottom: 20px;
}

.profile-item {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  margin-bottom: 10px;
  background: #1a1a1a;
  border-radius: 8px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.profile-avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  object-fit: cover;
}

.display-name {
  color: #ffffff;
  font-size: 16px;
}

.action-buttons {
  display: flex;
  align-items: center;
  gap: 10px;
}

.btn {
  padding: 8px 16px;
  border-radius: 4px;
  border: none;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.primary-btn {
  background: #03a670;
  color: white;
}

.secondary-btn {
  background: #a60303;
  color: white;
}

.status-text {
  color: #666;
  font-style: italic;
  padding: 8px 16px;
}

.avatar-container {
  position: relative;
  margin-right: 5%;
}

.status-dot {
  position: absolute;
  bottom: 2px;
  right: 2px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 2px solid #1a1a1a;
}primary

.status-dot.online {
  background-color: #03a670;
}

.status-dot.offline {
  background-color: #a60303;
}

/* Update existing profile-avatar style */
.profile-avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  object-fit: cover;
}

.profile-name {
  font-size: 16px;
  flex-grow: 1;
  color: #ffffff;
  margin-right: 20px;
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

.secondary-btn:hover {
  background: #333333;
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
  padding-left: 5%;
  gap: 0.5rem;
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

.overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.75);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.message-sender.clickable {
  cursor: pointer;
  transition: all 0.3s ease;
  color: #ffffff
}

.message-sender.clickable:hover {
  color:#03a670;
  opacity: 0.8;
  transform: scale(1.1);
}

.chat-header .primary-btn {
  transition: all 0.3s ease;
}

.chat-header .primary-btn:hover {
  background: #04d38e;
  transform: scale(1.05);
  box-shadow: 0 0 10px rgba(3, 166, 112, 0.5);
}

.friend-profile-modal {
  width: 90%;
  max-width: 500px;
  background: #1a1a1a;
  border-radius: 10px;
  box-shadow: 0 4px 20px rgba(3, 166, 112, 0.4);
  z-index: 1001;
  display: flex;
  flex-direction: column;
  max-height: 80vh;
}

.friend-profile-header {
  padding: 1rem;
  background: #2d2d2d;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-radius: 10px 10px 0 0;
  padding-left: 30%;
}

.profile-details {
  flex: 1;
  padding: 1.5rem;
  overflow-y: auto;
}

.detail-group {
  margin-bottom: 1.5rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid #404040;
}

.detail-group:last-child {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
}

.detail-group h5 {
  color: #03a670;
  margin: 0 0 0.5rem 0;
  font-size: 1rem;
}

.detail-group p {
  margin: 0;
  color: #ffffff;
  line-height: 1.4;
}

.friend-profile-footer {
  padding: 1rem;
  background: #2d2d2d;
  border-top: 1px solid #404040;
  border-radius: 0 0 10px 10px;
  display: flex;
  justify-content: center;
}

/* Add transition styles */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.avatar-group {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 1rem 0;
}

.profile-avatar-large {
  position: relative;
  width: 120px;
  height: 120px;
}

.friend-avatar {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid #03a670;
}

.status-indicator {
  position: absolute;
  bottom: 5px;
  right: 5px;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  border: 3px solid #1a1a1a;
}

.status-indicator.online {
  background-color: #03a670;
}

.status-indicator.offline {
  background-color: #a60303;
}


.status-message {
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 12px 24px;
  border-radius: 4px;
  z-index: 1000;
  animation: fadeIn 0.3s ease;
}

.status-message.success {
  background-color: #4caf50;
  color: white;
}

.status-message.warning {
  background-color: #ff9800;
  color: white;
}

.status-message.error {
  background-color: #f44336;
  color: white;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}


</style>