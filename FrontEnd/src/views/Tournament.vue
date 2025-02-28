<template>
  <!-- <div class="tournament-container">
    <div v-if="!isEnrolled" class="tournament-prompt">
      <p class="question">New Tournament Starting Soon. Wanna Join?</p>
      <div class="button-group">
        <button class="btn btn-yes" @click="handleYes">Yes</button>
        <button class="btn btn-no" @click="handleNo">No</button>
      </div>
    </div> -->
    <div class="tournament-container">
    <!-- Show enrollment prompt only if not enrolled and can enroll -->
    <div v-if="!isEnrolled && canEnroll" class="tournament-prompt">
      <p class="question">New Tournament Starting Soon. Wanna Join?</p>
      <div class="button-group">
        <button class="btn btn-yes" @click="handleYes">Yes</button>
        <button class="btn btn-no" @click="handleNo">No</button>
      </div>
    </div>

    <!-- Show message if there's an active tournament but user can't enroll -->
    <div v-if="!isEnrolled && !canEnroll" class="tournament-message">
      <p>{{ enrollmentMessage }}</p>
    </div>

    <!-- Tournament status -->
    <div v-if="isEnrolled" class="tournament-status">
      <!-- Waiting room -->
      <div v-if="tournamentStatus === 'waiting'" class="waiting-room">
        <h2>Tournament Waiting Room</h2>
        <div class="players-counter">
          <p>Players: {{ currentPlayers }}/{{ maxPlayers }}</p>
          <div class="progress-bar">
            <div :style="{ width: (currentPlayers / maxPlayers * 100) + '%' }" 
                 class="progress"></div>
          </div>
        </div>
        
        <div class="players-list">
          <h3>Connected Players:</h3>
          <ul>
            <li v-for="player in connectedPlayers" 
                :key="player.id"
                :class="{ 'current-player': player.id === currentUserId }">
              {{ formattedPlayerName(player) }}
              <span v-if="player.id === currentUserId">(You)</span>
            </li>
          </ul>
        </div>

        <div v-if="lastMessage" class="notification">
          {{ lastMessage }}
        </div>
      </div>

      <!-- Tournament starting -->
      <div v-if="tournamentStatus === 'starting'" class="tournament-bracket">
        <h2>Tournament Bracket</h2>
        
        <!-- Semi-finals -->
        <div class="semi-finals-container">
          <h3>Semi-finals</h3>
          <div class="semi-finals">
            <div v-for="match in tournamentData.semi_finals" 
                :key="match.match_id" 
                class="match-card"
                :class="{ 'completed': match.status === 'completed' }">
              <h4>Semi-Final {{ match.match_id.split('_')[1] + 1 }}</h4>
              <div class="player" 
                    :class="{ 'winner': match.winner?.id === match.player1.id }">
                  <div class="player-info">
                    <img v-if="match.player1.avatar_url" 
                        :src="match.player1.avatar_url" 
                        class="player-avatar"
                        alt="Player avatar">
                    <span class="player-name">{{ formattedPlayerName(match.player1) }}</span>
                  </div>
                </div>
                <div class="vs">VS</div>
                <div class="player"
                    :class="{ 'winner': match.winner?.id === match.player2.id }">
                  <div class="player-info">
                    <img v-if="match.player2.avatar_url" 
                        :src="match.player2.avatar_url" 
                        class="player-avatar"
                        alt="Player avatar">
                    <span class="player-name">{{ formattedPlayerName(match.player2) }}</span>
                  </div>
                </div>
              <button v-if="isPlayerInMatch(match) && match.status === 'pending'"
                      @click="startMatch(match)"
                      class="btn primary-btn">
                Start Match
              </button>
            </div>
          </div>
        </div>

        <!-- Finals -->
        <div v-if="tournamentData.current_phase === 'final'" class="finals-container">
          <h3>Final</h3>
          <div class="final-match">
            <div class="match-card"
                :class="{ 'completed': tournamentData.final.status === 'completed' }">
              <h4>Final Match</h4>
              <div class="player"
                  :class="{ 'winner': tournamentData.final.winner?.id === tournamentData.final.player1?.id }">
                {{ tournamentData.final.player1?.username || 'TBD' }}
              </div>
              <div class="vs">VS</div>
              <div class="player"
                  :class="{ 'winner': tournamentData.final.winner?.id === tournamentData.final.player2?.id }">
                {{ tournamentData.final.player2?.username || 'TBD' }}
              </div>
              <button v-if="isPlayerInMatch(tournamentData.final) && tournamentData.final.status === 'pending'"
                      @click="startMatch(tournamentData.final)"
                      class="btn primary-btn">
                Start Final Match
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- WebSocket connection status -->
  <Teleport to="body" v-if="showGame">
    <Game 
      :opponent="currentMatch.opponent.username"
      :gameId="currentMatch.match_id"
      :isHost="isHost"
      :userId="currentUserId"
      @close="handleGameEnd"
      @gameOver="handleGameOver"
    />
  </Teleport>

