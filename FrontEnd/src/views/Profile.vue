<template>
  <div v-if="statusMessage" class="status-message" :class="statusMessage.type">
    {{ statusMessage.text }}
  </div>
  <div class="profile-container">
    <!-- Profile Card -->
    <div class="profile-card" v-if="profile">
      <!-- Avatar Section with Upload/Delete -->
      <div class="avatar-container">
        <!-- Если аватар не найден, показываем текст -->
        <img 
          v-if="!avatarLoadError"
          :src="profile ? buildAvatarUrl(profile.avatar) : defaultAvatarUrl"
          @error="handleAvatarError"
          class="profile-picture"
          alt="Profile Picture"
        />
        
        <!-- Если возникла ошибка при загрузке аватара, показываем текст -->
        <span v-if="avatarLoadError" class="avatar-text">
          {{ profile.display_name.charAt(0).toUpperCase() }} <!-- Показываем первую букву имени пользователя -->
        </span>

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
    </div>
      <div class="profile-section">
        <h3 v-if="incomingFriendRequests.length" class="section-title">
          Incoming Friend Requests ({{ incomingFriendRequests.length }})
        </h3>
        <div class="friend-requests-list">
          <div v-for="request in incomingFriendRequests" 
              :key="request.id" 
              class="request-item">
            <div class="request-user-info">
              <img 
                :src="buildAvatarUrl(request.from_user.avatar)" 
                :alt="request.from_user.display_name"
                class="request-avatar"
                @error="handleAvatarError"
              >
              <span class="request-name">{{ request.from_user.display_name }}</span>
            </div>
            <div class="request-actions">
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
      </div>


    <!-- Loading and Error States -->
    <div v-if="loading">Loading...</div>
    <div v-if="error" class="error">{{ error }}</div>

    <!-- Add this after the search section -->
    <div v-if="profile" class="debug-section">
      <h3>Debug Information</h3>
      <div class="debug-info">
        <pre>
    User Profile:
    -------------
    ID: {{ profile.id }}
    Display Name: {{ profile.display_name }}
    Avatar URL: {{ profile.avatar }}
    Is Online: {{ profile.is_online }}
    Default Avatar: {{ isDefaultAvatar }}

    Friends List:
    -------------
    <template v-if="profile.friends && profile.friends.length">
    <span v-for="friend in profile.friends" :key="friend.id">
    Friend ID: {{ friend.id }}
    Name: {{ friend.display_name }}
    Status: {{ friend.is_online ? 'Online' : 'Offline' }}
    Avatar: {{ friend.avatar }}
    -------------------
    </span>
    </template>
    <template v-else>No friends</template>

    WebSocket:
    -------------
    Connected: {{ wsConnected }}
    Current User ID: {{ currentUserId }}

    Pending Requests:
    -------------
    <template v-if="incomingFriendRequests.length">
    <span v-for="request in incomingFriendRequests" :key="request.id">
    Request ID: {{ request.id }}
    From User: {{ request.from_user.display_name }}
    Status: {{ request.status }}
    -------------------
    </span>
    </template>
    <template v-else>No pending requests</template>
        </pre>
      </div>
    </div>


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
      defaultAvatarUrl: 'https://localhost/api/user/static/default/default.png',
      avatarLoadError: false,
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
    // Remove mapGetters and add direct token getter
    getToken() {
      return this.token;
    },
    isAuthenticated() {
      return !!this.token;
    },
    isDefaultAvatar() {
      return !this.profile.avatar || 
            this.profile.avatar === '/api/user/static/default/default.png';
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
      await this.fetchIncomingRequests();
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

      // Set status message
      this.statusMessage = { text, type };

      // Clear after timeout
      setTimeout(() => {
        this.statusMessage = null;
      }, 3000);
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
          // credentials: 'include'
        });

        if (!response.ok) {
          const errorText = await response.text();
          console.error(`Profile fetch failed: ${response.status}`, errorText);
          throw new Error(errorText);
        }

        const data = await response.json();
        this.profile = data;
        this.loading = false;

        // Set display name for editing
        await this.fetchIncomingRequests();
        
      } catch (error) {
        console.error('Profile fetch error:', error);
        if (error.message.includes('token_not_valid')) {
          // Token expired or invalid - redirect to login
          this.$router.push('/login');
        }
        throw error;
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

        const response = await fetch('https://localhost/api/user/profile/', { // Removed port 8000
          method: 'PUT',
          headers: {
            'Authorization': `Bearer ${token}`
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
        this.avatarLoadError = false;
        
        // Force image reload by adding timestamp
        if (this.profile.avatar) {
          this.profile.avatar = `${this.profile.avatar}?t=${Date.now()}`;
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
        this.profile.avatar = '/api/user/media/avatars/default.png';
        this.avatarLoadError = false;
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
      const token = localStorage.getItem('token');
      if (!token) {
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
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json',
              'Accept': 'application/json'
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
        // Token
        const token = localStorage.getItem('token');
        if (!token) {
          throw new Error('No auth token found');
        }
        const profile = this.searchResults.find(p => p.id === profileId);
        const response = await fetch(`/api/user/profile/${profileId}/block/`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
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
        // Token
        const token = localStorage.getItem('token');
        if (!token) {
          throw new Error('No auth token found');
        }
        const profile = this.searchResults.find(p => p.id === profileId);
        const response = await fetch(`/api/user/profile/${profileId}/block/`, {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
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
        const token = localStorage.getItem('token');
        console.log('Fetching profile with token:', token);

        if (!token) {
          throw new Error('No auth token found');
        }
        // Find friend in search results
        const friend = this.searchResults.find(p => p.id === friendId);
        if (!friend) {
          throw new Error('Friend not found in search results');
        }

        // Make API request
        const response = await fetch('/api/user/profile/add_friend/', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          },
          body: JSON.stringify({ friend_profile_id: friendId })
        });

        console.log('Friend request response:', response); // Debug log

        // Parse response
        const data = await response.json();
        
        if (!response.ok) {
          throw new Error(data.error || 'Failed to send friend request');
        }

        // Update UI
        this.searchResults = this.searchResults.map(profile => {
          if (profile.id === friendId) {
            return {
              ...profile,
              friend_request_status: 'pending',
              requested_by_current_user: true
            };
          }
          return profile;
        });

        // Show success message
        this.showStatus('Friend request sent to {name}', { name: friend.display_name }, 'success');
        
        // Refresh profile to update friend lists
        await this.fetchProfile();

      } catch (error) {
        console.error('Error sending friend request:', error);
        this.showStatus(error.message || 'Failed to send friend request', {}, 'error');
      }
    },

    async acceptFriendRequest(request) {
    try {
      const userId = request.from_user.id;
      const token = localStorage.getItem('token');
      
      const response = await fetch('/api/user/profile/friend-requests/accept/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ from_user_id: userId })
      });

      if (!response.ok) throw new Error('Failed to accept friend request');

      // Remove request from list
      this.incomingFriendRequests = this.incomingFriendRequests
        .filter(req => req.id !== request.id);
      
      // Update localStorage
      localStorage.setItem('incomingRequests', 
        JSON.stringify(this.incomingFriendRequests));

      // Show success message
      this.showStatus(
        'Friend request from {name} accepted', 
        { name: request.from_user.display_name }, 
        'success'
      );

      // Refresh profile to update friends list
      await this.fetchProfile();
    } catch (error) {
      console.error('Error accepting friend request:', error);
      this.showStatus('Failed to accept friend request', {}, 'error');
    }
  },

    async sendAcceptRequest(userId) {
      const token = localStorage.getItem('token');
      if (!token) {
        throw new Error('No auth token found');
      }
      const response = await fetch('/api/user/profile/friend-requests/accept/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
          'Accept': 'application/json'
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
      const userId = request.from_user.id;
      const token = localStorage.getItem('token');
      
      const response = await fetch('/api/user/profile/friend-requests/decline/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ from_user_id: userId })
      });

      if (!response.ok) throw new Error('Failed to decline friend request');

      // Remove request from list
      this.incomingFriendRequests = this.incomingFriendRequests
        .filter(req => req.id !== request.id);
      
      // Update localStorage
      localStorage.setItem('incomingRequests', 
        JSON.stringify(this.incomingFriendRequests));

      // Show success message
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

    async sendDeclineRequest(userId) {
      const token = localStorage.getItem('token');
      if (!token) {
        throw new Error('No auth token found');
      }
      const response = await fetch('/api/user/profile/friend-requests/decline/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
          'Accept': 'application/json'
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
      const token = localStorage.getItem('token');
      if (!token) {
        throw new Error('No auth token found');
      }
      try {
        const friend = this.profile.friends.find(f => f.id === friendId);
        const response = await fetch('/api/user/profile/remove_friend/', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
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
        const token = localStorage.getItem('token');
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
        
        // Store in localStorage for persistence
        localStorage.setItem('incomingRequests', JSON.stringify(data));
      } catch (error) {
        console.error('Error fetching friend requests:', error);
        this.showStatus('Failed to load friend requests', {}, 'error');
      }
    },

    // Helper method for avatar URL
    handleAvatarError(e) {
      console.warn('Avatar failed to load:', e.target.src);
      e.target.src = this.defaultAvatarUrl;
      this.avatarLoadError = true;
    },

    // Update the buildAvatarUrl method
    buildAvatarUrl(avatarPath) {
      if (!avatarPath || avatarPath.includes('/static/default/')) {
        return this.defaultAvatarUrl;
      }

      if (avatarPath.startsWith('http')) {
        return avatarPath;
      }

      return `https://localhost${avatarPath}`;
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
        // Send offline status via WebSocket
        if (this.notificationSocket && this.notificationSocket.readyState === WebSocket.OPEN) {
          this.notificationSocket.send(JSON.stringify({
            type: 'friend_status',
            status: 'offline'
          }));
          
          await new Promise(resolve => setTimeout(resolve, 100));
          this.notificationSocket.close();
        }

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

    // WebSocket methods
    // initNotificationSocket() {
    //   const token = this.getToken;
    //   const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    //   const wsHost = 'localhost'; // Use direct service URL
    //   const wsUrl = `${wsProtocol}//${wsHost}/ws/profile/notifications/?token=${token}`;
      
    //   this.notificationSocket = new WebSocket(wsUrl);
    //   this.notificationSocket.onopen = () => {
    //     this.wsConnected = true;
    //   };
    //   this.notificationSocket.onmessage = (e) => {
    //     console.log('WebSocket message received:', e.data);  // Debug logging
    //     const data = JSON.parse(e.data);
    //     // Handle incoming messages
    //     switch (data.type) {
    //       case 'friend_request':
    //         this.incomingFriendRequests.push({
    //             id: Date.now(), // Generate temporary ID
    //             from_user: {
    //                 id: data.from_user_id,
    //                 display_name: data.from_user_name,
    //                 avatar: this.buildAvatarUrl(data.from_user_avatar, 'http://localhost'),
    //                 is_online: true // Assume online since they just sent request
    //             }
    //         });
    //         this.showStatus(`New friend request from ${data.from_user_name}`, {}, 'success');
    //         break;

    //         case 'friend_status':
    //           const friendId = data.user_id;
    //           const status = data.status;
    //           // First try to find friend in the profile.friends array
    //           const friend = this.profile.friends.find(f => 
    //               f.user_id === friendId || // Check user_id
    //               f.id === friendId || // Check profile id
    //               (f.user && f.user.id === friendId) // Check nested user object
    //           );
              
    //           if (friend) {
    //               friend.is_online = (status === 'online');
    //               console.log(`Updated status for friend ${friend.display_name} to ${status}`);
    //           } else {
    //               console.log('Friend status update failed:', {
    //                   receivedId: friendId,
    //                   status: status,
    //                   friendsList: this.profile.friends
    //               });
    //           }
    //           break;

    //       case 'friend_request_accepted':
    //         this.fetchProfile();
    //         break;

    //       case 'friend_request_declined':
    //         this.fetchProfile();
    //         break;

    //       case 'friend_removed':
    //         this.fetchProfile(); // Refresh receiver's profile
    //         break;

    //       default:
    //         console.warn('Unhandled WebSocket message type:', data.type);
    //         break;
    //     }
    //   };
    //   this.notificationSocket.onclose = () => {
    //     this.wsConnected = false;
    //   };
    // },

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