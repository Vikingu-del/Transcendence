<template>
  <div class="play-container">
    <div class="game-controls">
      <button 
        @click="createGameLink" 
        :disabled="isGameCreated"
      >
        Create a Game Link
      </button>

      <div v-if="isGameCreated" class="share-section">
        <h3>Share with Friends</h3>
        <div class="friends-list">
          <div v-if="profile.friends && profile.friends.length > 0">
            <div v-for="friend in profile.friends" :key="friend.id" class="profile-item">
              <div class="user-info">
                <img :src="friend.avatar" :alt="friend.display_name" class="profile-avatar">
                <span class="profile-name">{{ friend.display_name }}</span>
                <span :class="['status-dot', friend.is_online ? 'online' : 'offline']"></span>
              </div>
              <button 
                @click="shareLink(friend.id)"
                class="primary-btn"
              >
                Share Link
              </button>
            </div>
          </div>
          <p v-else class="no-content">No friends available to share with</p>
        </div>
      </div>

      <button 
        @click="startGame"
        :disabled="!isGameCreated"
      >
        Play Game
      </button>
    </div>

    <div v-if="gameLink" class="game-link">
      <p>Game Link: {{ gameLink }}</p>
    </div>
  </div>

  <pre>{{ profile }}</pre>
  <pre> TOken 
    {{ token }}
  </pre>
</template>

<script>
import { ref } from 'vue';

export default {
  data() {
    return {
      gameLink: '',
      friends: [],
      selectedFriend: null,
      isGameCreated: false,
      gameId: null,
      chatSocket: null,
      gameSocket: null,
      profile: {
        friends: []
      },
      currentUserId: null,
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
  },

  mounted() {
    this.fetchProfile();
    // this.initNotificationSocket();
  },

  async created() {
    try {
      const token = localStorage.getItem('token');
      console.log('Initial token:', token);
      
      if (!token) {
        await this.$router.push('/login');
        return;
      }
      
      // this.initNotificationSocket();
    } catch (error) {
      console.error('Initialization error:', error);
      this.$router.push('/login');
    }
  },

  methods: {

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

    async createGameLink() {
      try {
        const response = await fetch('/api/pong/create/', {
          method: 'POST',
          headers: {
            'Authorization': `Token ${localStorage.getItem('token')}`,
            'Content-Type': 'application/json'
          }
        });

        if (!response.ok) {
          throw new Error('Failed to create game');
        }

        const data = await response.json();
        this.gameId = data.id;
        this.gameLink = `/pong/${data.id}`;
        this.isGameCreated = true;
        
      } catch (error) {
        console.error('Error creating game:', error);
      }
    },


    async shareLink(friendId) {
      if (!this.gameLink || !friendId) return;

      try {
        // Send game invitation through chat service
        const response = await fetch('http://localhost:8002/api/chat/send-message/', {
          method: 'POST',
          headers: {
            'Authorization': `Token ${localStorage.getItem('token')}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            recipient_id: friendId,
            message: `Join my Pong game! Click here: ${this.gameLink}`,
            type: 'game_invitation'
          })
        });

        if (!response.ok) {
          throw new Error('Failed to send game invitation');
        }

      } catch (error) {
        console.error('Error sharing game link:', error);
      }
    },

    startGame() {
      if (!this.gameId) return;

      // Initialize game WebSocket connection
      this.gameSocket = new WebSocket(`ws://localhost:8005/ws/pong/${this.gameId}/`);
      
      this.gameSocket.onopen = () => {
        console.log('Connected to game server');
        this.$router.push(`/game/${this.gameId}`);
      };

      this.gameSocket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log('Received game data:', data);
      };

      this.gameSocket.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
    }
  }
};
</script>


<style scoped>

.friends-list {
  margin-top: 20px;
  max-height: 300px;
  overflow-y: auto;
}

.profile-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
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
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
}

.profile-name {
  color: #ffffff;
  font-size: 16px;
}

.status-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  margin-left: 10px;
}

.status-dot.online {
  background-color: #03a670;
}

.status-dot.offline {
  background-color: #a60303;
}

.no-content {
  text-align: center;
  color: #666;
  padding: 20px;
}

.play-container {
  padding: 20px;
  max-width: 600px;
  margin: 0 auto;
}

.game-controls {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.share-section {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

button {
  padding: 10px 20px;
  border-radius: 5px;
  border: none;
  background-color: #4CAF50;
  color: white;
  cursor: pointer;
}

button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

select {
  padding: 8px;
  border-radius: 4px;
  margin-bottom: 10px;
}

.game-link {
  margin-top: 20px;
  padding: 10px;
  background-color: #f0f0f0;
  border-radius: 4px;
}
</style>