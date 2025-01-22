<template>
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

      <!-- Search Profiles Section -->
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
            <img :src="profile.avatar" :alt="profile.display_name" class="profile-avatar">
            <p>{{ profile.display_name }}</p>
            <div class="friend-actions">
              <div v-if="profile.friend_request_status === 'pending'">
                <div v-if="profile.requested_by_current_user">
                  <p class="status-text">Request Pending</p>
                </div>
                <div v-else>
                  <button @click="acceptFriendRequest(profile.id)" class="btn primary-btn">Accept</button>
                  <button @click="declineFriendRequest(profile.id)" class="btn secondary-btn">Decline</button>
                </div>
              </div>
              <div v-else-if="profile.is_friend">
                <button @click="removeFriend(profile.id)" class="btn secondary-btn">Remove Friend</button>
              </div>
              <div v-else>
                <button @click="sendFriendRequest(profile.id)" class="btn primary-btn">Add Friend</button>
              </div>
            </div>
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
      searchError: null,
      isSearching: false,
      searchTimeout: null,

      // Chat
      showChat: false,
      activeChat: null,
      messages: [],
      newMessage: ''
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
    await this.fetchProfile();
    this.connectWebSocket();

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

    async searchProfiles() {
      try {
        if (!this.searchQuery.trim()) {
          this.searchResults = [];
          return;
        }

        this.isSearching = true;
        this.searchError = null;

        const response = await fetch(
          `http://localhost:8000/api/profile/search/?q=${encodeURIComponent(this.searchQuery)}`,
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
        this.searchResults = data;

      } catch (error) {
        console.error('Search error:', error);
        this.searchError = error.message;
        this.searchResults = [];
      } finally {
        this.isSearching = false;
      }
    },

    async sendFriendRequest(friendId) {
      try {
        const response = await fetch('/api/profile/add_friend/', {
          method: 'POST',
          headers: {
            'Authorization': `Token ${this.getToken}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ friend_profile_id: friendId }),
        });
        if (response.ok) {
          alert('Friend request sent successfully');
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

    async acceptFriendRequest(fromUserId) {
      try {
        const response = await fetch('/api/profile/accept_friend_request/', {
          method: 'POST',
          headers: {
            'Authorization': `Token ${this.getToken}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ from_user_id: fromUserId }),
        });
        if (response.ok) {
          alert('Friend request accepted successfully');
          // Remove the request from the list
          this.incomingFriendRequests = this.incomingFriendRequests.filter(req => req.from_user_id !== fromUserId);
          // Update the friends list
          this.fetchProfile();
        } else {
          console.error('Failed to accept friend request');
        }
      } catch (error) {
        console.error('Error accepting friend request:', error);
      }
    },

    async declineFriendRequest(fromUserId) {
      try {
        const response = await fetch('/api/profile/decline_friend_request/', {
          method: 'POST',
          headers: {
            'Authorization': `Token ${this.getToken}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ friend_profile_id: fromUserId }),
        });
        if (response.ok) {
          alert('Friend request declined successfully');
          // Remove the request from the list
          this.incomingFriendRequests = this.incomingFriendRequests.filter(req => req.from_user_id !== fromUserId);
        } else {
          console.error('Failed to decline friend request');
        }
      } catch (error) {
        console.error('Error declining friend request:', error);
      }
    },

    async removeFriend(friendId) {
      try {
        const response = await fetch('/api/profile/remove_friend/', {
          method: 'POST',
          headers: {
            'Authorization': `Token ${this.getToken}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ friend_profile_id: friendId }),
        });
        if (response.ok) {
          alert('Friend removed successfully');
          // Refresh friends list
          this.fetchProfile();
          // Send WebSocket notification
          this.socket.send(JSON.stringify({
            type: 'friend_removed',
            user_id: this.currentUserId,
          }));
        } else {
          console.error('Failed to remove friend');
        }
      } catch (error) {
        console.error('Error removing friend:', error);
      }
    },

    async fetchIncomingFriendRequests() {
      try {
        const response = await fetch('/api/profile/incoming_friend_requests/', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
          },
        });
        if (response.ok) {
          const data = await response.json();
          this.incomingFriendRequests = data.requests || [];
        } else {
          console.error('Failed to fetch incoming friend requests');
          this.incomingFriendRequests = [];
        }
      } catch (error) {
        console.error('Error fetching incoming friend requests:', error);
        this.incomingFriendRequests = [];
      }
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
      // Handle logout
    },

    // NEED TO CHANGE WEB SOCKETS TO WORK WITH AUTHENTICATION TOKENS 

    // WebSocket methods
    // connectWebSocket() {
    //   const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    //   this.socket = new WebSocket(`${protocol}//${window.location.host}/ws/profile/notifications/`);
    //   this.socket.onmessage = (event) => {
    //     const data = JSON.parse(event.data);
    //     this.notifications.push(data);

    //     if (data.type === 'friend_request') {
    //       // Add the new friend request to the list
    //       this.incomingFriendRequests.push({
    //         from_user_id: data.from_user_id,
    //         from_user_name: data.from_user_name,
    //         avatar: data.from_user_avatar,
    //       });
    //     } else if (data.type === 'friend_status') {
    //       // Update friend's online status
    //       const friendId = data.user_id;
    //       const status = data.status;
    //       const friend = this.friends.find(f => f.id === friendId);
    //       if (friend) {
    //         friend.is_online = (status === 'online');
    //       } else {
    //         friend.is_online = (status === 'offline');
    //       }
    //     } else if (data.type === 'friend_request_accepted') {
    //       // Update the friends list
    //       this.fetchProfile();
    //     } else if (data.type === 'friend_request_declined') {
    //       // Handle friend request declined
    //       alert(`Your friend request to ${data.user_name} was declined.`);
    //     } else if (data.type === 'friend_removed') {
    //       // Handle friend removed
    //       this.friends = this.friends.filter(friend => friend.id !== data.user_id);
    //     }
    //   };
    //   this.socket.onclose = () => {
    //     console.log('WebSocket connection closed');
    //   };
    // }
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
  border: 2px solid #4caf50;
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

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  font-size: 14px;
  cursor: pointer;
}

.primary-btn {
  background-color: #4caf50;
  color: white;
  transition: transform 0.3s ease; /* Add transition for smooth animation */
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

.secondary-btn {
  background-color: #f44336;
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

input {
  width: 100%;
  padding: 10px;
  box-sizing: border-box;
}

</style>