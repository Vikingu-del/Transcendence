<template>
  <div v-if="statusMessage" class="status-message" :class="statusMessage.type">
    {{ statusMessage.text }}
  </div>
  <div class="profile-container">
    <!-- Profile Card -->
    <div class="profile-card" v-if="profile">
      <!-- Avatar Section with Upload/Delete -->
      <div class="avatar-container">
        <img 
          :src="profile?.avatar ? buildAvatarUrl(profile.avatar) : defaultAvatarUrl" 
          :alt="profile?.display_name || 'Profile'"
          class="profile-picture"
          @error="handleImageError"
        />
        <div class="avatar-actions">
          <input type="file" @change="onFileChange" class="file-input" id="avatar-upload" />
          <label for="avatar-upload" class="btn primary-btn">Change Avatar</label>
          <button v-if="!isDefaultAvatar" @click="deleteAvatar" class="btn secondary-btn">Delete Avatar</button>
        </div>
      </div>

      <!-- Profile Info Section with Edit -->
      <div class="profile-section">
        <form @submit.prevent="updatedisplayName" class="profile-form">
          <input
            v-model="displayName"
            :placeholder="profile.display_name"
            class="input-field"
            required
          />
          <span v-if="displayNameError" class="error-message">{{ displayNameError }}</span>
          <button 
            type="submit" 
            class="btn primary-btn" 
            :disabled="isUpdateDisabled"
            :class="{ 'enabled-btn': !isUpdateDisabled }"
          >
            Update Profile
          </button>
        </form>
      </div>

      <!-- Search Section -->
      <div class="search-section">
        <input 
          v-model="searchQuery" 
          @input="searchProfiles" 
          placeholder="Search profiles..." 
          class="input-field"
        />
        <div v-if="isSearching">Searching...</div>
        <div v-if="searchError" class="error-message">{{ searchError }}</div>
        <div v-if="searchQuery && !searchResults?.length && !isSearching" class="no-results">
          <p>No users found</p>
        </div>
        <div v-else-if="searchResults?.length" class="search-results">
          <div v-for="profile in searchResults" :key="profile.id" class="profile-item">
            <!-- Use get_avatar_url from Profile model -->
            <img :src="profile.avatar || profile.get_avatar_url":alt="profile.display_name" class="profile-avatar">
            <div class="profile-info">
              <p class="display-name">{{ profile.display_name }}</p>
            </div>
            
            <div class="friend-actions">
              <!-- Show when user is blocked -->
              <div v-if="isBlocked(profile)">
                <button @click="unblockUser(profile.id)" class="btn unblock-btn">
                  Unblock User
                </button>
              </div>
              <!-- Show for non-blocked users -->
              <div v-else>
                <!-- Show friend status buttons -->
                <div v-if="isFriend(profile)" class="friend-management">
                  <button @click="removeFriend(profile.id)" class="btn secondary-btn">
                    Remove Friend
                  </button>
                </div>
                <!-- Show pending request status -->
                <div v-else-if="profile.friend_request_status === 'pending'">
                  <p v-if="profile.requested_by_current_user" class="status-text">
                    Request Pending
                  </p>
                  <div v-else>
                    <button @click="acceptFriendRequest(profile.id)" class="btn accept-btn">
                      Accept
                    </button>
                    <button @click="declineFriendRequest(profile.id)" class="btn decline-btn">
                      Decline
                    </button>
                  </div>
                </div>
                <!-- Show add friend option -->
                <div v-else class="friend-management">
                  <button @click="sendFriendRequest(profile.id)" class="btn add-btn">
                    Add Friend
                  </button>
                  <button @click="blockUser(profile.id)" class="btn block-btn">
                    Block
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Incoming Friend Requests -->
      <div class="profile-section">
        <div v-if="incomingFriendRequests.length">Incoming Friend Requests</div>
        <div v-for="request in incomingFriendRequests" 
            :key="request.id" 
            class="profile-item">
          <img :src="request.from_user.avatar" :alt="request.from_user.display_name" class="profile-avatar">
          <span class="profile-name">{{ request.from_user.display_name }}</span>
          <div class="action-buttons">
            <button @click="acceptFriendRequest(request)" 
                    class="btn accept-btn">
              Accept
            </button>
            <button @click="declineFriendRequest(request)" 
                    class="btn decline-btn">
              Decline
            </button>
          </div>
        </div>
      </div>

      <!-- Friends Section with Chat -->
      <div class="profile-section">
        <h3>Friends</h3>
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
                  {{ parseInt(message.sender) === parseInt(currentUserId) ? '' : activeChat }} <!-- Hide sender name for own messages -->
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

    <!-- Loading and Error States -->
    <div v-if="loading">Loading...</div>
    <div v-if="error" class="error">{{ error }}</div>

    <!-- Logout Button -->
    <nav>
      <button @click="logout" class="btn secondary-btn">Logout</button>
    </nav>
  </div>