</template>


<script>

import Game from './Game.vue'; 

export default {
  name: 'Tournament',

  components: {
    Game
  },

  data() {
    return {
      profile: null,
      isEnrolled: false,
      tournamentStatus: 'waiting',
      currentPlayers: 0,
      maxPlayers: 4,
      matches: [],
      tournamentId: null,
      lastMessage: '',
      currentUserId: null,
      canEnroll: false,
      enrollmentMessage: '',

      // WebSocket connection
      tournamentSocket: null,
      wsConnected: false,
      wsReconnectAttempts: 0,
      maxReconnectAttempts: 5,
      reconnectionTimeout: null,
      connectedPlayers: [],

      // Game state
      tournamentData: {
        semi_finals: [],
        final: null,
        current_phase: null
      },
      showGame: false,
      currentMatch: null,
      isHost: false
    }
  },
  computed: {
    getToken() {
      return localStorage.getItem('token');
    },
    isAuthenticated() {
      return !!this.getToken; // Changed from this.token to this.getToken
    },
    formattedPlayerName() {
    return (player) => {
      return player.display_name || player.username;
    }
  }
  },
  async created() {
    try {
      // Check authentication first
      if (!this.getToken) { // Changed from !this.isAuthenticated
        console.log('No token found, redirecting to login');
        this.$router.push('/login');
        return;
      }

      console.log('Initial token:', this.getToken);

      // First fetch profile
      await this.fetchProfile();
      
      // Only check enrollment after profile is loaded
      if (this.profile && this.profile.id) {
        await this.checkEnrollment();
        
        // If enrolled, fetch tournament status and connect to WebSocket
        if (this.isEnrolled) {
          await this.fetchTournamentStatus();
          this.connectWebSocket();
        }
      }
    } catch (error) {
      console.error('Initialization error:', error);
      if (error.message.includes('token_not_valid')) {
        this.$router.push('/login');
      }
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
          if (response.status === 401) {
            this.$router.push('/login');
            return;
          }
          throw new Error(`Profile fetch failed: ${response.statusText}`);
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

    async fetchDisplayNames(players) {
      const token = this.getToken;
      if (!token) return players;

      try {
        const updatedPlayers = await Promise.all(players.map(async (player) => {
          try {
            const response = await fetch(`/api/user/profile/${player.id}/`, {
              headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
              }
            });

            if (response.ok) {
              const profile = await response.json();
              return {
                ...player,
                display_name: profile.display_name || player.username
              };
            }
          } catch (error) {
            console.error(`Error fetching profile for player ${player.id}:`, error);
          }
          return player;
        }));

        return updatedPlayers;
      } catch (error) {
        console.error('Error fetching display names:', error);
        return players;
      }
    },

    async checkEnrollment() {
      try {
        const token = this.getToken;
        if (!token) {
          console.error('No auth token found');
          this.$router.push('/login');
          return;
        }

        const response = await fetch('/api/tournament/check-enrollment/', {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          }
        });

        if (response.status === 401) {
          console.error('Authentication failed');
          this.$router.push('/login');
          return;
        }

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        this.isEnrolled = data.enrolled;
        this.canEnroll = data.can_enroll;
        this.enrollmentMessage = data.message;

        // If enrolled, fetch tournament status
        if (this.isEnrolled) {
          await this.fetchTournamentStatus();
          this.connectWebSocket();
        }
        
      } catch (error) {
        console.error('Error checking enrollment:', error);
        if (error.message.includes('token_not_valid')) {
          this.$router.push('/login');
        }
      }
    },

    async fetchTournamentStatus() {
      try {
        const token = this.getToken;
        if (!token) throw new Error('No auth token found');

        const response = await fetch('/api/tournament/active/', {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });
        
        if (!response.ok) {
          const errorText = await response.text();
          throw new Error(errorText);
        }

        const data = await response.json();
        this.tournamentStatus = data.status;
        this.currentPlayers = data.players;
        this.maxPlayers = data.max_players;
        this.tournamentId = data.id;
      } catch (error) {
        console.error('Error fetching tournament status:', error);
        if (error.message.includes('token_not_valid')) {
          this.$router.push('/login');
        }
      }
    },

    async handleYes() {
      try {
        const token = this.getToken;
        if (!token) throw new Error('No auth token found');

        const response = await fetch('/api/tournament/enroll/', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });
        
        if (!response.ok) {
          const errorText = await response.text();
          throw new Error(errorText);
        }

        const data = await response.json();
        if (data.enrolled) {
          this.isEnrolled = true;
          this.tournamentId = data.tournament_id;
          await this.fetchTournamentStatus();
          this.connectWebSocket();
        }
      } catch (error) {
        console.error('Error enrolling in tournament:', error);
        if (error.message.includes('token_not_valid')) {
          this.$router.push('/login');
        }
      }
    },

    handleMessage(event) {
      try {
        const data = JSON.parse(event.data);
        console.log('Received websocket message:', data);

        switch(data.type) {
          case 'player_update':
            // Update players list and count
            this.connectedPlayers = data.players;
            this.currentPlayers = data.total_players;
            if (data.message) this.lastMessage = data.message;

            // Check if tournament is starting
            if (data.tournament_status === 'starting') {
              console.log('Tournament is starting, updating state');
              this.tournamentStatus = 'starting';
              
              // Check if we have valid matches data
              if (data.matches && typeof data.matches === 'object') {
                this.tournamentData = {
                  semi_finals: data.matches.semi_finals || [],
                  final: data.matches.final || null,
                  current_phase: data.matches.current_phase || 'semi-final'
                };
              } else {
                console.error('Invalid matches data received:', data.matches);
              }
            }
            break;
          
          case 'tournament_start':
            console.log('Received tournament start event');
            this.tournamentStatus = 'starting';
            if (data.tournament_data) {
              this.tournamentData = {
                semi_finals: data.tournament_data.semi_finals || [],
                final: data.tournament_data.final || null,
                current_phase: data.tournament_data.current_phase || 'semi-final'
              };
            }
            if (data.message) this.lastMessage = data.message;
            break;

          case 'match_update':
            this.handleMatchUpdate(data);
            break;

          case 'error':
            console.error('Server error:', data.message);
            if (data.code === 'authentication_failed') {
              this.$router.push('/login');
            }
            break;
        }
      } catch (error) {
        console.error('Error handling message:', error);
      }
    },

    // Main connection function
    async connectWebSocket() {
      try {
        if (!this.validateConnection()) return;
        
        this.closeExistingConnection();
        const wsUrl = this.buildWebSocketUrl();
        
        this.tournamentSocket = new WebSocket(wsUrl);
        this.setupWebSocketHandlers();
        
        await this.waitForConnection();
      } catch (error) {
        console.error('Connection error:', error);
        this.wsConnected = false;
        
        // Only attempt reconnection for specific error codes
        if (error.code === 4000 || error.code === 1006) {
          await this.handleReconnection();
        }
      }
    },

    // Validation check
    validateConnection() {
      if (!this.getToken || !this.tournamentId) {
        console.log('Missing token or tournament ID');
        return false;
      }
      return true;
    },

    // Close existing connection
    closeExistingConnection() {
      if (this.tournamentSocket) {
        this.tournamentSocket.close();
        this.tournamentSocket = null;
      }
    },

    // Build WebSocket URL
    buildWebSocketUrl() {
      const token = localStorage.getItem('token');

      const wsUrl = `ws://localhost:8005/ws/tournament/${this.tournamentId}/?token=${token}`;

      return wsUrl;
    },

    // Setup WebSocket event handlers
    setupWebSocketHandlers() {
      this.tournamentSocket.onopen = this.handleOpen;
      this.tournamentSocket.onclose = this.handleClose;
      this.tournamentSocket.onerror = this.handleError;
      this.tournamentSocket.onmessage = this.handleMessage;
    },

    // WebSocket event handlers
    handleOpen() {
      console.log('WebSocket connection established');
      this.wsConnected = true;
      this.wsReconnectAttempts = 0;
    },

    handleClose(event) {
      console.log('WebSocket closed:', event.code, event.reason);
      this.wsConnected = false;
      
      // Only reconnect for specific close codes
      if (event.code === 4000 || event.code === 1006) {
        this.handleReconnection();
      } else if (event.code === 4001) {
        // Authentication failed, redirect to login
        this.$router.push('/login');
      }
    },

    handleError(error) {
      console.error('WebSocket error:', error);
      this.wsConnected = false;
    },

    // Update tournament state
    updateTournamentState(data) {
      this.currentPlayers = data.players;
      this.connectedPlayers = data.connected_players || [];
    },

    waitForConnection(timeout = 5000) {
      return new Promise((resolve, reject) => {
        const timer = setTimeout(() => {
          reject(new Error('WebSocket connection timeout'));
        }, timeout);

        this.tournamentSocket.onopen = () => {
          clearTimeout(timer);
          this.wsConnected = true;
          this.wsReconnectAttempts = 0;
          console.log('WebSocket connection established');
          resolve();
        };
      });
    },

    async handleReconnection() {
      if (this.wsReconnectAttempts >= this.maxReconnectAttempts) {
        console.log('Max reconnection attempts reached');
        this.$router.push('/tournament'); // Redirect to tournament page
        return;
      }

      this.wsReconnectAttempts++;
      
      // Exponential backoff with maximum delay of 5 seconds
      const delay = Math.min(1000 * Math.pow(1.5, this.wsReconnectAttempts), 5000);
      console.log(`Reconnecting in ${delay}ms... Attempt ${this.wsReconnectAttempts}`);
      
      if (this.reconnectionTimeout) {
        clearTimeout(this.reconnectionTimeout);
      }
      
      this.reconnectionTimeout = setTimeout(async () => {
        try {
          // Check if we're still enrolled before reconnecting
          await this.checkEnrollment();
          if (this.isEnrolled) {
            await this.connectWebSocket();
          } else {
            console.log('No longer enrolled in tournament');
            this.$router.push('/tournament');
          }
        } catch (error) {
          console.error('Reconnection failed:', error);
        }
      }, delay);
    },


    //Game Related Methods
    isPlayerInMatch(match) {
      return match.player1.id === this.currentUserId || 
             match.player2.id === this.currentUserId;
    },

    startMatch(match) {
      console.log('Starting match:', match);
      this.currentMatch = {
        match_id: match.match_id,
        opponent: match.player1.id === this.currentUserId ? match.player2 : match.player1
      };
      this.isHost = match.player1.id === this.currentUserId;
      this.showGame = true;
    },

    handleGameEnd() {
      console.log('Game ended');
      this.showGame = false;
      this.currentMatch = null;
    },

    handleGameOver(result) {
      console.log('Game over with result:', result);
      if (this.tournamentSocket?.readyState === WebSocket.OPEN) {
        const matchResult = {
          type: 'match_complete',
          match_id: this.currentMatch.match_id,
          winner_id: result.winner,
          final_score: result.score
        };
        
        console.log('Sending match result:', matchResult);
        this.tournamentSocket.send(JSON.stringify(matchResult));
      }
      this.handleGameEnd();
    },

    handleMatchUpdate(data) {
      console.log('Handling match update:', data);
      const { match_id, winner_id } = data;
      
      if (!this.tournamentData) {
        console.error('Tournament data not initialized');
        return;
      }

      // Update semi-finals
      if (match_id.startsWith('semi_')) {
        const semiMatch = this.tournamentData.semi_finals.find(m => m.match_id === match_id);
        if (semiMatch) {
          semiMatch.status = 'completed';
          semiMatch.winner = winner_id;
          console.log('Updated semi-final match:', semiMatch);
        }

        // Check if all semi-finals are complete
        const allSemisComplete = this.tournamentData.semi_finals.every(m => m.status === 'completed');
        if (allSemisComplete && this.tournamentData.current_phase === 'semi-final') {
          this.tournamentData.current_phase = 'final';
          console.log('All semi-finals complete, moving to finals');
        }
      }
      
      // Update finals
      if (match_id === 'final') {
        if (this.tournamentData.final) {
          this.tournamentData.final.status = 'completed';
          this.tournamentData.final.winner = winner_id;
          this.tournamentData.current_phase = 'completed';
          console.log('Tournament completed, winner:', winner_id);
        }
      }
    },

    // Add this method to clean up
    beforeDestroy() {
      if (this.reconnectionTimeout) {
        clearTimeout(this.reconnectionTimeout);
      }
      if (this.tournamentSocket) {
        this.tournamentSocket.close(1000, 'Component destroyed');
        this.tournamentSocket = null;
      }
    },

    beforeUnmount() {
      if (this.showGame) {
        this.handleGameEnd();
      }
      if (this.reconnectionTimeout) {
        clearTimeout(this.reconnectionTimeout);
      }
      if (this.tournamentSocket) {
        this.tournamentSocket.close(1000, 'Component destroyed');
        this.tournamentSocket = null;
      }
    },

    watch: {
      tournamentStatus(newStatus, oldStatus) {
        console.log(`Tournament status changed from ${oldStatus} to ${newStatus}`);
      },
      'tournamentData.semi_finals': {
        handler(newVal) {
          console.log('Semi-finals updated:', newVal);
        },
        deep: true
      }
    }
  }
}
</script>

