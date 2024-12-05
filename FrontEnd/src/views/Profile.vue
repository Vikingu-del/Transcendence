<template>
  <div class="profile-container">
    <!-- Profile Section -->
    <div class="profile-card">
      <h2>Profile</h2>
      <div class="profile-section">
        <img :src="avatarUrl" alt="User Avatar" class="profile-picture" />
        <form @submit.prevent="updateProfile" class="profile-form">
          <input
            v-model="displayName"
            :placeholder="displayNamePlaceholder"
            class="input-field"
            required
          />
          <input type="file" @change="onFileChange" class="file-input" />
          <button type="submit" class="btn primary-btn">Update Profile</button>
        </form>
      </div>
      <button @click="logout" class="btn secondary-btn">Logout</button>
    </div>   

    <!-- Search Profiles Section -->
    <div>
      <input v-model="searchQuery" @input="searchProfiles" placeholder="Search profiles..." />
      <div v-if="searchResults === null">
        <p>No users found.</p>
      </div>
      <div v-else>
        <div v-for="profile in searchResults" :key="profile.id">
          <p>{{ profile.display_name }}</p>
          <div v-if="profile.friend_request_status === 'pending'">
            <div v-if="profile.requested_by_current_user">
              <p>Request Pending</p>
            </div>
            <div v-else>
              <button @click="acceptFriendRequest(profile.id)">Accept Friend Request</button>
              <button @click="declineFriendRequest(profile.id)">Decline Friend Request</button>
            </div>
          </div>
          <div v-else-if="profile.is_friend">
            <button @click="removeFriend(profile.id)">Remove Friend</button>
          </div>
          <div v-else>
            <button @click="sendFriendRequest(profile.id)">Send Friend Request</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Incoming Friend Requests Section -->
    <div class="profile-card" v-if="incomingFriendRequests && incomingFriendRequests.length > 0">
      <h2>Incoming Friend Requests</h2>
      <ul class="search-results">
        <li v-for="request in incomingFriendRequests" :key="request.from_user_id" class="profile-item">
          <img :src="request.avatar" alt="Avatar" class="profile-avatar" />
          <span class="profile-name">{{ request.from_user_name }}</span>
          <button @click="acceptFriendRequest(request.from_user_id)" class="btn primary-btn">Accept</button>
          <button @click="declineFriendRequest(request.from_user_id)" class="btn secondary-btn">Decline</button>
        </li>
      </ul>
    </div>

    <!-- Friends List Section -->
    <div class="profile-card">
      <h2>Friends</h2>
      <ul class="search-results">
        <li v-for="friend in friends" :key="friend.id" class="profile-item">
          <img :src="friend.avatar" alt="Avatar" class="profile-avatar" />
          <span class="profile-name">{{ friend.display_name }}</span>
          <span class="status" :class="{ online: friend.is_online, offline: !friend.is_online }">
            {{ friend.is_online ? 'Online' : 'Offline' }}
          </span>
          <button @click="removeFriend(friend.id)" class="btn secondary-btn">Remove Friend</button>
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
import { mapActions } from 'vuex';