</template>

<script>
import { mapGetters } from 'vuex';
import { WebSocketService } from '../services/WebSocketService';
import { getApiEndpoints } from '../services/ApiService';

export default {
  name: 'Profile',
  
  data() {
    return {
      // Profile Data
      loading: true,
      error: null,
      profile: null,
      isInitialized: false,
      
      //Display Name Update
      displayName: '',
      displayNameError: null,
      isUpdateDisabled: true,
      
      // Avatar Upload
      defaultAvatarUrl: window.location.hostname === 'localhost' 
      ? 'http://localhost:8000/api/user/media/default_avatar.png' 
      : '/api/user/media/default_avatar.png',

      // Profile Search
      searchQuery: '',
      searchResults: [],
      isSearching: false,
      searchError: null,
      searchTimeout: null,
      currentUserId: null,

      //Web Socket
      wsConnected: false,
      notificationSocket: null,

      // Friend Requests
      incomingFriendRequests: JSON.parse(localStorage.getItem('incomingRequests') || '[]'),

      // Chat
      showChat: false,
      activeChat: null,
      chatId: null,
      chatSocket: null,
      currentFriendId: null,
      messages: [],
      newMessage: '',

      // Status Message
      statusMessage: null,
      wsService: null,
      apiEndpoints: null
    };
  },

  computed: {
    ...mapGetters(['getToken', 'isAuthenticated']),

    isDefaultAvatar() {
      return !this.profile || this.profile.avatar === this.defaultAvatarUrl;
    }
  },

  watch: {
    displayName() {
      this.checkDisplayName();
    },
    messages: {
      handler() {
        this.scrollToBottom(); // Add scroll when messages update
      },
      deep: true
    }
  },

  async created() {
    try {
      if (this.isInitialized) return;
      
      // Initialize WebSocket service
      this.wsService = new WebSocketService();
      this.wsService.addListener('chat', 'message', this.handleChatMessage);
      this.wsService.addListener('user', 'message', this.handleUserEvent);
      this.apiEndpoints = getApiEndpoints(this.getBaseUrl);
      
      // Initialize authentication
      const authInitialized = await this.$store.dispatch('initializeAuth');
      
      if (!authInitialized || !this.getToken) {
        this.$router.push('/login');
        return;
      }
      
      // Connect WebSocket after auth is confirmed
      this.wsService.connect(this.getToken);
      
      this.isInitialized = true;
      const profile = await this.fetchProfile();

      // Only set currentUserId if profile fetch was successful
      if (profile && profile.id) {
        this.currentUserId = profile.id;
        await this.fetchIncomingRequests();
      }
    } catch (error) {
      console.error('Error in created hook:', error);
      this.wsService?.disconnect(); // Cleanup WebSocket if initialization fails
      this.$router.push('/login');
    }
  },

  mounted() {
    this.initNotificationSocket();
  },

  methods: {
    handleImageError(e) {
      console.error('Image faile to load:', e.target.src);
       // Prevent infinite loop by checking if already using default
      if (e.target.src.includes('default.png')) {
        console.warn('Default image also failed to load');
        return;
      }
      e.target.src = this.defaultAvatarUrl;
    },

    getBaseUrl() {
      // Get protocol and hostname
      const protocol = window.location.protocol;
      const hostname = window.location.hostname;
      return hostname === 'localhost' 
        ? 'http://localhost:8000' 
        : `${protocol}//${hostname}`;
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

    async fetchProfile() {
      try {
        this.loading = true;
        this.error = null;
        
        const response = await fetch(this.apiEndpoints.profile, {
          method: 'GET',
          headers: {
            'Authorization': `Token ${this.$store.state.token}`,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          },
          credentials: 'include'
        });
        
        // Log response status for debugging
        console.log('Profile fetch response status:', response.status);

        // Handle unauthorized first
        if (response.status === 401) {
          console.log('Unauthorized access, logging out...');
          await this.$store.dispatch('logoutAction');
          this.$router.push('/login');
          return null;
        }

        // Handle other non-200 responses
        if (!response.ok) {
          const errorText = await response.text();
          console.error('Error response:', errorText);
          throw new Error(`Failed to fetch profile: ${response.status}`);
        }

        // Get response as text first for debugging
        const responseText = await response.text();
        console.log('Raw response:', responseText);

        // Parse JSON response
        const profile = JSON.parse(responseText);
        console.log('Parsed profile:', profile);

        // Handle avatar URL with new API path
        if (profile.avatar) {
          profile.avatar = this.buildAvatarUrl(profile.avatar);
        }
      
        // Update component data
        this.profile = profile;
        this.error = null;
        return profile;
      } catch (error) {
        console.error('Profile fetch error:', error);
        this.error = error.message;
        this.profile = null;
        throw error; // Rethrow for created hook
      } finally {
        this.loading = false;
      }
    },

    async onFileChange(e) {
      try {
        const file = e.target.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append('avatar', file);

        const response = await fetch(this.apiEndpoints.profile, {
          method: 'POST',
          headers: {
            'Authorization': `Token ${this.getToken}`,
            'Accept': 'application/json',
          },
          body: formData,
          credentials: 'include'
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.message || 'Failed to upload avatar');
        }

        // Update profile with new data including avatar
        const updatedProfile = await response.json();

        // Ensure avatar URL uses HTTPS in production
        if (window.location.hostname !== 'localhost') {
          updatedProfile.avatar = updatedProfile.avatar.replace('http://', 'https://');
        }

        this.profile = updatedProfile;
        this.showStatus('Avatar updated successfully', {}, 'success');

      } catch (error) {
        console.error('Avatar upload error:', error);
        this.error = error.message;
        this.showStatus(error.message, {}, 'error');
      }
    },

    async deleteAvatar() {
      try {
        const response = await fetch(this.apiEndpoints.profile, {
          method: 'DELETE',
          headers: {
            'Authorization': `Token ${this.getToken}`
          }
        });

        if (!response.ok) {
          throw new Error('Failed to delete avatar');
        }

        // Update profile with new data including default avatar
        const updatedProfile = await response.json();
        this.profile = updatedProfile;

      } catch (error) {
        console.error('Avatar deletion error:', error);
        this.error = error.message;
      }
    },

    async checkDisplayName() {
      if (!this.displayName || this.displayName === this.profile.display_name) {
        this.isUpdateDisabled = true;
        return;
      }
      this.isUpdateDisabled = false;
    },

    async updatedisplayName() {
      try {
        const response = await fetch(this.apiEndpoints.profile, {
          method: 'PUT',
          headers: {
            'Authorization': `Token ${this.getToken}`,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          },
          credentials: 'include',
          body: JSON.stringify({
            display_name: this.displayName
          })
        });

        // Log the raw response
        console.log('Response status:', response.status);
        const responseText = await response.text();
        console.log('Response text:', responseText);

        // Try to parse JSON only if there's content
        let data;
        if (responseText) {
          try {
            data = JSON.parse(responseText);
          } catch (e) {
            console.error('JSON parse error:', e);
            throw new Error('Invalid server response format');
          }
        }
        if (!response.ok) {
          throw new Error(data?.message || 'Failed to update display name');
        }

        // Update profile with new data
        this.profile = data;
        this.displayNameError = null;
        this.isUpdateDisabled = true;
        this.showStatus('Profile updated successfully', {}, 'success');

      } catch (error) {
        console.error('Display name update error:', error);
        this.displayNameError = error.message;
        this.showStatus(error.message, {}, 'error');
      }
    },

    isFriend(profile) {
      return this.profile?.friends?.some(friend => friend.id === profile.id)
    },

    isBlocked(profile) {
      return profile.isBlocked; // Check the isBlocked flag from API response
    },

    async searchProfiles() {
      try {
        if (!this.searchQuery.trim()) {
          this.searchResults = [];
          this.showStatus('Please enter a search term', {}, 'warning');
          return;
        }

        this.isSearching = true;
        this.searchError = null;

        const response = await fetch(
        `${this.apiEndpoints.search}?q=${encodeURIComponent(this.searchQuery.trim())}`,
          {
            headers: {
              'Authorization': `Token ${this.getToken}`,
              'Content-Type': 'application/json',
              'Accept': 'application/json'
            },
            credentials: 'include'
          }
        );

        if (!response.ok) {
          throw new Error('Search failed');
        }

        const data = await response.json();
        console.log('Search results:', data); // Debug log
        this.searchResults = data;

        if (data.length === 0) {
          this.showStatus('No users found for "{query}"', { query: this.searchQuery }, 'warning');
        } else {
          this.showStatus('Found {count} users', { count: data.length }, 'success');
        }
      
      } catch (error) {
        console.error('Search error:', error);
        this.searchError = error.message;
        this.searchResults = [];
      } finally {
        this.isSearching = false;
      }
    },

    async blockUser(profileId) {
      try {
        const profile = this.searchResults.find(p => p.id === profileId);
        const response = await fetch(`${this.apiEndpoints.profile}${profileId}/block/`, {
          method: 'POST',
          headers: {
            'Authorization': `Token ${this.getToken}`,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          }
        });

        if (!response.ok) throw new Error('Failed to block user');
        
        this.searchResults = this.searchResults.map(profile => {
          if (profile.id === profileId) {
            return { ...profile, isBlocked: true };
          }
          return profile;
        });

        this.showStatus('User {name} has been blocked', { name: profile.display_name }, 'warning');
      } catch (error) {
        this.showStatus(error.message, 'error');
      }
    },

    async unblockUser(profileId) {
      try {
        const profile = this.searchResults.find(p => p.id === profileId);
        const response = await fetch(`${this.apiEndpoints.profile}${profileId}/block/`, {
          method: 'DELETE',
          headers: {
            'Authorization': `Token ${this.getToken}`,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          }
        });

        if (!response.ok) throw new Error('Failed to unblock user');

        this.searchResults = this.searchResults.map(profile => {
          if (profile.id === profileId) {
            return { ...profile, isBlocked: false };
          }
          return profile;
        });

        this.showStatus('User {name} has been unblocked', { name: profile.display_name }, 'success');
      } catch (error) {
        this.showStatus(error.message, 'error');
      }
    },

    async sendFriendRequest(friendId) {
      try {
        const friend = this.searchResults.find(p => p.id === friendId);
        const response = await fetch(`${this.apiEndpoints.profile}add_friend/`, {
          method: 'POST',
          headers: {
            'Authorization': `Token ${this.getToken}`,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          },
          body: JSON.stringify({ friend_profile_id: friendId }),
        });
        if (response.ok) {
          this.showStatus('Friend request sent to {name}', { name: friend.display_name }, 'success');
          // Update the search results to reflect the pending status
          this.searchResults = this.searchResults.map(profile => {
            if (profile.id === friendId) {
              profile.friend_request_status = 'pending';
              profile.requested_by_current_user = true;
            }
            return profile;
          });
        } else {
          console.error('Failed to send friend request');
        }
      } catch (error) {
        console.error('Error sending friend request:', error);
      }
    },

    async acceptFriendRequest(request) {
      try {
        const userId = this.extractUserId(request);
        await this.sendAcceptRequest(userId);
        this.updateLocalRequests(userId);
        this.showStatus('Friend request accepted', {}, 'success');
        await this.fetchProfile();
      } catch (error) {
        console.error('Accept error:', error);
        this.showStatus('Error: {msg}', { msg: error.message }, 'error');
      }
    },

    async sendAcceptRequest(userId) {
      const response = await fetch(`${this.apiEndpoints.friendRequests}accept/`, {
        method: 'POST',
        headers: {
          'Authorization': `Token ${this.getToken}`,
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ from_user_id: userId })
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || 'Failed to accept friend request');
      }
    },

    async declineFriendRequest(request) {
      try {
        const userId = this.extractUserId(request);
        await this.sendDeclineRequest(userId);
        this.updateLocalRequests(userId);
        this.showStatus('Friend request declined', {}, 'success');
      } catch (error) {
        console.error('Decline error:', error);
        this.showStatus('Error: {msg}', { msg: error.message }, 'error');
      }
    },

    // Helper methods
    extractUserId(request) {
      const userId = request.from_user_id || request.from_user?.id;
      if (!userId) throw new Error('Invalid request data');
      return userId;
    },

    async sendDeclineRequest(userId) {
      const response = await fetch(`${this.apiEndpoints.friendRequests}decline/`, {
        method: 'POST',
        headers: {
          'Authorization': `Token ${this.getToken}`,
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ from_user_id: userId })
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || 'Failed to decline friend request');
      }
    },

    updateLocalRequests(userId) {
      this.incomingFriendRequests = this.incomingFriendRequests.filter(
        req => (req.from_user_id || req.from_user?.id) !== userId
      );
      localStorage.setItem('incomingRequests', JSON.stringify(this.incomingFriendRequests));
    },

    async removeFriend(friendId) {
      try {
        const friend = this.profile.friends.find(f => f.id === friendId);
        const response = await fetch(`${this.apiEndpoints.profile}remove_friend/`, {
          method: 'POST',
          headers: {
            'Authorization': `Token ${this.getToken}`,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
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

    // Helper method to check friend request status
    getFriendRequestStatus(profile) {
      return profile.friend_request_status;
    },


    async fetchIncomingRequests() {
      try {
        console.log('Starting fetch of incoming requests');
        
        const response = await fetch(this.apiEndpoints.friendRequests, {
          headers: {
            'Authorization': `Token ${this.getToken}`,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          }
        });

        const data = await response.json();
        console.log('Raw API response:', data);

        // Validate data before processing
        if (!Array.isArray(data)) {
          throw new Error('Invalid response format');
        }
        
        // Map with validation
        const validRequests = data
          .filter(request => {
            const isValid = request && request.from_user;
            if (!isValid) console.warn('Invalid request:', request);
            return isValid;
          })
          .map(request => ({
            id: request.id,
            from_user: {
              id: request.from_user.id,
              display_name: request.from_user.display_name,
              avatar: this.buildAvatarUrl(request.from_user.avatar, baseUrl),
              is_online: !!request.from_user.is_online
            },
            status: request.status
          }));

        console.log('Processed requests:', validRequests);
        this.incomingFriendRequests = validRequests;

      } catch (error) {
        console.error('Fetch error:', error);
        this.incomingFriendRequests = []; // Reset on error
      }
    },

    // Helper method for avatar URL
    buildAvatarUrl(avatarPath) {
      if (!avatarPath) {
        console.log('No avatar path, using default');
        return `${this.getBaseUrl()}/api/user/media/default_avatar.png`;
      }
      // If it's an absolute URL
      if (avatarPath.startsWith('http')) {
        // Force HTTPS in production
        return window.location.protocol === 'https:'
          ? avatarPath.replace('http://', 'https://')
          : avatarPath;
      }

          // For relative paths, ensure proper API prefix
      const filename = avatarPath.split('/').pop(); // Get just the filename
      return `${this.getBaseUrl()}/api/user/media/${filename}`;
    },

    formatDate(timestamp) {
      if (!timestamp) return '';
      try {
        return new Date(timestamp).toLocaleTimeString();
      } catch (e) {
        console.error('Date parsing error:', e);
        return '';
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
        const response = await fetch(`${this.apiEndpoints.chat}${friend.id}/`, {
          method: 'GET',
          headers: {
            'Authorization': `Token ${this.getToken}`,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
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
        const wsUrl = `${wsScheme}://${window.location.host}/api/chat/ws/${this.chatId}/?token=${this.getToken}`;
        
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


    async logout() {
      try {
        // Send offline status
        if (this.notificationSocket && this.notificationSocket.readyState === WebSocket.OPEN) {
          this.notificationSocket.send(JSON.stringify({
            type: 'friend_status',
            status: 'offline'
          }));
          
          await new Promise(resolve => setTimeout(resolve, 100));
          this.notificationSocket.close();
        }

        localStorage.removeItem('incomingRequests');
        
        // Clear store and redirect
        await this.$store.dispatch('logoutAction');
        this.$router.push('/login');
      } catch (error) {
        console.error('Logout error:', error);
      }
    },

    // WebSocket methods
    initNotificationSocket() {
      //Get token from store
      const token = this.getToken;
      const wsScheme = window.location.protocol === 'https:' ? 'wss' : 'ws';
      const wsHost = window.location.hostname;
      const wsUrl = `${wsScheme}://${wsHost}/api/user/ws/notifications/?token=${this.getToken}`;
      console.log('Attempting WebSocket connection:', wsUrl);
      this.notificationSocket = new WebSocket(wsUrl);
      this.notificationSocket.onopen = () => {
        this.wsConnected = true;
        console.log('WebSocket connected');
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
                    avatar: this.buildAvatarUrl(data.from_user_avatar, this.getBaseUrl()),
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

    // Cleanup on component destruction
    beforeDestroy() {
      if (this.notificationSocket) {
        this.notificationSocket.close();
      }
      if (this.chatSocket) {
        this.chatSocket.close();
      }
    }
  }
};
</script>

<style scoped>
.profile-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
  font-family: Arial, sans-serif;
}

.profile-card {
  padding: 20px;
  width: 100%;
  max-width: 600px;
  text-align: center;
  margin-bottom: 20px;
}

.profile-section {
  margin-bottom: 20px;
}

.avatar-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 20px;
}

.profile-picture {
  width: 150px;
  height: 150px;
  border-radius: 50%;
  border: 2px solid #000000;
  margin-bottom: 10px;
}

.avatar-actions {
  display: flex;
  gap: 10px;
}

.file-input {
  display: none;
}

.profile-form {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 10px;
}

.error-message {
  color: red;
  font-size: 12px;
  margin-top: 5px;
}

.friend-actions {
  margin-left: auto;
  display: flex;
  gap: 10px;
}

.friend-management {
  display: flex;
  gap: 8px;
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
  background: #333333;
  color: white;
}

.primary-btn:hover {
  background: #03a670;
}

.primary-btn:disabled {
  background-color: #5b5b5b;
  cursor: not-allowed;
}

.secondary-btn {
  background: #333333;
  color: #ffffff;
}

.secondary-btn:hover {
  background: #a60303;
}

.warning-btn {
  background: #a60303;
  color: white;
}

.action-buttons {
  display: flex;
  gap: 10px;
}

.accept-btn {
  background: #03a670;
  color: white;
}

.decline-btn {
  background: #a60303;
  color: white;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
}

.enabled-btn {
  animation: pulse 1s infinite; /* Apply the pulse animation */
}

.block-btn {
  background: #a60303;
  color: white;
}

.unblock-btn {
  background: #666;
  color: white;
}

.btn:hover {
  opacity: 0.8;
}

.search-results {
  list-style: none;
  padding-top: 1%;
  padding-bottom: 1%;
  margin: 0;
}

.profile-item {
  display: flex;
  align-items: center;
  margin-bottom: 1%;
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
  padding-left: 5%;
  padding-right: 5%;
}

.status {
  padding-left: 5%;
  padding-right: 5%;
  margin-right: 10px;
}

.status.online {
  color: green;
}

.status.offline {
  color: red;
}

nav {
  text-align: right;
}

nav .btn {
  margin: 1em 0;
}

.chat-container {
  height: 500px;
  display: flex;
  flex-direction: column;
  border-radius: 10px;
  box-shadow: 2px 2px 30px #03a670;
}

.chat-header {
  padding: 1rem;
  background: #2d2d2d;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #ffffff;
  border-radius: 10px;
}

.chat-header h4 {
  color: #ffffff;
  font-size: 1.1rem;
  font-weight: 500;
  margin: 0;
  padding: 0;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.chat-messages {
  flex-grow: 1;
  overflow: auto;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  background: #1a1a1a;
  scroll-behavior: smooth;
}

.message {
  display: flex;
  max-width: 70%;
  margin-bottom: 1rem;
}

.message-sent {
  margin-left: auto;
  margin-right: 1%;
}

.message-received {
  margin-right: auto;
  margin-left: 1%;
  text-align: left;
}

.message-sender {
  font-weight: bold;
  margin-bottom: 4px;
  
}

.message-content {
  padding: 1rem;
  border-radius: 1rem;
  position: relative;
  min-width: 100px;
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
  display: block;
  text-align: left;
}

.message-text {
  word-break: break-word;
  font-size: 0.9rem;
  line-height: 1.4;
}

.chat-input {
  padding: 1rem;
  background: #2d2d2d;
  border-top: 1px solid #404040;
  border-radius: 10px;
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

.status-text {
  color: #666;
  font-style: italic;
}

input {
  width: 100%;
  padding: 10px;
  box-sizing: border-box;
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