<style scoped>
.tournament-container {
text-align: center;
padding: 2rem;
}

.tournament-prompt {
margin-top: 2rem;
}

.tournament-status {
  max-width: 800px;
  margin: 0 auto;
}

.waiting-status {
  text-align: center;
  padding: 2rem;
  background: #2c2c2c;
  border-radius: 8px;
  margin-top: 2rem;
}

.question {
font-size: 1.5rem;
margin-bottom: 2rem;
}

.button-group {
display: flex;
justify-content: center;
gap: 1rem;
}

.btn {
padding: 0.5rem 2rem;
border: none;
border-radius: 4px;
cursor: pointer;
font-size: 1rem;
transition: transform 0.2s;
}

.btn:hover {
transform: scale(1.05);
}

.btn-yes {
background-color: #4CAF50;
color: white;
}

.btn-no {
background-color: #f44336;
color: white;
}

.connection-status {
  position: fixed;
  top: 1rem;
  right: 1rem;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  background-color: #ff4444;
  color: white;
  font-size: 0.875rem;
  transition: background-color 0.3s ease;
}

.connection-status.connected {
  background-color: #44ff44;
}

.matches-container {
  margin-top: 2rem;
  padding: 1rem;
  background: #2c2c2c;
  border-radius: 8px;
}

