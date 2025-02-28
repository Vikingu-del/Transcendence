<template>
    <transition name="fade">
      <div v-if="showGameWindow" class="overlay">
        <PongGame 
          :opponent="opponent"
          :gameId="gameId"
          :isHost="isHost"
          :userId="userId"
          @close="closeGame"
        />
      </div>
    </transition>
  </template>
  
  <script>
  import PongGame from '../views/Game.vue';
  import { ref, computed } from 'vue';
  import { useStore } from 'vuex';
  
  export default {
    name: 'GlobalGame',
    components: {
      PongGame
    },
    setup() {
      const store = useStore();
      
      // Get game state from store
      const showGameWindow = ref(false);
      const opponent = ref('');
      const gameId = ref('');
      const isHost = ref(false);
      const userId = computed(() => store.state.userId || parseInt(localStorage.getItem('userId')));
  
      // Method to open game
      const openGame = (gameData) => {
        console.log('GlobalGame: Opening game with data:', gameData);
        opponent.value = gameData.opponent;
        gameId.value = gameData.gameId;
        isHost.value = gameData.isHost;
        showGameWindow.value = true;
        console.log('Game window open status:', showGameWindow.value);
      };
      
      // Method to close game
      const closeGame = () => {
        console.log('GlobalGame: Closing game window');
        showGameWindow.value = false;
        gameId.value = '';
        opponent.value = '';
        console.log('Game window closed, new status:', showGameWindow.value);
      };
      
      return {
        showGameWindow,
        opponent,
        gameId,
        isHost,
        userId,
        openGame,
        closeGame
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