export default {
  data() {
    return {
      displayName: '',
      avatarUrl: '',
      avatarFile: null,
      friends: [],
      searchQuery: '',
      searchResults: [],
      incomingFriendRequests: [], // Initialize as an empty array
      currentUserId: null,
      notifications: [],
      socket: null, // WebSocket connection
    };
  },
  async created() {
    await this.fetchProfile();
    await this.fetchIncomingFriendRequests();
    this.connectWebSocket();
  },
  methods: {
    ...mapActions(['logoutAction']),

    // Fetch the user's profile
    async fetchProfile() {
      try {
        const response = await fetch('/api/profile/', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
          },
        });
        if (response.ok) {
          const data = await response.json();
          this.displayName = data.display_name;
          this.avatarUrl = data.avatar;
          this.friends = data.friends;
          this.currentUserId = data.id;
        } else {
          const errorText = await response.text();
          console.error('Fetch failed:', errorText);
          alert('Failed to fetch profile');
        }
      } catch (error) {
        console.error('Error fetching profile:', error);
        alert('Error fetching profile');
      }
    },

    // Fetch incoming friend requests
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

    // Connect to the WebSocket for real-time updates
    connectWebSocket() {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      this.socket = new WebSocket(`${protocol}//${window.location.host}/ws/profile/notifications/`);
      this.socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        this.notifications.push(data);

        if (data.type === 'friend_request') {
          // Add the new friend request to the list
          this.incomingFriendRequests.push({
            from_user_id: data.from_user_id,
            from_user_name: data.from_user_name,
            avatar: data.from_user_avatar,
          });
        } else if (data.type === 'friend_status') {
          // Update friend's online status
          const friendId = data.user_id;
          const status = data.status;
          const friend = this.friends.find(f => f.id === friendId);
          if (friend) {
            friend.is_online = (status === 'online');
          }
        } else if (data.type === 'friend_request_accepted') {
          // Update the friends list
          this.fetchProfile();
        } else if (data.type === 'friend_request_declined') {
          // Handle friend request declined
          alert(`Your friend request to ${data.user_name} was declined.`);
        } else if (data.type === 'friend_removed') {
          // Handle friend removed
          this.friends = this.friends.filter(friend => friend.id !== data.user_id);
        }
      };
      this.socket.onclose = () => {
        console.log('WebSocket connection closed');
      };
    },

    // Search for profiles
    async searchProfiles() {
      if (this.searchQuery.trim() === '') {
        this.searchResults = [];
        return;
      }
      try {
        const response = await fetch(`/api/profile/search_profiles/?q=${this.searchQuery}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('authToken')}`
          }
        });
        if (response.ok) {
          const data = await response.json();
          this.searchResults = data.filter(profile => profile.id !== this.currentUserId);
        } else {
          const errorText = await response.text();
          console.error('Fetch failed:', errorText);
        }
      } catch (error) {
        console.error('Error searching profiles:', error);
      }
    },

    // Send a friend request
    async sendFriendRequest(friendId) {
      try {
        const response = await fetch('/api/profile/add_friend/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': this.getCookie('csrftoken'),
            'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
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

    // Accept a friend request
    async acceptFriendRequest(fromUserId) {
      try {
        const response = await fetch('/api/profile/accept_friend_request/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': this.getCookie('csrftoken'),
            'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
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

    // Decline a friend request
    async declineFriendRequest(fromUserId) {
      try {
        const response = await fetch('/api/profile/decline_friend_request/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': this.getCookie('csrftoken'),
            'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
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

    // Remove a friend
    async removeFriend(friendId) {
      try {
        const response = await fetch('/api/profile/remove_friend/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': this.getCookie('csrftoken'),
            'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
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

    // Logout
    async logout() {
      try {
        // Notify friends that the user is offline
        this.socket.send(JSON.stringify({
          type: 'friend_status',
          user_id: this.currentUserId,
          status: 'offline',
        }));

        // Wait a moment to ensure the message is sent
        await new Promise(resolve => setTimeout(resolve, 100));

        // Perform logout action
        const csrfToken = this.getCookie('csrftoken');
        if (csrfToken) {
          await this.logoutAction({ csrftoken: csrfToken });
          localStorage.removeItem('authToken'); // Clear the token on logout
        } else {
          alert('CSRF token missing. Please refresh and try again.');
        }
      } catch (error) {
        alert('Logout failed. Please try again.');
      }
    },
    getCookie(name) {
      let cookieValue = null;
      if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; cookies.length > i; i++) {
          const cookie = cookies[i].trim();
          if (cookie.substring(0, name.length + 1) === name + '=') {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            break;
          }
        }
      }
      return cookieValue;
    },
    onFileChange(event) {
      this.avatarFile = event.target.files[0];
      if (this.avatarFile) {
        this.avatarUrl = URL.createObjectURL(this.avatarFile);
      }
    },

    // Update the user's profile
    async updateProfile() {
      const formData = new FormData();
      formData.append('display_name', this.displayName);
      if (this.avatarFile) {
        formData.append('avatar', this.avatarFile);
      }

      try {
        const response = await fetch('/api/profile/', {
          method: 'PUT',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
          },
          body: formData,
        });
        if (response.ok) {
          await this.fetchProfile();
          alert('Profile updated successfully');
        } else {
          alert('Failed to update profile');
        }
      } catch (error) {
        console.error('Error updating profile:', error);
      }
    },
  },
  computed: {
    displayNamePlaceholder() {
      return this.displayName ? this.displayName : 'Display Name';
    },
    filteredFriends() {
      return this.searchResults.length > 0 ? this.searchResults : this.friends;
    },
  },
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

.profile-picture {
  width: 150px;
  height: 150px;
  border-radius: 50%;
  border: 2px solid #4caf50;
  margin-bottom: 10px;
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
</style>