.semi-finals {
  display: flex;
  justify-content: space-around;
  margin-top: 2rem;
}

.match-card {
  background: #3c3c3c;
  padding: 1rem;
  border-radius: 8px;
  width: 250px;
}

.match-card h3 {
  margin-bottom: 1rem;
  color: #fff;
}

.player {
  padding: 0.5rem;
  background: #4c4c4c;
  margin: 0.5rem 0;
  border-radius: 4px;
}

.vs {
  margin: 0.5rem 0;
  font-weight: bold;
  color: #ffaa00;
}

.tournament-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
}

.waiting-room {
  background: #2c2c2c;
  border-radius: 8px;
  padding: 2rem;
  margin-top: 2rem;
}

.players-counter {
  margin: 2rem 0;
  text-align: center;
}

.progress-bar {
  width: 100%;
  height: 20px;
  background: #444;
  border-radius: 10px;
  overflow: hidden;
  margin-top: 1rem;
}

.progress {
  height: 100%;
  background: #4CAF50;
  transition: width 0.3s ease;
}

.players-list {
  background: #3c3c3c;
  border-radius: 8px;
  padding: 1rem;
  margin-top: 2rem;
}

.players-list ul {
  list-style: none;
  padding: 0;
}

.players-list li {
  padding: 0.5rem;
  margin: 0.5rem 0;
  background: #4c4c4c;
  border-radius: 4px;
}

