<template>
  <div class="friends-container">
    <div class="friends-nav">
      <button 
        @click="activeTab = 'friends'"
        :class="['tab-btn', { active: activeTab === 'friends' }]"
      >
      {{ t('friends.title') }} ({{ profile.friends?.length || 0 }})
      </button>
      <button 
        @click="activeTab = 'requests'"
        :class="['tab-btn', { active: activeTab === 'requests', 'highlight': incomingFriendRequests.length > 0 }]"
      >
      {{ t('friends.request') }} ({{ incomingFriendRequests.length }})
      </button>
      <button 
        @click="activeTab = 'search'"
        :class="['tab-btn', { active: activeTab === 'search' }]"
      >
      {{ t('friends.find') }}
      </button>
    </div>

    <!-- Friends List Section -->
    <div v-if="activeTab === 'friends'" class="section">
      <div v-if="profile.friends && profile.friends.length > 0">
        <div v-for="friend in profile.friends" :key="friend.id" class="profile-item">
          <div class="avatar-container" @click="showFriendInfo(friend)">
            <img 
              :src="friend.avatar" 
              :alt="friend.display_name" 
              :class="['profile-avatar', friend.is_online ? 'online' : 'offline']"
            >
            <span :class="['status-dot', friend.is_online ? 'online' : 'offline']"></span>
          </div>
          <span class="profile-name">{{ friend.display_name }}</span>
          <div class="friend-actions">
            <button @click="showFriendInfo(friend)" class="btn primary-btn">{{ t('friends.info') }}</button>
            <button @click="removeFriend(friend.id)" class="btn secondary-btn">{{ t('friends.remove') }}</button>
          </div>
        </div>
      </div>
      <p v-else class="no-content">{{ t('friends.noFriends') }}</p>
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
            {{ t('profile.friends.accept') }}
            </button>
            <button 
              @click="declineFriendRequest(request)" 
              class="btn secondary-btn"
            >
            {{ t('profile.friends.decline') }}
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
          :placeholder="t('profile.search.placeholder')" 
          class="search-input"
        />
      </div>

      <div v-if="isSearching" class="loading">
        <span>{{ t('profile.search.searching') }}</span>
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
            {{ t('profile.friends.add') }}
            </button>
            <button 
              v-else-if="isFriend(profile)" 
              @click="removeFriend(profile.id)" 
              class="btn secondary-btn"
            >
            {{ t('profile.friends.remove') }}
            </button>
            <span 
              v-else-if="profile.friend_request_status === 'pending'" 
              class="status-text"
            >
            {{ t('profile.friends.pending') }}
            </span>

            <!-- Block/Unblock button -->
            <button
              v-if="canShowBlockButton(profile)"
              @click="blockUser(profile.id)" 
              class="btn secondary-btn"
            >
            {{ t('profile.friends.block') }}
            </button>
            <button 
              v-else-if="isBlocked(profile)"
              @click="unblockUser(profile.id)" 
              class="btn primary-btn"
            >
            {{ t('profile.friends.unblock') }}
            </button>
          </div>
        </div>
      </div>
      <p v-else-if="searchQuery" class="no-content">{{ t('profile.search.noResults') }}</p>
    </div>
    <div v-if="statusMessage":class="['status-message', statusMessage.type]">
      {{ statusMessage.text }}
    </div>

    <!-- Add this right before the closing </div> of friends-container -->
    <transition name="fade">
      <div v-if="showFriendProfile && selectedFriend" class="overlay">
        <div class="friend-profile-modal">
          <div class="friend-profile-header">
            <h3 class="profile-title">{{ t('friends.profileInfo') }}</h3>
            <button @click="showFriendProfile = false" class="btn secondary-btn">{{ t('friends.close') }}</button>
          </div>

          <div class="profile-details">
            <!-- Avatar section -->
            <div class="detail-group avatar-group">
              <div class="profile-avatar-small">
                <img 
                  :src="selectedFriend.avatar" 
                  :alt="selectedFriend.display_name"
                  :class="['friend-avatar', selectedFriend.is_online ? 'online' : 'offline']"
                >
                <span :class="['status-indicator', selectedFriend.is_online ? 'online' : 'offline']"></span>
              </div>
            </div>

            <div class="detail-group">
              <h5>{{ t('friends.displayName') }}</h5>
              <p>{{ selectedFriend.display_name }}</p>
            </div>

            <div class="detail-group">
              <h5>{{ t('friends.title') }} ({{ selectedFriend.friends_count }})</h5>
              <div class="friends-list">
                <div v-if="selectedFriend.friends && selectedFriend.friends.length > 0">
                  <div v-for="friend in selectedFriend.friends" 
                    :key="friend.id" 
                    class="friend-mini-card"
                    @click="friend.id === currentUserId ? goToMyProfile() : showFriendInfo(friend)">
                    <div class="friend-mini-avatar">
                      <img :src="friend.avatar" :alt="friend.display_name">
                      <span :class="['mini-status-dot', friend.is_online ? 'online' : 'offline']"></span>
                    </div>
                    <span class="friend-mini-name">{{ friend.display_name }}</span>
                  </div>
                </div>
                <p v-else class="no-content">{{ t('friends.noFriends') }}</p>
              </div>
            </div>

            <div class="detail-group">
              <h5>Match History</h5>
              <p>Coming soon...</p>
            </div>
            
          </div>

          <div class="friend-profile-footer">
            <button @click="startChat(selectedFriend)" class="btn primary-btn">{{ t('friends.chat') }}</button>
          </div>
        </div>
      </div>
    </transition>

    <!-- Chat Section -->
    <transition name="fade">
      <div v-if="showChat" class="overlay">
        <div class="chat-container">
          <div class="chat-header">
            <button 
              @click="sendGameInvite" 
              class="btn primary-btn"
              :disabled="!selectedFriend.is_online"
              :class="{ 'btn-disabled': !selectedFriend.is_online }"
            >
              <i class="game-icon"></i>
              {{ selectedFriend.is_online ? 'Invite to Play' : 'Friend Offline' }}
            </button>
            
            <h4 class="chat-title">{{ t('friends.chatWith') }} {{ activeChat }}</h4>
            
            <button @click="closeChat" class="btn secondary-btn">{{ t('friends.close') }}</button>
          </div>
          <div class="chat-messages" ref="chatMessages">
            <div v-for="message in messages" 
              :key="message.id" 
              :class="['message', { 
                'message-sent': parseInt(message.sender_id) === parseInt(currentUserId),
                'message-received': parseInt(message.sender_id) !== parseInt(currentUserId)
              }]">
              <div class="message-content" 
                @contextmenu.prevent="showMessageOptions($event, message)"
                :class="{ 
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
              :placeholder="t('friends.typeMessage')"
              class="chat-input-field"
            />
            <button @click="sendMessage" class="btn primary-btn">{{ t('friends.sendMessage') }}</button>
          </div>
        </div>
      </div>
    </transition>

    <!-- Game Window -->
    <!-- filepath: /home/ipetruni/Desktop/Transcendence/FrontEnd/src/views/Friends.vue -->
    <transition name="fade">
        <div v-if="showGameWindow" class="overlay">
            <PongGame 
                :opponent="opponent || ''"
                :gameId="currentGameId || ''"
                :isHost="gameInviteSent"
                @close="closeGameWindow"
            />
        </div>
    </transition>

    <transition name="slide-down">
      <div v-if="gameInviteNotification" class="game-invite-banner">
          <div class="game-invite-content">
              <span class="game-invite-text">
                  {{ gameInviteNotification.sender }} invited you to play!
              </span>
              <div class="game-invite-actions">
                  <button @click="handleGameAccepted" class="btn primary-btn">Accept</button>
                  <button @click="declineGameInvite" class="btn secondary-btn">Decline</button>
              </div>
          </div>
      </div>
    </transition>
  </div>

  <!-- Debugging
  <div>
    <pre>{{ profile }}</pre>
    <pre>{{ incomingFriendRequests }}</pre>
    <pre>{{ searchResults }}</pre>
  </div> -->
