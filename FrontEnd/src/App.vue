<script setup>
import { RouterLink, RouterView, useRouter } from 'vue-router'
import HelloWorld from './components/HelloWorld.vue'
import { computed, onMounted, ref, onUnmounted } from 'vue'
import { useStore } from 'vuex'
import { provide } from 'vue'
import { useI18n } from 'vue-i18n'


const { t, locale } = useI18n()
const store = useStore()
const router = useRouter()
const isAbleToPlay = computed(() => store.state.isAbleToPlay)
const isAuthenticated = computed(() => store.state.isAuthenticated)
const unreadNotificationCount = ref(0)
const notificationSocket = ref(null)
const gameInviteTimeout = ref(null)
const gameInviteNotification = ref(null) // Add this line

const languages = [
  { code: 'en', name: 'English' },
  { code: 'fr', name: 'Français' },
  { code: 'de', name: 'Deutsch' }
]

async function logout() {
  try {
    await store.dispatch('logoutAction')
    router.push('/login')
  } catch (error) {
    console.error('Logout error:', error)
  }
}

async function fetchUnreadNotificationCount() {
  try {
    const token = localStorage.getItem('token')
    if (!token || !isAuthenticated.value) return
    
    console.log('Fetching unread notification count...')
    
    const response = await fetch('/api/notification/unread-count/', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    
    if (!response.ok) {
      const errorText = await response.text()
      console.error('Failed to fetch notification count:', response.status, errorText)
      return
    }
    
    const data = await response.json()
    console.log('Unread notification count:', data.count)
    unreadNotificationCount.value = data.count
  } catch (error) {
    console.error('Error fetching notification count:', error)
    // Don't set count to 0 on network errors to avoid flickering the badge
    // Only set to 0 when we explicitly know there are no unread notifications
  }
}

function initNotificationSocket() {
  try {
    const token = localStorage.getItem('token')
    if (!token || !isAuthenticated.value) return
    
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsHost = window.location.host
    const wsUrl = `${wsProtocol}//${wsHost}/ws/notification/?token=${encodeURIComponent(token)}`
    
    console.log('Connecting to notification socket:', wsUrl)
    notificationSocket.value = new WebSocket(wsUrl)
    
    notificationSocket.value.onopen = () => {
      console.log('Notification socket connected')
    }
    
    notificationSocket.value.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        console.log('Notification received in App.vue:', data)
        
        // Handle game invites specially
        if (data.type === 'game_invite' && parseInt(data.recipient_id) === parseInt(store.state.userId)) {
          handleGameInvite(data);
        }
        
        // Update notification count for all notifications
        fetchUnreadNotificationCount();
      } catch (error) {
        console.error('Error processing notification:', error)
      }
    }

    // Add the game invite handler function
    function handleGameInvite(data) {
      console.log('Game invite received:', data);
      
      // Clear any existing timeout
      if (gameInviteTimeout.value) {
        clearTimeout(gameInviteTimeout.value);
      }
      
      // Create the game invitation notification
      gameInviteNotification.value = {
        senderId: data.sender_id,
        sender: data.sender_name,
        gameId: data.game_id,
        timestamp: new Date().toISOString()
      };
      
      // Add timeout to auto-expire the invitation after 30 seconds
      gameInviteTimeout.value = setTimeout(() => {
        gameInviteNotification.value = null;
      }, 30000);
      
      // Play notification sound if available
      const notificationSound = document.getElementById('notificationSound');
      if (notificationSound) {
        notificationSound.play().catch(e => console.log('Error playing sound:', e));
      }
    }
    
    notificationSocket.value.onerror = (error) => {
      console.error('Notification socket error:', error)
    }
    
    notificationSocket.value.onclose = () => {
      console.log('Notification socket closed')
      
      // Reconnect if authenticated
      if (isAuthenticated.value) {
        console.log('Attempting to reconnect notification socket...')
        setTimeout(initNotificationSocket, 3000)
      }
    }
  } catch (error) {
    console.error('Error initializing notification socket:', error)
    if (isAuthenticated.value) {
      setTimeout(initNotificationSocket, 3000)
    }
  }
}

