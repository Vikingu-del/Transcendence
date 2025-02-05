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
          :src="profile.avatar" 
          :alt="profile.display_name"
          class="profile-picture"
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
          <h4>Chat with {{ activeChat }}</h4>
          <button @click="closeChat" class="btn secondary-btn">Close</button>
        </div>
        <div class="chat-messages">
          <div v-for="message in messages" :key="message.timestamp" class="chat-message">
            <span class="chat-username">{{ message.sender }}:</span>
            <span class="chat-text">{{ message.message }}</span>
            <span class="chat-time">{{ new Date(message.timestamp).toLocaleTimeString() }}</span>
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
      defaultAvatarUrl: 'http://localhost:8000/media/default.png',
      isDefaultAvatar: true,

      // Profile Search
      searchQuery: '',
      searchResults: [],
      isSearching: false,
      searchError: null,
      searchTimeout: null,
      currentUserId: null,

      //Web Socket
      socket: null,
      wsConnected: false,

      // Friend Requests
      incomingFriendRequests: JSON.parse(localStorage.getItem('incomingRequests') || '[]'),

      // Chat
      showChat: false,
      activeChat: null,
      messages: [],
      newMessage: '',

      // Status Message
      statusMessage: null
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
    }
  },

  async created() {
    if (this.isInitialized) return;
    
    const authInitialized = await this.$store.dispatch('initializeAuth');
    
    if (!authInitialized || !this.getToken) {
      this.$router.push('/login');
      return;
    }
    
    this.isInitialized = true;
    this.currentUserId = this.$store.state.user?.id
    await this.fetchProfile();
    this.fetchIncomingRequests();
    this.connectWebSocket();

  },

  methods: {

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
        const response = await fetch('http://localhost:8000/api/profile/', {
          headers: {
            'Authorization': `Token ${this.getToken}`,
            'Content-Type': 'application/json'
          },
        });
        
        if (!response.ok) {
          if (response.status === 401) {
            await this.$store.dispatch('logoutAction');
            this.$router.push('/login');
            return;
          }
          throw new Error('Failed to fetch profile');
        }
        
        this.profile = await response.json();
        this.error = null;
      } catch (error) {
        console.error('Profile fetch error:', error);
        this.error = error.message;
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

        const response = await fetch('http://localhost:8000/api/profile/', {
          method: 'PUT',
          headers: {
            'Authorization': `Token ${this.getToken}`
          },
          body: formData
        });

        if (!response.ok) {
          throw new Error('Failed to upload avatar');
        }

        // Update profile with new data including avatar
        const updatedProfile = await response.json();
        this.profile = updatedProfile;

      } catch (error) {
        console.error('Avatar upload error:', error);
        this.error = error.message;
      }
    },

    async deleteAvatar() {
      try {
        const response = await fetch('http://localhost:8000/api/profile/', {
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
        const response = await fetch('http://localhost:8000/api/profile/', {
          method: 'PUT',
          headers: {
            'Authorization': `Token ${this.getToken}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            display_name: this.displayName
          })
        });

        if (!response.ok) {
          const data = await response.json();
          if (response.status === 400) {
            this.displayNameError = data.message;
            return;
          }
          throw new Error('Failed to update display name');
        }

        // Update profile with new data
        const updatedProfile = await response.json();
        this.profile = updatedProfile;
        this.displayNameError = null;
        this.isUpdateDisabled = true;

      } catch (error) {
        console.error('Display name update error:', error);
        this.displayNameError = error.message;
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
          `http://localhost:8000/api/profile/search/?q=${encodeURIComponent(this.searchQuery.trim())}`,
          {
            headers: {
              'Authorization': `Token ${this.getToken}`,
              'Content-Type': 'application/json'
            }
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
        const response = await fetch(`/api/profile/${profileId}/block/`, {
          method: 'POST',
          headers: {
            'Authorization': `Token ${this.getToken}`,
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
        const response = await fetch(`/api/profile/${profileId}/block/`, {
          method: 'DELETE',
          headers: {
            'Authorization': `Token ${this.getToken}`,
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
        const response = await fetch('/api/profile/add_friend/', {
          method: 'POST',
          headers: {
            'Authorization': `Token ${this.getToken}`,
            'Content-Type': 'application/json',
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
      const response = await fetch('/api/profile/friend-requests/accept/', {
        method: 'POST',
        headers: {
          'Authorization': `Token ${this.getToken}`,
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
      const response = await fetch('/api/profile/friend-requests/decline/', {
        method: 'POST',
        headers: {
          'Authorization': `Token ${this.getToken}`,
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

    // Helper method to check friend request status
    getFriendRequestStatus(profile) {
      return profile.friend_request_status;
    },


    async fetchIncomingRequests() {
    try {
      console.log('Starting fetch of incoming requests');
      
      const response = await fetch('/api/profile/friend-requests/', {
        headers: {
          'Authorization': `Token ${this.getToken}`,
          'Content-Type': 'application/json'
        }
      });

      const data = await response.json();
      console.log('Raw API response:', data);

      // Validate data before processing
      if (!Array.isArray(data)) {
        throw new Error('Invalid response format');
      }

      const baseUrl = 'http://localhost:8000';
      
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
    buildAvatarUrl(avatarPath, baseUrl) {
      if (!avatarPath) return `${baseUrl}/media/default.png`;
      if (avatarPath.startsWith('http')) return avatarPath;
      return `${baseUrl}${avatarPath}`;
    },

    async startChat(friend) {
      // Initialize chat
    },
    async sendMessage() {
      // Handle message sending
    },
    closeChat() {
      // Close chat window
    },
    async logout() {
      await this.$store.dispatch('logoutAction');
      this.$router.push('/login');
    },

    // WebSocket methods
    connectWebSocket() {
      //Get token from store
      const token = this.getToken;
      this.socket = new WebSocket(`ws://localhost:8000/ws/profile/notifications/?token=${token}`);
      this.socket.onopen = () => {
        this.wsConnected = true;
      };
      this.socket.onmessage = (e) => {
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
            const friend = this.friends.find(f => f.id === friendId);
            if (friend) {
              friend.is_online = (status === 'online');
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
      this.socket.onclose = () => {
        this.wsConnected = false;
      };
    },

    // Cleanup on component destruction
    beforeDestroy() {
      if (this.socket) {
        this.socket.close();
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

.input-field,
.file-input {
  padding: 10px;
  border: 1px solid #4caf50;
  border-radius: 5px;
  font-size: 14px;
  width: 100%;
}

.error-message {
  color: red;
  font-size: 12px;
  margin-top: 5px;
}

.friend-actions {
  display: flex;
  gap: 10px;
}

.friend-management {
  display: flex;
  gap: 8px;
}

.btn {
  padding: 6px 12px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
}

.primary-btn {
  background-color: #4CAF50;
  color: white;
}

.secondary-btn {
  background-color: #f44336;
  color: white;
}

.warning-btn {
  background: #ff4444;
  color: white;
  overlay: #cc0000;
}

.action-buttons {
  display: flex;
  gap: 10px;
}

.accept-btn {
  background: #4CAF50;
  color: white;
}

.decline-btn {
  background: #f44336;
  color: white;
}

.primary-btn:disabled {
  background-color: #5b5b5b;
  cursor: not-allowed;
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
  background: #ff4444;
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
  padding: 0;
  margin: 0;
}

.profile-item {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.profile-avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  margin-right: 10px;
}

.profile-name {
  font-size: 16px;
  flex-grow: 1;
}

.status {
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
  margin-top: 20px;
}

.chat-box {
  border: 1px solid #ccc;
  padding: 10px;
  height: 200px;
  overflow-y: scroll;
}

.chat-message {
  margin-bottom: 10px;
}

.chat-username {
  font-weight: bold;
}

.warning-btn {
  background-color: #dc3545;
  color: white;
  margin-left: 8px;
}

.friend-management {
  display: flex;
  gap: 8px;
}

.friend-actions {
  margin-left: auto;
  display: flex;
  gap: 8px;
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