.current-player {
  background: #2196F3 !important;
  color: white;
}

.notification {
  margin-top: 2rem;
  padding: 1rem;
  background: #2196F3;
  border-radius: 4px;
  color: white;
}

.tournament-starting {
  text-align: center;
  animation: fadeIn 0.5s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.tournament-bracket {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.semi-finals-container,
.finals-container {
  margin: 2rem 0;
}

.match-card {
  background: #2c2c2c;
  padding: 1.5rem;
  border-radius: 8px;
  margin: 1rem 0;
  transition: all 0.3s ease;
}

.match-card.completed {
  background: #1a1a1a;
  opacity: 0.8;
}

.player {
  padding: 1rem;
  margin: 0.5rem 0;
  background: #3c3c3c;
  border-radius: 4px;
  transition: all 0.3s ease;
}

.player.winner {
  background: #4CAF50;
  color: white;
  font-weight: bold;
}

.vs {
  margin: 0.5rem 0;
  color: #888;
  font-weight: bold;
}

.primary-btn {
  margin-top: 1rem;
  background: #2196F3;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.primary-btn:hover {
  background: #1976D2;
  transform: translateY(-2px);
}

.player-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.player-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
}

.player-name {
  font-weight: bold;
}

.tournament-message {
  background: #2c2c2c;
  border-radius: 8px;
  padding: 1.5rem;
  margin: 2rem auto;
  max-width: 600px;
  text-align: center;
}

.tournament-message p {
  color: #fff;
  font-size: 1.2rem;
  margin: 0;
}
</style>