function sendNotification(notificationData) {
  if (notificationSocket.value && notificationSocket.value.readyState === WebSocket.OPEN) {
    notificationSocket.value.send(JSON.stringify(notificationData))
    return true
  }
  console.warn('Notification socket not connected')
  return false
}

// Add methods to accept or decline the game invitation
function acceptGameInvite() {
  if (!gameInviteNotification.value) return;
  
  // Navigate to Friends.vue with game parameters
  router.push({
    path: '/friends',
    query: { 
      action: 'join-game',
      gameId: gameInviteNotification.value.gameId,
      sender: gameInviteNotification.value.sender,
      senderId: gameInviteNotification.value.senderId
    }
  });
  
  // Clear the invitation
  if (gameInviteTimeout.value) {
    clearTimeout(gameInviteTimeout.value);
  }
  gameInviteNotification.value = null;
}

function declineGameInvite() {
  if (!gameInviteNotification.value || !notificationSocket.value) return;
  
  // Send decline message
  if (notificationSocket.value.readyState === WebSocket.OPEN) {
    const declineData = {
      type: 'game_decline',
      game_id: gameInviteNotification.value.gameId,
      recipient_id: gameInviteNotification.value.senderId,
      sender_id: store.state.userId
    };
    
    notificationSocket.value.send(JSON.stringify(declineData));
  }
  
  // Clear the invitation
  if (gameInviteTimeout.value) {
    clearTimeout(gameInviteTimeout.value);
  }
  gameInviteNotification.value = null;
}