</template>

<script>
import PongGame from './Game.vue';
import { useI18n } from 'vue-i18n';


export default {
  name: 'Friends',

    components: {
      PongGame
    },
    setup() {
    const { t } = useI18n();
    return { t };
  },
  
    data() {
    return {
      // User Profile and Friends
      profile: {
        friends: []  // Array of user's friends
      },
      
      // WebSocket Related
      wsConnected: false,
      chatSocket: null,
      
      // Search Functionality
      searchQuery: '',
      searchResults: [],
      isSearching: false,
      searchError: null,
      searchTimeout: null,
      
      // Friend Requests
      incomingFriendRequests: JSON.parse(localStorage.getItem('incomingRequests') || '[]'),
      
      // Friend Profile Modal
      selectedFriend: {
        id: null,
        display_name: '',
        avatar: '',
        is_online: false,
        friends: [],      // Friend's friends list - for nested friends view
        friends_count: 0  // Total count of friend's friends
      },
      showFriendProfile: false,
      
      // Navigation
      activeTab: 'friends',
      
      // Authentication
      token: localStorage.getItem('token'),
      currentUserId: null,
      
      // UI State
      statusMessage: null,
      
      // Chat Functionality
      messages: [],
      newMessage: '',
      showChat: false,
      activeChat: null,
      chatId: null,

      //Notification
      notificationSocket: null,

      // Game Functionality
      opponent: null,
      showGameWindow: false,
      gameInviteSent: false,
      currentGameId: null,
      gameInviteNotification: null,
      gameInviteTimeout: null,
      gameStarted: false,
      player1Name: '',
      player2Name: ''
    }
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
      
      this.initNotificationSocket();
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
        throw error;
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

        // Send friend request notification through WebSocket Erik
        if (this.notificationSocket && this.notificationSocket.readyState === WebSocket.OPEN) {
          const notificationData = {
            type: 'friend_request',
            recipient_id: friendId,
            sender_name: this.profile.display_name || this.username,
            sender_id: this.currentUserId 
          };

          console.log('Sending friend request notification:', notificationData);
          this.notificationSocket.send(JSON.stringify(notificationData));
        } else {
          console.error('Notification socket not connected');
        }
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

        // Remove from incoming request
        this.incomingFriendRequests = this.incomingFriendRequests.filter(req => req.id !== request.id);
        localStorage.setItem('incomingRequests', JSON.stringify(this.incomingFriendRequests));
      
        // Fetch updated profile to get fresh friends list
        await this.fetchProfile();

        if (this.notificationSocket && this.notificationSocket.readyState === WebSocket.OPEN) {
          const notificationData = {
            type: 'friend_accepted',
            recipient_id: request.from_user.id,
            sender_name: this.profile.display_name || this.username,
            sender_id: this.currentUserId
          };

          console.log('Sending friend request accepted notification:', notificationData);
          this.notificationSocket.send(JSON.stringify(notificationData));
        } else {
          console.error('Notification socket not connected');
        }
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
        if (this.notificationSocket && this.notificationSocket.readyState === WebSocket.OPEN) {
          const notificationData = {
            type: 'friend_declined',
            recipient_id: request.from_user.id,  // Send to the person who originally sent the request
            sender_name: this.profile.display_name || this.username,
            sender_id: this.currentUserId
          };

          console.log('Sending friend decline notification:', notificationData);
          this.notificationSocket.send(JSON.stringify(notificationData));
        } else {
          console.error('Notification socket not connected');
        }
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

          // Update search results to clear any pending status - ADD THIS CODE
          this.searchResults = this.searchResults.map(profile => {
            if (profile.id === friendId) {
              return {
                ...profile,
                friend_request_status: null,  // Clear the pending status
                requested_by_current_user: false,
                is_friend: false // Make sure "is_friend" is set to false
              };
            }
            return profile;
          });

          this.showStatus('Friend {name} removed successfully', { name: friend.display_name }, 'success');
          await this.fetchProfile();
          
          // Send friend removal notification through WebSocket
          if (this.notificationSocket && this.notificationSocket.readyState === WebSocket.OPEN) {
            const notificationData = {
              type: 'friend_removed',
              recipient_id: friendId,
              sender_name: this.profile.display_name || this.username,
              sender_id: this.currentUserId
            };

            console.log('Sending friend removal notification:', notificationData);
            this.notificationSocket.send(JSON.stringify(notificationData));
          } else {
            console.error('Notification socket not connected');
          }
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

    // checks user ID and token
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

    // Handles UI state changes
    updateChatUI(friend) {
      this.activeChat = friend.display_name;
      this.showFriendProfile = false;
      this.showChat = true;
    },

    // creates unique chat identifier
    generateChatId(friendId) {
      const chatId = [this.currentUserId, friendId]
        .sort((a, b) => a - b)
        .join('_');
      console.log('Generated chat ID:', chatId);
      return chatId;
    },

    // retrieves chat messages
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

    // handles API response parsing
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

    // sets up WebSocket connection
    async initializeChatWebSocket(chatId) {
      if (this.chatSocket && this.chatSocket.readyState === WebSocket.OPEN) {
        this.chatSocket.close();
      }

      const wsUrl = this.buildWebSocketUrl(chatId);
      console.log('Connecting WebSocket to:', wsUrl);
      
      this.chatSocket = new WebSocket(wsUrl);
      this.setupWebSocketEventHandlers(chatId);
    },

    // constructs WebSocket URL
    buildWebSocketUrl(chatId) {
      const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsHost = window.location.host;
      return `${wsProtocol}//${wsHost}/ws/chat/${chatId}/?token=${this.getToken}`;
    },

    // configures WebSocket handlers
    setupWebSocketEventHandlers(chatId) {

      this.chatSocket.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            console.log('Received WebSocket message:', data);
            
            if (data.type === 'chat_message') {
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
            else if (data.type === 'game_invite') {
            this.handleGameInvite(data.message);
            }

            
        } catch (error) {
            console.error('Error processing message:', error);
        }
    };
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
        
        if (data.type === 'chat_message') {
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
        else if (data.type === 'game_invite') {
        this.handleGameInvite(data.message);
        }
        else if (data.type === 'game_accepted') {
          this.handleGameAccepted(data.message);
        }
        else if (data.type === 'game_state') {
          this.handleGameState(data.message);
        }
        else if (data.type === 'game_declined') {
          this.handleGameDeclined(data.message);
        }
        else if (data.type === 'tournament_notification') {
          this.handleTournamentNotification(data.message);
        }
      } catch (error) {
        console.error('Error processing message:', error);
      }
    },

    // manages error states
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

    goToMyProfile() {
      this.$router.push('/profile'); // Adjust the route path as needed
      this.showFriendProfile = false; // Close the friend profile modal
    },
        
    async showFriendInfo(friend) {
      try {
        const response = await fetch(`/api/user/profile/${friend.id}/`, {
          headers: {
            'Authorization': `Bearer ${this.getToken}`,
            'Content-Type': 'application/json'
          }
        });

        if (!response.ok) {
          throw new Error('Failed to fetch friend profile');
        }

        const friendData = await response.json();
        this.selectedFriend = {
          id: friendData.id,
          display_name: friendData.display_name,
          avatar: friendData.avatar,
          is_online: friendData.is_online,
          friends: friendData.friends || [],
          friends_count: friendData.friends_count || 0
        };
        this.showFriendProfile = true;
        this.showChat = false;  // Close chat if open

      } catch (error) {
        console.error('Error fetching friend details:', error);
        this.showStatus('Failed to load friend profile', {}, 'error');
      }
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

        const notificationMessageData = {
          type: 'chat_message',
          message: {
            text: this.newMessage,
            sender_id: this.currentUserId,
            recipient_id: this.selectedFriend.id,
            sender_name: this.profile.display_name || 'User'
          }
        };

        console.log('Sending notification:', notificationMessageData);

        console.log('Sending message data:', {
          messageContent: messageData,
          socketState: this.chatSocket.readyState,
          currentUserId: this.currentUserId,
          chatId: this.chatId,
          timestamp: new Date().toISOString()
        });

        this.chatSocket.send(JSON.stringify(messageData));
        this.notificationSocket.send(JSON.stringify(notificationMessageData));
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

    handleGameInvite(data) {
        console.log('Handling game invite:', data);
        
        // Clear any existing timeout
        if (this.gameInviteTimeout) {
            clearTimeout(this.gameInviteTimeout);
        }

        // Only show invitation if we're the recipient
        if (parseInt(data.recipient_id) === parseInt(this.currentUserId)) {
            // Set notification data with complete information
            this.gameInviteNotification = {
                sender: data.sender_name,
                recipient: data.recipient_name,
                gameId: data.game_id,
                senderId: data.sender_id,
                recipientId: this.currentUserId,
                player1Name: data.player1_username,
                player2Name: data.player2_username
            };

            // Store player names
            this.player1Name = data.player1_username;
            this.player2Name = data.player2_username;

            // Show status message
            this.showStatus(`${data.sender_name} invited you to play!`, {}, 'info');

            // Auto-hide notification after 10 seconds
            this.gameInviteTimeout = setTimeout(() => {
                this.declineGameInvite();
            }, 10000);
        }
    },

    handleGameAccepted(data) {
        console.log('Game acceptance received:', data);
        
        try {
            // If we're handling a click event (recipient accepting)
            if (!data || data instanceof Event) {
                if (!this.gameInviteNotification) {
                    console.error('No game invite notification found');
                    return;
                }

                // Set game data for recipient
                this.currentGameId = this.gameInviteNotification.gameId;
                this.opponent = this.gameInviteNotification.sender;
                
                // Send accept message through notification WebSocket
                if (this.notificationSocket && this.notificationSocket.readyState === WebSocket.OPEN) {
                    const acceptData = {
                        type: 'game_accepted',
                        game_id: this.currentGameId,
                        sender_id: this.gameInviteNotification.senderId,
                        recipient_id: this.currentUserId,
                        recipient_name: this.profile.display_name,
                        sender_name: this.gameInviteNotification.sender
                    };
                    
                    console.log('Sending game acceptance:', acceptData);
                    this.notificationSocket.send(JSON.stringify(acceptData));
                }
            } 
            // If we're handling a WebSocket message (sender receiving acceptance)
            else {
                // Set game data for sender
                this.currentGameId = data.game_id;
                this.opponent = data.recipient_name;
                this.showStatus(`${data.recipient_name} accepted your game invite!`, {}, 'success');
            }

            // Common actions for both sender and recipient
            this.showGameWindow = true;
            this.showChat = false;
            this.gameInviteSent = !data; // true for recipient, false for sender
            
            // Clear any existing notifications
            if (this.gameInviteNotification) {
                this.gameInviteNotification = null;
            }

            // Initialize game connection
            this.initializeGameConnection(this.currentGameId);

        } catch (error) {
            console.error('Error handling game acceptance:', error);
            this.showStatus('Failed to process game acceptance', {}, 'error');
        }
    },

    initializeGameConnection(gameId) {
        const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsHost = window.location.host;
        const wsUrl = `${wsProtocol}//${wsHost}/ws/game/${gameId}/?token=${this.getToken}`;
        
        // Close existing game socket if any
        if (this.gameSocket && this.gameSocket.readyState === WebSocket.OPEN) {
            this.gameSocket.close();
        }

        // Create new game socket
        this.gameSocket = new WebSocket(wsUrl);
        
        this.gameSocket.onopen = () => {
            console.log('Game WebSocket connected');
        };

        this.gameSocket.onerror = (error) => {
            console.error('Game WebSocket error:', error);
            this.showStatus('Error connecting to game server', {}, 'error');
        };

        this.gameSocket.onclose = () => {
            console.log('Game WebSocket closed');
        };
    },

    declineGameInvite() {
      if (!this.gameInviteNotification) return;

      // Clear the timeout
      if (this.gameInviteTimeout) {
        clearTimeout(this.gameInviteTimeout);
      }

      // Send decline message through WebSocket
      if (this.chatSocket && this.chatSocket.readyState === WebSocket.OPEN) {
        const declineData = {
          type: 'game_decline',
          game_id: this.gameInviteNotification.gameId,
          recipient_id: this.selectedFriend.id
        };
        
        console.log('Sending game decline:', declineData);
        this.chatSocket.send(JSON.stringify(declineData));
      }

      // Clear the notification
      this.gameInviteNotification = null;
    },
    
    initNotificationSocket() {
        try {
            const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsHost = window.location.host;
            const token = this.getToken;

            if (!token) {
                console.error('No token available for notification socket');
                return;
            }

            const wsUrl = `${wsProtocol}//${wsHost}/ws/notifications/?token=${encodeURIComponent(token)}`;
            console.log('Connecting to notification socket:', wsUrl);
            this.notificationSocket = new WebSocket(wsUrl);
            this.notificationSocket.onopen = () => {
                this.wsConnected = true;
            };

            // Update the message handler to use proper async/await
            this.notificationSocket.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    console.log('Received notification data:', data);

                    // Handle different notification types synchronously
                    switch (data.type) {
                        case 'game_invite':
                            this.handleGameInvite(data);
                            break;
                        case 'game_accepted':
                            this.handleGameAccepted(data);
                            break;
                        case 'game_declined':
                            this.handleGameDecline(data);
                            break;
                        case 'chat_message':
                            this.handleChatNotification(data);
                            break;
                        case 'friend_request':
                            this.handleFriendRequestNotification(data);
                            break;
                        case 'friend_accepted':
                            this.handleFriendAcceptNotification(data);
                            break;
                        case 'friend_declined':
                            this.handleFriendDeclineNotification(data);
                            break;
                        case 'friend_removed':
                          this.handleFriendRemoveNotification(data);
                          break;
                        default:
                            console.log('Unknown notification type:', data.type);
                    }
                } catch (error) {
                  console.error('Error processing notification:', error);
                }
            };

            this.notificationSocket.onerror = (error) => {
                console.error('Notification WebSocket error:', error);
                this.wsConnected = false;
                setTimeout(() => this.initNotificationSocket(), 3000);
            };

            this.notificationSocket.onclose = () => {
                console.log('Notification WebSocket closed');
                this.wsConnected = false;
                // Only attempt to reconnect if the component is still mounted
                if (!this._isDestroyed) {
                    setTimeout(() => this.initNotificationSocket(), 3000);
                }
            };

        } catch (error) {
            console.error('Error initializing notification socket:', error);
            setTimeout(() => this.initNotificationSocket(), 3000);
        }
    },

    

    // handleGameDecline(data) {
    //     if (parseInt(data.sender_id) === parseInt(this.currentUserId)) {
    //         this.showStatus('Game invite declined', {}, 'warning');
    //         this.gameInviteSent = false;
    //         this.showGameWindow = false;
    //     }
    // },

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

    // Game Invite Methods
    async sendGameInvite() {
        try {
            const uuid = crypto.randomUUID();
            this.currentGameId = uuid;
            this.opponent = this.selectedFriend.display_name; // Set the opponent name
            
            if (this.notificationSocket && this.notificationSocket.readyState === WebSocket.OPEN) {
                const inviteData = {
                    type: 'game_invite',
                    game_id: uuid,
                    sender_id: this.currentUserId,
                    recipient_id: this.selectedFriend.id,
                    sender_name: this.profile.display_name,
                    recipient_name: this.selectedFriend.display_name
                };
                
                console.log('Sending game invite:', inviteData);
                this.notificationSocket.send(JSON.stringify(inviteData));
                this.gameInviteSent = true;
                this.showGameWindow = true;
                this.showChat = false;
            } else {
                throw new Error('Notification socket not connected');
            }
        } catch (error) {
            console.error('Error sending game invite:', error);
            this.showStatus('Failed to send game invite', {}, 'error');
        }
    },

    // Add method to handle game join
    handleGameJoin(gameId) {
      this.currentGameId = gameId;
      this.showGameWindow = true;
      this.gameInviteSent = false; // Since we're joining, not hosting
    },

    handleFriendRequestNotification(data) {
        try {
            console.log('Handling friend request notification:', data);
            
            // Only update the UI if we're the recipient, not the sender
            if (parseInt(data.recipient_id) === parseInt(this.currentUserId)) {
                this.fetchIncomingRequests().then(() => {
                    this.showStatus('New friend request received from {name}', { name: data.sender_name }, 'info');
                }).catch(error => {
                    console.error('Error fetching friend requests after notification:', error);
                });
            } else {
                console.log('Ignoring friend request notification not meant for us');
            }
        } catch (error) {
            console.error('Error processing friend request notification:', error);
        }
    },

    handleFriendAcceptNotification(data) {
      try {
        console.log('Handling friend acceptance notification:', data);
        // some check
        if (parseInt(data.recipient_id) === parseInt(this.currentUserId)) {
          // Refresh the friends list to show the new friend
          this.fetchProfile().then(() => {
            this.showStatus(`${data.sender_name} accepted your friend request`, {}, 'success');
          }).catch(error => {
            console.error('Error fetching profile after friend acceptance:', error);
          });
        } else {
          console.log('Ignoring friend acceptance notification not meant for us');
        }
      } catch (error) {
        console.error('Error processing friend acceptance notification:', error);
      }
    },

    handleFriendDeclineNotification(data) {
      try {
        console.log('Handling friend decline notification:', data);
        
        if (parseInt(data.recipient_id) === parseInt(this.currentUserId)) {
          // Find the declined user in search results and update their status
          this.searchResults = this.searchResults.map(profile => {
            if (profile.id === parseInt(data.sender_id)) {
              return {
                ...profile,
                friend_request_status: null,  // Clear the pending status
                requested_by_current_user: false
              };
            }
            return profile;
          });
          
          // Refresh the profile data
          this.fetchProfile().then(() => {
            this.showStatus(`${data.sender_name} declined your friend request`, {}, 'info');
          }).catch(error => {
            console.error('Error fetching profile after friend decline:', error);
          });
        } else {
          console.log('Ignoring friend decline notification not meant for us');
        }
      } catch (error) {
        console.error('Error processing friend decline notification:', error);
      }
    },

    // Add this method to handle friend removal notifications
    handleFriendRemoveNotification(data) {
      try {
        console.log('Handling friend removal notification:', data);
        
        if (parseInt(data.recipient_id) === parseInt(this.currentUserId)) {
          // Update search results to clear any pending status
          this.searchResults = this.searchResults.map(profile => {
            if (profile.id === parseInt(data.sender_id)) {
              return {
                ...profile,
                friend_request_status: null,  // Clear the pending status
                requested_by_current_user: false,
                is_friend: false // Make sure "is_friend" is set to false
              };
            }
            return profile;
          });
          
          // Refresh the profile to update the friends list
          this.fetchProfile().then(() => {
            this.showStatus(`${data.sender_name} has removed you from their friends list`, {}, 'info');
          }).catch(error => {
            console.error('Error fetching profile after friend removal:', error);
          });
        } else {
          console.log('Ignoring friend removal notification not meant for us');
        }
      } catch (error) {
        console.error('Error processing friend removal notification:', error);
      }
    },

    // In Friends.vue
    handleChatNotification(data) {
      try {
        // Add defensive checks for data structure
        if (!data || typeof data !== 'object') {
          console.error('Invalid notification data received:', data);
          return;
        }

        const senderId = data.sender_id?.toString();
        const senderName = data.sender_name || 'Someone';
        const currentChatId = this.chatId;

        // Log the received data for debugging
        console.log('Received chat notification:', {
          senderId,
          senderName,
          currentChatId,
          fullData: data
        });
        
        if (!currentChatId || !currentChatId.includes(senderId)) {
          this.showStatus(
            `New message from ${senderName}`, 
            {}, 
            'info'
          );
        }
      } catch (error) {
        console.error('Error processing chat notification:', error);
      }
    },

    closeGameWindow() {
        this.showGameWindow = false;
        this.gameInviteSent = false;
        this.opponent = null; // Reset the opponent
        
        // Optionally reopen chat
        this.showChat = true;
    },

    handleGameInvite(data) {
        console.log('Handling game invite:', data);
        
        if (this.gameInviteTimeout) {
            clearTimeout(this.gameInviteTimeout);
        }

        if (parseInt(data.recipient_id) === parseInt(this.currentUserId)) {
            this.gameInviteNotification = {
                sender: data.sender_name,
                recipient: data.recipient_name,
                gameId: data.game_id,
                senderId: data.sender_id
            };

            this.showStatus(`${data.sender_name} invited you to play!`, {}, 'info');
            
            this.gameInviteTimeout = setTimeout(() => {
                this.declineGameInvite();
            }, 10000);
        }
    },


    // handleTournamentNotification(notification) {
    //   this.showStatus(
    //     'Tournament game starting soon!', 
    //     {}, 
    //     'warning'
    //   );
    //   // Optional: Add sound notification
    //   this.playNotificationSound();
    // },
  },

  messages: {
    handler() {
      this.scrollToBottom();
    },
    deep: true
  },

  beforeDestroy() {
    this._isDestroyed = true;
    if (this.notificationSocket) {
        this.notificationSocket.close();
    }
    if (this.gameSocket) {
        this.gameSocket.close();
    }
    if (this.chatSocket) {
        this.chatSocket.close();
    }
  },

};
</script>

