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
    };
  },
  mounted() {
    // Get friends list when component mounts
    this.getFriendsList();
  },
  methods: {
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

    async getFriendsList() {
      try {
        const response = await fetch('http://localhost:8000/api/user/profile/friends/', {
          headers: {
            'Authorization': `Token ${localStorage.getItem('token')}`
          }
        });

        if (!response.ok) {
          throw new Error('Failed to fetch friends');
        }

        const data = await response.json();
        this.friends = data;

      } catch (error) {
        console.error('Error fetching friends:', error);
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
        <select v-model="selectedFriend">
          <option value="">Select a friend</option>
          <option 
            v-for="friend in friends" 
            :key="friend.id" 
            :value="friend.id"
          >
            {{ friend.display_name }}
          </option>
        </select>
        <button 
          @click="shareLink(selectedFriend)"
          :disabled="!selectedFriend"
        >
          Share Link with Friend
        </button>
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
</template>

<style scoped>
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