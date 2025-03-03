<template>
    <transition name="fade">
      <div v-if="showGameWindow" class="overlay">
        <PongGame 
          :opponent="opponent"
          :opponentId="opponentId"
          :gameId="gameId"
          :isHost="isHost"
          :userId="userId"
          :tournamentId="tournamentId"
          @close="closeGame"
          @gameOver="handleGameOver"
        />
      </div>
    </transition>
  </template>
  
  <script>
  import PongGame from '../views/Game.vue';
  import { ref, computed, inject } from 'vue';
  import { useStore } from 'vuex';
  
  export default {
    name: 'GlobalGame',
    components: {
      PongGame
    },
    setup() {
      const store = useStore();
      const eventBus = inject('eventBus', null);
      
      // Get game state from store
      const showGameWindow = ref(false);
      const opponent = ref('');
      const opponentId = ref(null);
      const gameId = ref('');
      const isHost = ref(false);
      const userId = computed(() => store.state.userId || parseInt(localStorage.getItem('userId')));
      const tournamentId = ref(null);
  
      // Method to open game
      const openGame = (gameData) => {
                
        opponent.value = gameData.opponent;
        opponentId.value = parseInt(gameData.opponentId);
        gameId.value = gameData.gameId;
        isHost.value = gameData.isHost;
        tournamentId.value = gameData.tournamentId;
        showGameWindow.value = true;
      };
      
      // Method to close game
      const closeGame = () => {
        showGameWindow.value = false;
        gameId.value = '';
        opponent.value = '';
        tournamentId.value = null;
      };

      const handleGameOver = (result) => {
        
        // Emit the event globally for Tournament component
        if (eventBus) {
          eventBus.emit('tournament:gameOver', {
            gameId: gameId.value,
            tournamentId: tournamentId.value,
            ...result
          });
        }
        
        // Global custom event for components without eventBus
        if (window) {
          const customEvent = new CustomEvent('tournament:gameComplete', {
            detail: {
              gameId: gameId.value,
              tournamentId: tournamentId.value,
              ...result
            }
          });
          window.dispatchEvent(customEvent);
        }
        
        // Close the game window after a short delay
        setTimeout(() => {
          closeGame();
        }, 200);
      };
      
      return {
        showGameWindow,
        opponent,
        opponentId,
        gameId,
        isHost,
        userId,
        tournamentId,
        openGame,
        closeGame,
        handleGameOver
      };
    }
  }
  </script>
  
  <style scoped>
  .overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.8);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
  }
  
  .fade-enter-active,
  .fade-leave-active {
    transition: opacity 0.3s ease;
  }
  
  .fade-enter-from,
  .fade-leave-to {
    opacity: 0;
  }
  </style>