<style scoped>
/* Layout & Container Styles */
.friends-container {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
}

/* Navigation Styles */
.friends-nav {
  width: 100%;
  display: flex;
  justify-content: center;
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

/* Section Styles */
.section {
  width: 100%;
  background: #1a1a1a;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  box-sizing: border-box;
}

/* Search Styles */
.search-box {
  width: 100%;
  max-width: 600px;
  margin: 0 auto 20px auto;
}

.search-input {
  width: 100%;
  padding: 10px;
  border: 1px solid #404040;
  border-radius: 4px;
  background: #2d2d2d;
  color: white;
}

.search-results {
  width: 100%;
}

/* Profile & User Info Styles */
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

.profile-name {
  font-size: 16px;
  flex-grow: 1;
  color: #ffffff;
  margin-right: 20px;
  margin-left: 10px;
}

.display-name {
  color: #ffffff;
  font-size: 16px;
}

/* Button Styles */
.btn {
  padding: 8px 16px;
  border-radius: 4px;
  border: none;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  min-width: 100px; /* Add fixed minimum width */
  height: 36px; /* Add fixed height */
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  white-space: nowrap; /* Prevent text wrapping */
}
.friend-actions {
  display:grid;
  gap: 10px;
}


.primary-btn {
  background: #03a670;
  color: white;
}

.primary-btn:hover {
  background: #04d38e;
  transform: scale(1.05);
  box-shadow: 0 0 15px rgba(3, 166, 112, 0.3);
}

.secondary-btn {
  background: #a60303;
  color: white;

}

.secondary-btn:hover {
  background: #d30404;
  transform: scale(1.05);
  box-shadow: 0 0 15px rgba(166, 3, 3, 0.3);
}

.action-buttons {
  display: flex;
  align-items: center;
  gap: 10px;
}

.avatar-container {
  position: relative;
  width: 50px;
  height: 50px;
}

/* Status Indicators */
.status-dot {
  position: absolute;
  bottom: 2px;
  right: 2px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 2px solid #1a1a1a;
}

.status-dot.online,
.status-indicator.online {
  background-color: #03a670;
}

.status-dot.offline,
.status-indicator.offline {
  background-color: #a60303;
}

/* Chat Container Styles */
.chat-container {
  height: 75vh;
  width: 75%;
  display: grid;
  grid-template-rows: auto 1fr auto;
  border-radius: 10px;
  box-shadow: 2px 2px 30px #03a670;
  margin: 20px auto;
  max-width: 1200px;
  min-width: 400px;
}

.chat-header {
  padding: 1rem;
  background: #2d2d2d;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #ffffff;
  border-radius: 10px 10px 0 0;
  gap: 1rem;
}

.btn-disabled {
  background-color: #666666;
  cursor: not-allowed;
  opacity: 0.7;
  transform: none !important;
  box-shadow: none !important;
}

.btn-disabled:hover {
  background-color: #666666;
  transform: none;
  box-shadow: none;
}

.chat-input {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  background: #2d2d2d;
  border-radius: 0 0 10px 10px;
}

.chat-input-field {
  flex: 1;
  padding: 0.5rem;
  border: 1px solid #404040;
  border-radius: 4px;
  background: #1a1a1a;
  color: #ffffff;
}

.chat-messages {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1.5rem;
  overflow-y: auto;
  background: #1a1a1a;
  scroll-behavior: smooth;
}

.message {
  display: flex;
  width: 100%;
  margin-bottom: 1rem;
}

.message-sent {
  justify-content: flex-end;
}

.message-received {
  justify-content: flex-start;
}

.message-content {
  max-width: 65%; /* Reduced from 70% for better readability */
  min-width: 60px;
  padding: 1rem;
  position: relative;
  word-wrap: break-word; /* Ensures long words break */
  overflow-wrap: break-word; /* Modern browsers */
  hyphens: auto; /* Adds hyphens when breaking words */
}

.content-sent {
  background: #03a670;
  color: #ffffff;
  border-radius: 1rem 1rem 0 1rem;
  margin-left: auto;
}

.content-received {
  background: #333333;
  color: #ffffff;
  border-radius: 1rem 1rem 1rem 0;
  margin-right: auto;
}

/* Message Header and Footer */
.message-header {
  margin-bottom: 0.5rem;
}

.message-sender {
  font-size: 0.8rem;
  opacity: 0.8;
  cursor: pointer;
}

.message-text {
  display: block;
  line-height: 1.4; /* Improved readability for long messages */
  white-space: pre-wrap; /* Preserves whitespace and wraps */
}

.message-footer {
  margin-top: 0.5rem;
  text-align: right;
}

.message-time {
  font-size: 0.7rem;
  opacity: 0.7;
}

/* Add media queries for responsive design */
@media (max-width: 768px) {
  .message-content {
  max-width: 85%; /* Wider messages on smaller screens */
  }

  .chat-container {
  width: 90%; /* Wider container on smaller screens */
  min-width: 300px;
  }
}

/* Friend Profile Modal Styles */
.friend-profile-modal {
  width: 75%;
  height: 75vh;
  max-width: 1000px;
  min-width: 400px;
  background: #1a1a1a;
  border-radius: 10px;
  box-shadow: 2px 2px 30px #03a670;
  z-index: 1001;
  display: flex;
  flex-direction: column;
  margin: 20px auto;
}

.friend-profile-header {
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 1.5rem;
  background: #2d2d2d;
  border-radius: 10px 10px 0 0;
  position: relative;
}

.profile-title {
  color: #ffffff;
  text-align: center;
  font-size: 1.0rem;
  margin: 0;
}

/* Position close button absolutely */
.friend-profile-header .secondary-btn {
  position: absolute;
  right: 1.5rem;
}

.profile-details {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2rem;
  padding: 2rem;
  overflow-y: auto;
}

.detail-group {
  width: 100%;
  text-align: center;
}

.avatar-group {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 1rem 0;
}

.profile-avatar-large {
  position: relative;
  width: 50px;
  height: 50px;
  margin: 0 auto;
}

.friend-avatar {
  width: 150px; /* Changed from 50% to fixed size */
  height: 150px; /* Changed from 50% to fixed size */
  object-fit: cover;
  border-radius: 50%;
  border: 4px solid transparent;
  transition: border-color 0.3s ease;
}

/* Status Styles for both types of avatars */
.friend-avatar.online,
.profile-avatar.online {
  border-color: #03a670;
  box-shadow: 0 0 15px rgba(3, 166, 112, 0.3);
}

.friend-avatar.offline,
.profile-avatar.offline {
  border-color: #a60303;
  box-shadow: 0 0 15px rgba(166, 3, 3, 0.3);
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

.friend-profile-footer {
  width: 100%;
  display: flex;
  justify-content: center;
  padding: 1.5rem;
  background: #2d2d2d;
  border-radius: 0 0 10px 10px;
}

.friend-profile-footer .btn {
  min-width: 120px;
}

/* Add hover effects */
.friend-profile-footer .primary-btn:hover {
  transform: scale(1.05);
  box-shadow: 0 0 15px rgba(3, 166, 112, 0.5);
}


/* Overlay & Modal Styles */
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
  padding: 2rem;
}

/* Animation Styles */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Utility Classes */
.no-content {
  text-align: center;
  color: #666;
  padding: 20px;
}

.status-text {
  color: #666;
  font-style: italic;
  padding: 8px 16px;
}

/* Status Message Styles */
.status-message {
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 12px 24px;
  border-radius: 4px;
  z-index: 1000;
  animation: fadeIn 0.3s ease;
}

.status-message.success { background-color: #4caf50; color: white; }
.status-message.warning { background-color: #ff9800; color: white; }
.status-message.error { background-color: #f44336; color: white; }


/* Friend List Styles */
.friends-list {
  display: list-item;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  padding: 2%;
  max-height: 200px;
  overflow-y: auto;
  border-radius: 8px;
  margin-top: 1rem;
}

.friend-mini-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0.5rem;
  background: #3b3939;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  margin: 0.5rem;
  box-shadow: 0 2px 8px rgba(3, 166, 112, 0.1);
}

.friend-mini-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(3, 166, 112, 0.2);
}

.friend-mini-avatar {
  position: relative;
  width: 40px;
  height: 40px;
  margin-bottom: 0.5rem;
}

.friend-mini-avatar img {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
}

.mini-status-dot {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  border: 2px solid #1a1a1a;
}

.mini-status-dot.online {
  background-color: #03a670;
  box-shadow: 0 0 8px rgba(3, 166, 112, 0.5);
}

.mini-status-dot.offline {
  background-color: #a60303;
  box-shadow: 0 0 8px rgba(166, 3, 3, 0.5);
}

.friend-mini-name {
  font-size: 0.8rem;
  color: #ffffff;
  text-align: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100px;
}

/* Game Window Styles */
.game-container {
  height: 75vh;
  width: 75%;
  display: grid;
  grid-template-rows: auto 1fr;
  border-radius: 10px;
  box-shadow: 2px 2px 30px #03a670;
  margin: 20px auto;
  max-width: 1200px;
  min-width: 400px;
  background: #1a1a1a;
}

.game-header {
  padding: 1rem;
  background: #2d2d2d;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #ffffff;
  border-radius: 10px 10px 0 0;
}

.game-title {
  margin: 0;
  font-size: 1.2rem;
  color: #ffffff;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Game Invite */
.game-invite-banner {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  background: rgba(3, 166, 112, 0.95);
  color: white;
  padding: 1rem;
  z-index: 2000;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
}

.game-invite-content {
  max-width: 600px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.game-invite-text {
  font-size: 1.1rem;
  font-weight: 500;
}

.game-invite-actions {
  display: flex;
  gap: 0.5rem;
}

/* Animation for the banner */
.slide-down-enter-active,
.slide-down-leave-active {
  transition: transform 0.3s ease, opacity 0.3s ease;
}

.slide-down-enter-from,
.slide-down-leave-to {
  transform: translateY(-100%);
  opacity: 0;
}

.slide-down-enter-to,
.slide-down-leave-from {
  transform: translateY(0);
  opacity: 1;
}

.tab-btn.highlight {
  background: #ff9800; /* Highlight color */
  color: white;
  box-shadow: 0 0 10px rgba(255, 152, 0, 0.5);
  animation: pulse 1s infinite;
}

@keyframes pulse {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
  100% {
    transform: scale(1);
  }
}
</style>