<template>
  <div class="profile-container">
    <div class="profile-card" v-if="profile">
      <!-- Avatar Section -->
      <div class="avatar-container">
        <img 
          :src="profile.avatar" 
          :alt="profile.display_name"
          class="profile-picture"
        />
      </div>

      <!-- Profile Info Section -->
      <div class="profile-section">
        <h2>{{ profile.display_name }}</h2>
        <p>Status: {{ profile.is_online ? 'Online' : 'Offline' }}</p>
      </div>

      <!-- Friends Section -->
      <div class="profile-section">
        <h3>Friends</h3>
        <div v-if="profile.friends && profile.friends.length > 0">
          <div v-for="friend in profile.friends" :key="friend.id" class="profile-item">
            <img :src="friend.avatar" :alt="friend.display_name" class="profile-avatar">
            <span class="profile-name">{{ friend.display_name }}</span>
            <span :class="['status', friend.is_online ? 'online' : 'offline']">
              {{ friend.is_online ? 'Online' : 'Offline' }}
            </span>
          </div>
        </div>
        <p v-else>No friends yet</p>
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
      loading: true,
      error: null,
      profile: null,
      isInitialized: false
    };
  },

  computed: {
    ...mapGetters(['getToken', 'isAuthenticated'])
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