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
        <div v-for="request in incomingFriendRequests" :key="request.id" class="request-item">
          <div class="user-info">
            <img 
              :src="request.from_user.avatar" 
              :alt="request.from_user.display_name"
              class="profile-avatar"
            >
            >
            <span class="display-name">{{ request.from_user.display_name }}</span>
          </div>
          <div class="request-actions">
            <button @click="acceptFriendRequest(request)" class="btn accept-btn">Accept</button>
            <button @click="declineFriendRequest(request)" class="btn decline-btn">Decline</button>
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
      
      <div v-else-if="searchResults.length > 0" class="search-results">
        <div v-for="profile in searchResults" :key="profile.id" class="profile-item">
          <div class="user-info">
            <img :src="profile.avatar" :alt="profile.display_name" class="profile-avatar">
            <span class="display-name">{{ profile.display_name }}</span>
          </div>
          <div class="action-buttons">
            <button 
              v-if="!isFriend(profile) && !profile.friend_request_status" 
              @click="sendFriendRequest(profile.id)" 
              class="btn primary-btn"
            >
              Add Friend
            </button>
            <span v-else-if="profile.friend_request_status === 'pending'" class="status-text">
              Request Pending
            </span>
            <button 
              v-else-if="!isBlocked(profile)"
              @click="blockUser(profile.id)" 
              class="btn secondary-btn"
            >
              Block
            </button>
            <button 
              v-else
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
  </div>

  <!-- Debugging -->
  <div>
    <pre>{{ profile }}</pre>
    <pre>{{ incomingFriendRequests }}</pre>
    <pre>{{ searchResults }}</pre>
  </div>
</template>

<script>
import { mapGetters } from 'vuex';
import { SERVICE_URLS } from '@/config/services';

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
      messages: [],
      newMessage: '',
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
      activeTab: 'friends'
    };
  },

  computed: {
    ...mapGetters(['getToken', 'isAuthenticated']),
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

    isFriend(profile) {
      return this.profile?.friends?.some(friend => friend.id === profile.id)
    },

    isBlocked(profile) {
      return profile.isBlocked; // Check the isBlocked flag from API response
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
      } catch (error) {
        console.error('Profile fetch error:', error);
        if (error.message.includes('token_not_valid')) {
          // Token expired or invalid - redirect to login
          this.$router.push('/login');
        }
        throw error;
      }
    },

    async startChat(friend) {
      try {
        this.activeChat = friend.display_name;
        this.showFriendProfile = false;
        this.showChat = true;
        
        const chatId = [this.currentUserId.toString(), friend.id.toString()]
        .sort()
        .join('_');
        
        const response = await fetch(`${SERVICE_URLS.CHAT_SERVICE}/api/chats/${chatId}/`, {
          method: 'GET',
          headers: {
            'Authorization': `Token ${this.getToken}`,
            'Content-Type': 'application/json'
          }
        });
        
        if (!response.ok) {
          const errorData = await response.json();
          console.error('Chat service error:', errorData);
          throw new Error(`Chat service error: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Messages data:', {
          currentUserId: this.currentUserId,
          friendId: friend.id,
          messages: data.messages
        });
        
        this.messages = data.messages.map(msg => ({
          id: msg.id,
          chat: msg.chat,
          sender_id: msg.sender_id,
          text: msg.text,
          created_at: msg.created_at
        }));
        
        this.chatId = chatId;
        // Setup WebSocket connection with token
        if (this.chatSocket) {
          this.chatSocket.close();
        }
        
        const wsScheme = window.location.protocol === 'https:' ? 'wss' : 'ws';
        const wsUrl = `${wsScheme}://${window.location.host}/chat/ws/chat/${this.chatId}/?token=${this.getToken}`;
        this.chatSocket = new WebSocket(wsUrl);
        
        // Handle incoming messages with correct structure
        this.chatSocket.onmessage = (event) => {
          const data = JSON.parse(event.data);
          if (data.type === 'chat.message') {
            const newMessage = {
              id: data.message.id,
              chat: data.message.chat,
              sender_id: data.message.sender_id || data.message.sender,
              text: data.message.text,
              created_at: data.message.created_at || new Date().toISOString()
            };
            
            console.log('Message alignment check:', {
              newMessage,
              senderId: newMessage.sender_id,
              currentUserId: this.currentUserId,
              isOwn: parseInt(newMessage.sender_id) === parseInt(this.currentUserId)
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
        
        this.showChat = false;
        this.activeChat = null;
      }
    },
        
    showFriendInfo(friend) {
      this.selectedFriend = friend;
      this.showFriendProfile = true;
      this.showChat = false;
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

    async removeFriend(friendId, event) {
      try {
        // Prevent event propagation
        event?.stopPropagation();
        
        const friend = this.profile.friends.find(f => f.id === friendId);
        const response = await fetch('/api/user/profile/remove_friend/', {
          method: 'POST',
          headers: {
            'Authorization': `Token ${this.getToken}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ friend_profile_id: friendId }),
        });
          
        if (response.ok) {
          this.showStatus('Friend {name} removed successfully', { name: friend.display_name }, 'success');
          
          // Make sure profile modal is closed
          this.showFriendProfile = false;
          this.selectedFriend = null;
          
          await this.fetchProfile(); // Refresh sender's profile
        } else {
          console.error('Failed to remove friend');
          this.showStatus('Failed to remove friend', {}, 'error');
        }
      } catch (error) {
        console.error('Error removing friend:', error);
        this.showStatus('Error removing friend', {}, 'error');
      }
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
}

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
  background: #a60303;
  color: #ffffff;
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
  padding-left: 10%;
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
</style>