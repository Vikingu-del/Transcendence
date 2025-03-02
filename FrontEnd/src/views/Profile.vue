<template>
  <div class="profile-container">
    <!-- Profile Card -->
    <div class="profile-card" v-if="profile">
      <!-- Avatar Section with Upload/Delete -->
      <div class="avatar-container">
        <!-- Avatar Image -->
        <img 
            :src="buildAvatarUrl(profile.avatar)"
            @error="handleAvatarError"
            class="profile-picture"
            alt="Profile Picture"
            :key="profile.avatar"
        />

        <div class="avatar-actions">
          <input type="file" @change="onFileChange" class="file-input" id="avatar-upload" />
          <label for="avatar-upload" class="btn primary-btn">Change Avatar</label>
          <button 
            v-if="!isDefaultAvatar" 
            @click="deleteAvatar" 
            class="btn secondary-btn"
          >
            Delete Avatar
          </button>
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
      <!-- Match History -->
      <div class="match-history" v-if="profile">
          <h3>Match History</h3>
          
          <div v-if="!profile.match_history || profile.match_history.length === 0" class="no-matches">
            No matches played yet
          </div>
          
          <ul v-else class="match-list">
            <li v-for="match in profile.match_history" :key="match.id" 
            :class="['match-item', match.result.toLowerCase()]">
            <div class="match-result">{{ match.result }}</div>
            <div class="match-score">{{ match.score }}</div>
            <div class="match-opponent">You vs {{ match.opponentDisplayName || match.opponent }}</div>
          </li>
        </ul>
      </div>
    </div>

    <div 
      v-if="statusMessage" 
      :class="['status-message', statusMessage.type]"
    >
      {{ statusMessage.text }}
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
import axios from '@/plugins/axios';
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
      defaultAvatarUrl: '/api/user/media/default.png',
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

      // Status Message
      statusMessage: null,

      //Auth Token
      token: localStorage.getItem('token'),
    };
  },

  computed: {
    getToken() {
      return this.token;
    },
    isAuthenticated() {
      return !!this.token;
    },
    isDefaultAvatar() {
      return !this.profile.avatar || this.profile.avatar.includes('default.png');
    },
  },

  watch: {
    displayName() {
      this.checkDisplayName();
    },
    messages: {
      handler() {
        this.scrollToBottom();
      },
      deep: true
    }
  },

  // Update the created hook:
  async created() {
    try {
      const token = localStorage.getItem('token');
      console.log('Initial token:', token);
      
      if (!token) {
        await this.$router.push('/login');
        return;
      }

      await this.fetchProfile();
      this.updateOnlineStatus(true);
    } catch (error) {
      console.error('Profile initialization error:', error);
    }
  },

  mounted() {
    // this.initNotificationSocket();
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
      this.statusMessage = { text, type };

      // Clear after timeout
      setTimeout(() => {
        this.statusMessage = null;
      }, 3000);
    },

    async updateOnlineStatus(status) {
      try {
        const token = localStorage.getItem('token');
        const response = await fetch('/api/user/profile/online-status/', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ status })
        });

        if (!response.ok) {
          throw new Error('Failed to update online status');
        }
      } catch (error) {
        console.error('Error updating online status:', error);
      }
    },

    async fetchProfile() {
      try {
        const token = localStorage.getItem('token');
        console.log('Fetching profile with token:', token);

        if (!token) {
          throw new Error('No auth token found');
        }

        const response = await fetch('/api/user/profile/', {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
        });

        if (!response.ok) {
          const errorText = await response.text();
          console.error(`Profile fetch failed: ${response.status}`, errorText);
          throw new Error(errorText);
        }

        this.profile = await response.json();
        this.profile.is_online = true;
        this.currentUserId = this.profile.id;
        this.loading = false;
        
        await this.fetchMatchHistory();
      } catch (error) {
        console.error('Profile fetch error:', error);
        if (error.message.includes('token_not_valid')) {
          this.$router.push('/login');
        }
        throw error;
      }
    },

    async changeUserNameOfOpponentToDisplayName(opponentId) {
      try {
        const token = localStorage.getItem('token');
        const response = await fetch(`/api/user/profile/${opponentId}/`, {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });

        if (!response.ok) {
          throw new Error('Failed to fetch opponent profile');
        }

        const opponentProfile = await response.json();
        return opponentProfile.display_name;
      } catch (error) {
        console.error('Error fetching opponent profile:', error);
        return 'Unknown';
      }
    },

    async fetchMatchHistory() {
      try {
        const token = localStorage.getItem('token');
        if (!token) {
          throw new Error('No auth token found');
        }
        
        // Use the profile ID to fetch match history for the current user
        const userId = this.profile.id;
        const response = await fetch(`/api/game/match-history/${userId}/`, {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });
            
        if (!response.ok) {
          throw new Error('Failed to fetch match history');
        }
        
        const matchHistory = await response.json();
        
        // Fetch display names for all opponents
        for (const match of matchHistory) {
          if (match.opponent_id) {
            try {
              match.opponentDisplayName = await this.changeUserNameOfOpponentToDisplayName(match.opponent_id);
            } catch (error) {
              console.error('Error fetching opponent display name:', error);
              match.opponentDisplayName = match.opponent || 'Unknown';
            }
          } else {
            // Solo games or missing opponent_id
            match.opponentDisplayName = match.opponent || 'Solo Game';
          }
        }
        
        if (this.profile) {
          this.profile.match_history = matchHistory;
        }
        
        console.log('Fetched match history with display names:', matchHistory);
      } catch (error) {
        console.error('Error fetching match history:', error);
      }
    },

    async onFileChange(e) {
      try {
        const token = localStorage.getItem('token');
        console.log('Fetching profile with token:', token);

        if (!token) {
          throw new Error('No auth token found');
        }
        const file = e.target.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append('avatar', file);

        const response = await fetch('/api/user/profile/', { // Removed port 8000
          method: 'PUT',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
          body: formData
        });

        if (!response.ok) {
          throw new Error('Failed to upload avatar');
        }

        // Update profile with new data including avatar
        const updatedProfile = await response.json();
        this.profile = updatedProfile;
        
        // Reset avatar load error flag
        
        // Force image reload by adding timestamp
        if (this.profile.avatar) {
          this.profile.avatar = `${this.profile.avatar}`;
        }

        this.showStatus('Avatar updated successfully', {}, 'success');
      } catch (error) {
        console.error('Avatar upload error:', error);
        this.showStatus(error.message, {}, 'error');
      }
    },

    async deleteAvatar() {
      try {
        const token = localStorage.getItem('token');
        // if (this.profile.avatar === '/api/user/media/default.png') {
        //   throw new Error('Cannot delete default avatar');
        // }
        const response = await fetch('/api/user/profile/', {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        if (!response.ok) {
          throw new Error('Failed to delete avatar');
        }

        // Update profile with new data including default avatar
        const updatedProfile = await response.json();
        this.profile = updatedProfile;

        // Reset avatar to defualt avatar
        this.profile.avatar = '/api/user/media/default.png';
        // Refresh Page
        // this.$router.go();
        this.showStatus('Avatar deleted successfully', {}, 'success');



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
        const token = localStorage.getItem('token');
        if (!token) {
          throw new Error('No auth token found');
        }

        const response = await fetch('/api/user/profile/', {
          method: 'PUT',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          },
          body: JSON.stringify({
            display_name: this.displayName
          })
        });

        const data = await response.json();

        if (!response.ok) {
          if (response.status === 400) {
            // Show error status message for duplicate display name
            this.showStatus('Display name already exists', {}, 'error');
            this.displayNameError = data.message;
            return;
          }
          throw new Error('Failed to update display name');
        }

        // Update profile with new data
        this.profile = data;
        this.displayNameError = null;
        this.isUpdateDisabled = true;
        
        // Show success message
        this.showStatus('Display name updated successfully', {}, 'success');

      } catch (error) {
        console.error('Display name update error:', error);
        this.displayNameError = error.message;
        // Show error status message for other errors
        this.showStatus(error.message, {}, 'error');
      }
    },

    // Helper methods
    extractUserId(request) {
      // Handle both object formats and direct ID input
      if (typeof request === 'number') {
        return request;
      }

      if (!request) {
        throw new Error('Request object is required');
      }

      // Try different possible paths to get the user ID
      const userId = request.from_user_id || // Direct ID
                    (request.from_user && request.from_user.id) || // Nested user object
                    request.id; // Direct profile ID

      if (!userId) {
        console.error('Invalid request structure:', request);
        throw new Error('Invalid request data: User ID not found');
      }

      return userId;
    },

    buildAvatarUrl(avatarPath) {
      console.log('Building avatar URL:', avatarPath);
      // If no avatar path or it's the default avatar path
      if (!avatarPath || avatarPath.includes('default.png')) {
        return this.defaultAvatarUrl;
      }

      // If it's already a full URL
      if (avatarPath.startsWith('/api/user/media/')) {
        return avatarPath;
      }

      // For any other case, assume it's a relative path
      return `/api/user/media/${avatarPath}`;
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

    async logout() {
      try {
        // Set offline status before logging out
        await this.updateOnlineStatus(false);

        // Clear local storage
        await this.$store.dispatch('logoutAction');
        localStorage.removeItem('incomingRequests');
        
        // Reset component state
        this.token = null;
        this.profile = null;
        
        // Redirect to login
        this.$router.push('/login');
      } catch (error) {
        console.error('Logout error:', error);
      }
    },

    // Cleanup on component destruction
    beforeDestroy() {
      // Set offline status when component is destroyed
      this.updateOnlineStatus(false);

      // Close ChatWebSocket connection
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

.match-history {
  width: 100%;
  max-width: 600px;
  margin-top: 20px;
  padding: 15px;
  border-radius: 8px;
}

.match-history h3 {
  margin-top: 0;
  margin-bottom: 15px;
  text-align: center;
}

.no-matches {
  text-align: center;
  font-style: italic;
  color: #666;
}

.match-list {
  list-style: none;
  padding: 0;
}

.match-item {
  display: inline-flex;
  width: 100%;
  justify-content: space-between;
  padding: 10px 15px;
  margin-bottom: 8px;
  border-radius: 4px;
  background-color: #808080;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.match-item.win {
  border-left: 4px solid #4caf50;
}

.match-item.loss {
  border-left: 4px solid #f44336;
}

.match-result {
  font-weight: bold;
}

.match-result.win {
  color: #4caf50;
}

.match-result.loss {
  color: #f44336;
}

.match-score {
  padding-left: 15%;
  font-size: 1rem;
  font-weight: bold;
}

.match-opponent {
  font-size: 0.9rem;
  color: #333;
}

</style>