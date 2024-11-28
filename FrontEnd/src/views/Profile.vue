<template>
  <div class="profile-container">
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
    <div class="profile-card">
      <h2>Incoming Friend Requests</h2>
      <ul class="search-results">
        <li v-for="request in incomingFriendRequests" :key="request.id" class="profile-item">
          <img :src="request.avatar" alt="Avatar" class="profile-avatar" />
          <span class="profile-name">{{ request.display_name }}</span>
          <button @click="acceptFriendRequest(request.id)">Accept</button>
          <button @click="declineFriendRequest(request.id)">Decline</button>
        </li>
      </ul>
    </div>
    <div class="profile-card">
      <h2>Friends</h2>
      <ul class="search-results">
        <li v-for="friend in friends" :key="friend.id" class="profile-item">
          <img :src="friend.avatar" alt="Avatar" class="profile-avatar" />
          <span class="profile-name">{{ friend.display_name }}</span>
          <button @click="removeFriend(friend.id)">Remove Friend</button>
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
      incomingFriendRequests: [],
      currentUserId: null,
      notifications: [],
    };
  },
  async created() {
    await this.fetchProfile();
    await this.fetchIncomingFriendRequests();
    this.connectWebSocket();
  },
  methods: {
    ...mapActions(['logoutAction']),
    async fetchProfile() {
      try {
        const csrfToken = this.getCookie('csrftoken');
        const response = await fetch('/profile/', {
          headers: {
            'X-CSRFToken': csrfToken,
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
    async fetchIncomingFriendRequests() {
      try {
        const response = await fetch('/profile/incoming_friend_requests/', {
          headers: {
            'X-CSRFToken': this.getCookie('csrftoken'),
          },
        });
        if (response.ok) {
          const data = await response.json();
          this.incomingFriendRequests = data;
        } else {
          console.error('Failed to fetch incoming friend requests');
        }
      } catch (error) {
        console.error('Error fetching incoming friend requests:', error);
      }
    },
    connectWebSocket() {
      const socket = new WebSocket(`ws://${window.location.host}/ws/notifications/`);
      socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        this.notifications.push(data);
        if (data.type === 'friend_request') {
          this.fetchIncomingFriendRequests();
        } else if (data.type === 'friend_accepted' || data.type === 'friend_removed') {
          this.fetchProfile(); // Refresh friends list
        }
      };
    },
    async searchProfiles() {
      if (this.searchQuery.trim() === '') {
        this.searchResults = [];
        return;
      }
      try {
        const response = await fetch(`/profile/search_profiles/?q=${this.searchQuery}`);
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
    async sendFriendRequest(friendId) {
      try {
        const response = await fetch('/profile/add_friend/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': this.getCookie('csrftoken'),
          },
          body: JSON.stringify({ friend_profile_id: friendId }),
        });
        if (response.ok) {
          alert('Friend request sent successfully');
          this.searchProfiles();
        } else {
          console.error('Failed to send friend request');
        }
      } catch (error) {
        console.error('Error sending friend request:', error);
      }
    },
    async acceptFriendRequest(friendId) {
      try {
        const response = await fetch('/profile/accept_friend_request/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': this.getCookie('csrftoken'),
          },
          body: JSON.stringify({ friend_profile_id: friendId }),
        });
        if (response.ok) {
          alert('Friend request accepted successfully');
          this.fetchIncomingFriendRequests();
          this.fetchProfile(); // Refresh friends list
        } else {
          console.error('Failed to accept friend request');
        }
      } catch (error) {
        console.error('Error accepting friend request:', error);
      }
    },
    async declineFriendRequest(friendId) {
      try {
        const response = await fetch('/profile/decline_friend_request/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': this.getCookie('csrftoken'),
          },
          body: JSON.stringify({ friend_profile_id: friendId }),
        });
        if (response.ok) {
          alert('Friend request declined successfully');
          this.fetchIncomingFriendRequests();
        } else {
          console.error('Failed to decline friend request');
        }
      } catch (error) {
        console.error('Error declining friend request:', error);
      }
    },
    async removeFriend(friendId) {
      try {
        const response = await fetch('/profile/remove_friend/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': this.getCookie('csrftoken'),
          },
          body: JSON.stringify({ friend_profile_id: friendId }),
        });
        if (response.ok) {
          alert('Friend removed successfully');
          this.fetchProfile(); // Refresh friends list
        } else {
          console.error('Failed to remove friend');
        }
      } catch (error) {
        console.error('Error removing friend:', error);
      }
    },
    async logout() {
      try {
        const csrfToken = this.getCookie('csrftoken');
        if (csrfToken) {
          await this.logoutAction({ csrftoken: csrfToken });
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
        for (let i = 0; i < cookies.length; i++) {
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
    async updateProfile() {
      const formData = new FormData();
      formData.append('display_name', this.displayName);
      if (this.avatarFile) {
        formData.append('avatar', this.avatarFile);
      }

      const csrfToken = this.getCookie('csrftoken');

      try {
        const response = await fetch('/profile/', {
          method: 'PUT',
          headers: {
            'X-CSRFToken': csrfToken,
          },
          body: formData,
        });
        if (response.ok) {
          await this.fetchProfile();
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
  max-width: 400px;
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
  border: 1px solid #4caf50;
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
}
</style>