// Check authentication state on app load
onMounted(async () => {
  let token = localStorage.getItem('token')
  console.log('Token status:', token ? 'Present' : 'Not found')

  const clearTokenAndRedirect = () => {
    localStorage.removeItem('token')
    store.commit('setToken', null)
    if (router.currentRoute.value.path !== '/login') {
      router.push('/login')
    }
  }

  if (!token || token === 'undefined' || token === 'null') {
    clearTokenAndRedirect()
    return
  }

  try {
    const response = await fetch('/api/auth/validate-token/', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    
    if (!response.ok) {
      throw new Error('Token validation failed')
    }

    store.commit('setToken', token)
  } catch (error) {
    console.error('Token validation error:', error)
    clearTokenAndRedirect()
  }
})

// Replace your second onMounted with this version
onMounted(() => {
  locale.value = 'en'
  
  // Set up notification handling if authenticated
  if (isAuthenticated.value) {
    // Fetch notification count immediately
    fetchUnreadNotificationCount()
    
    // Initialize WebSocket for real-time notifications
    initNotificationSocket()
    
    // Set up backup polling interval (in case WebSocket fails)
    const intervalId = setInterval(fetchUnreadNotificationCount, 60000)
    
    // Clean up when component unmounts
    onUnmounted(() => {
      clearInterval(intervalId)
      
      // Close WebSocket connection
      if (notificationSocket.value) {
        notificationSocket.value.close()
        notificationSocket.value = null
      }
    })
  }
})

// Make notification socket and methods available to all child components
provide('notificationService', {
  socket: notificationSocket,
  sendNotification: (data) => {
    if (notificationSocket.value && notificationSocket.value.readyState === WebSocket.OPEN) {
      notificationSocket.value.send(JSON.stringify(data));
      return true;
    }
    return false;
  },
  fetchUnreadCount: fetchUnreadNotificationCount,
  unreadCount: unreadNotificationCount,
  gameInvite: gameInviteNotification,
  acceptGameInvite,
  declineGameInvite
});

</script>

<template>
  <header>
    <img alt="Vue logo" class="logo" src="@/assets/logo.svg" width="125" height="125" />
    
    <div class="wrapper">
      <HelloWorld msg="Transcendence" />
      <nav>
        <RouterLink to="/">{{ t('nav.home') }}</RouterLink>
        <RouterLink v-if="!isAuthenticated" to="/login">{{ t('nav.login') }}</RouterLink>
        <RouterLink v-if="!isAuthenticated" to="/register">{{ t('nav.register') }}</RouterLink>
        <RouterLink v-if="isAuthenticated" to="/profile">{{ t('nav.profile') }}</RouterLink>
        <RouterLink v-if="isAuthenticated" to="/friends">{{ t('nav.friends') }}</RouterLink>
        <RouterLink v-if="isAuthenticated" to="/notifications">
          Notifications
          <span v-if="unreadNotificationCount > 0" class="notification-badge">
            {{ unreadNotificationCount }}
          </span>
        </RouterLink>
        <RouterLink v-if="isAuthenticated" to="/tournament">{{ t('nav.tournament') }}</RouterLink>
      </nav>
    </div>
    <div class="language-selector">
      <select v-model="locale">
        <option v-for="lang in languages" :key="lang.code" :value="lang.code">
          {{ lang.name }}
        </option>
      </select>
    </div>
  </header>

  <RouterView />
  <transition name="slide-down">
    <div v-if="gameInviteNotification" class="game-invite-banner">
      <div class="game-invite-content">
        <div class="game-invite-text">
          {{ gameInviteNotification.sender }} has invited you to play a game!
        </div>
        <div class="game-invite-actions">
          <button @click="acceptGameInvite" class="game-btn accept-btn">Accept</button>
          <button @click="declineGameInvite" class="game-btn decline-btn">Decline</button>
        </div>
      </div>
    </div>
  </transition>

  <!-- Add audio element for notification sound -->
  <audio id="notificationSound" src="/notification-sound.mp3" preload="auto"></audio>
</template>

<style scoped>

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

  .game-btn {
    padding: 8px 16px;
    border-radius: 4px;
    border: none;
    cursor: pointer;
    font-weight: 500;
    transition: all 0.2s;
  }

  .accept-btn {
    background: white;
    color: #03a670;
  }

  .accept-btn:hover {
    background: #f0f0f0;
    transform: translateY(-2px);
  }

  .decline-btn {
    background: rgba(255, 255, 255, 0.2);
    color: white;
  }

  .decline-btn:hover {
    background: rgba(255, 255, 255, 0.3);
    transform: translateY(-2px);
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

.language-selector {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 1000;
}

.language-selector select {
  padding: 8px 12px;
  border-radius: 6px;
  border: 2px solid #03a670;
  background-color: #2d2d2d;
  color: white;
  font-size: 14px;
  cursor: pointer;
  outline: none;
  transition: all 0.3s ease;
}

.language-selector select:hover {
  border-color: #04d38e;
  box-shadow: 0 0 10px rgba(3, 166, 112, 0.3);
}

header {
  line-height: 1.5;
  max-height: 100vh;
}

.logo {
  display: block;
  margin: 0 auto 2rem;
}

nav {
  width: 100%;
  font-size: 12px;
  text-align: center;
  margin-top: 2rem;
}

nav a.router-link-exact-active {
  color: var(--color-text);
}

nav a.router-link-exact-active:hover {
  background-color: transparent;
}

nav a {
  display: inline-block;
  padding: 0 1rem;
  border-left: 1px solid var(--color-border);
}

nav a:first-of-type {
  border: 0;
}

@media (min-width: 1024px) {
  header {
    display: flex;
    place-items: center;
    padding-right: calc(var(--section-gap) / 2);
  }
    
  .logo {
    margin: 0 2rem 0 0;
  }
    
  header .wrapper {
    display: flex;
    place-items: flex-start;
    flex-wrap: wrap;
  }
      
  nav {
    text-align: left;
    margin-left: -1rem;
    font-size: 1rem;
    padding: 1rem 0;
    margin-top: 1rem;
  }
  .notification-badge {
    background-color: #f44336;
    color: white;
    padding: 2px 6px;
    border-radius: 50%;
    font-size: 0.7rem;
    margin-left: 5px;
    position: relative;
    top: -8px;
  }
}
</style>