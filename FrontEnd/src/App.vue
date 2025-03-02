<script setup>
import { RouterLink, RouterView, useRouter } from 'vue-router'
import HelloWorld from './components/HelloWorld.vue'
import { computed, onMounted, ref, onUnmounted, nextTick } from 'vue'
import { useStore } from 'vuex'
import { provide } from 'vue'
import { watch } from 'vue'
import { useI18n } from 'vue-i18n'
import GlobalGame from './components/GlobalGame.vue'


const { t, locale } = useI18n()
const store = useStore()
const router = useRouter()
const isAbleToPlay = computed(() => store.state.isAbleToPlay)
const isAuthenticated = computed(() => store.state.isAuthenticated)
const unreadNotificationCount = ref(0)
const notificationSocket = ref(null)
const gameInviteTimeout = ref(null)
const gameInviteNotification = ref(null) // Add this line
const globalGame = ref(null)

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
        const data = JSON.parse(event.data);
        console.log('Notification received in App.vue:', data);
        
        // Handle game invites with detailed logging
        if (data.type === 'game_invite') {
          console.log('Game invite detected in App.vue:', {
            recipientId: data.recipient_id,
            myId: store.state.userId,
            match: parseInt(data.recipient_id) === parseInt(store.state.userId)
          });
          
          // Modified comparison that will work even if store.state.userId isn't set
          const currentUserId = store.state.userId || localStorage.getItem('userId');
          
          if (parseInt(data.recipient_id) === parseInt(currentUserId)) {
            console.log('This game invite is for me, handling it now');
            handleGameInvite(data);
          } else {
            console.log('This game invite is not for me:', {
              recipientId: parseInt(data.recipient_id),
              currentUserId: parseInt(currentUserId)
            });
          }
        }

        else if (data.type === 'game_accepted') {
          console.log('Game acceptance received in App.vue:', data);
          // If we're the original sender of the game invite
          const currentUserId = store.state.userId || localStorage.getItem('userId');
          if (parseInt(data.recipient_id) === parseInt(currentUserId)) {
            console.log('Our game invitation was accepted by:', data.sender_name);
            
            // The game window should already be open for the sender
            // This notification just confirms the recipient joined
          }
        }

        else if (data.type === 'game_declined') {
          console.log('Game decline received in App.vue:', data);
          
          // Get the current user ID 
          const currentUserId = store.state.userId || localStorage.getItem('userId');
          console.log('Current user ID:', currentUserId, 'Recipient ID:', data.recipient_id);
          
          if (parseInt(data.recipient_id) === parseInt(currentUserId)) {
            console.log('Our game invitation was declined by:', data.sender_name);
            
            // Force close the game window through multiple approaches
            if (globalGame.value) {
              console.log('GlobalGame ref found, forcing game window to close');
              
              // Call the method
              globalGame.value.closeGame();
              
              // Also directly force the state to be closed
              globalGame.value.showGameWindow = false;
              
              // Use store dispatch as backup
              store.dispatch('closeGame');
              
              // Verify on next tick if it worked
              nextTick(() => {
                console.log('Game window closed status:', !globalGame.value.showGameWindow);
                
                // If it's still open, try force closing again
                if (globalGame.value.showGameWindow) {
                  console.log('Window still open, forcing closure again');
                  globalGame.value.showGameWindow = false;
                  store.dispatch('closeGame');
                }
              });
            } else {
              console.error('GlobalGame ref is not available');
              // Try using store dispatch
              store.dispatch('closeGame');
            }
          } else {
            console.log('This game decline notification is not for us');
          }
        }
        // Update notification count for all notifications
        fetchUnreadNotificationCount();
      } catch (error) {
        console.error('Error processing notification:', error);
      }
    };

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
  
  // Launch the game
  globalGame.value.openGame({
    opponent: gameInviteNotification.value.sender,
    gameId: gameInviteNotification.value.gameId,
    isHost: false
  });
  
  // IMPORTANT: Send acceptance notification back to the host
  if (notificationSocket.value && notificationSocket.value.readyState === WebSocket.OPEN) {
    const acceptData = {
      type: 'game_accepted',
      game_id: gameInviteNotification.value.gameId,
      sender_id: store.state.userId,  // Current user is now the sender of acceptance
      recipient_id: gameInviteNotification.value.senderId,  // Original sender is now recipient
      sender_name: store.state.profile?.display_name || localStorage.getItem('username') || 'Player',
      recipient_name: gameInviteNotification.value.sender
    };
    
    console.log('Sending game acceptance notification:', acceptData);
    notificationSocket.value.send(JSON.stringify(acceptData));
  }
  
  // Clear the invitation
  if (gameInviteTimeout.value) {
    clearTimeout(gameInviteTimeout.value);
  }
  gameInviteNotification.value = null;
}

function declineGameInvite() {
  if (!gameInviteNotification.value || !notificationSocket.value) {
    console.log('No game invite to decline or socket not available');
    return;
  }

  console.log('Declining game invite with data:', {
    gameId: gameInviteNotification.value.gameId,
    recipientId: gameInviteNotification.value.senderId,
    senderId: store.state.userId
  });
  
  try {
    const token = localStorage.getItem('token');
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsHost = window.location.host;
    const gameWsUrl = `${wsProtocol}//${wsHost}/ws/game/${gameInviteNotification.value.gameId}/?token=${encodeURIComponent(token)}`;
    
    console.log('Connecting to game WebSocket to send decline:', gameWsUrl);
    const tempGameSocket = new WebSocket(gameWsUrl);
    
    tempGameSocket.onopen = () => {
      console.log('Connected to game socket to send decline message');
      tempGameSocket.send(JSON.stringify({
        type: 'player_declined'
      }));
      
      // Close the socket after sending
      setTimeout(() => tempGameSocket.close(), 1000);
    };
  } catch (error) {
    console.error('Error sending direct game decline:', error);
  }
  
  // Clear the invitation
  if (gameInviteTimeout.value) {
    clearTimeout(gameInviteTimeout.value);
  }
  gameInviteNotification.value = null;
}

// Add this function to update the user's language preference
async function updateLanguagePreference(lang) {
  if (!isAuthenticated.value) return;
  
  try {
    const token = localStorage.getItem('token');
    const response = await fetch('/api/user/profile/', {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ language: lang })
    });
    
    if (response.ok) {
      console.log('Language preference updated successfully');
      if (store.state.profile) {
        store.commit('updateProfile', { ...store.state.profile, language: lang });
      }
    } else {
      console.error('Failed to update language preference');
    }
  } catch (error) {
    console.error('Error updating language preference:', error);
  }
}

// Modify the language setter to update the backend
const setLocale = (value) => {
  locale.value = value;
  if (isAuthenticated.value) {
    updateLanguagePreference(value);
  }
};

// Use a computed property with getter and setter for locale
const userLocale = computed({
  get: () => locale.value,
  set: (value) => setLocale(value)
});

onMounted(async () => {
  let token = localStorage.getItem('token')
  const refreshToken = localStorage.getItem('refreshToken')
  console.log('Token status:', token ? 'Present' : 'Not found', 
              'Refresh token:', refreshToken ? 'Present' : 'Not found')

  const clearTokenAndRedirect = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('refreshToken')
    store.commit('setToken', null)
    if (router.currentRoute.value.path !== '/login') {
      router.push('/login')
    }
  }

  // If no access token but refresh token exists, try to refresh
  if ((!token || token === 'undefined' || token === 'null') && refreshToken) {
    try {
      console.log('No valid token but refresh token exists, trying to refresh');
      
      // Set refreshing state BEFORE starting the refresh
      store.commit('setIsRefreshing', true);
      
      if (typeof store._actions['refreshToken'] !== 'undefined') {
        token = await store.dispatch('refreshToken');
        console.log('Got new token from refresh:', token ? 'Success' : 'Failed');
        
        if (token) {
          // Successfully refreshed the token
          store.commit('setToken', token);

          // Force update authentication state
          store.commit('setIsAuthenticated', true);
  
          // Skip validation after refresh
          console.log('Token refreshed successfully, skipping validation');
          
          // Get user ID with the new token
          await fetchUserProfile(token);
          
          // Return early
          return;
        }
      } else {
        console.error('refreshToken action is not defined in the store');
        clearTokenAndRedirect();
        return;
      }
    } catch (error) {
      console.error('Failed to refresh token:', error);
      clearTokenAndRedirect();
      return;
    } finally {
      // Make sure we clear the refreshing state when done
      store.commit('setIsRefreshing', false);
    }
  } else if (!token || token === 'undefined' || token === 'null') {
    // No token and no refresh token
    console.log('No token and no refresh token, redirecting to login')
    clearTokenAndRedirect()
    return
  }

  // Only run the validation flow if we didn't just refresh the token
  try {
    // Only validate if we have a token
    if (token) {
      console.log('Validating existing token...')
      const response = await fetch('/api/auth/validate-token/', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (!response.ok) {
        console.error('Token validation failed with status:', response.status)
        
        // Try refreshing one more time if we have a refresh token
        if (refreshToken) {
          console.log('Token validation failed, trying to refresh token')
          try {
            token = await store.dispatch('refreshToken')
            if (token) {
              console.log('Refresh successful after validation failure')
              store.commit('setToken', token)
              await fetchUserProfile(token)
              return
            }
          } catch (refreshError) {
            console.error('Failed to refresh token after validation error:', refreshError)
            clearTokenAndRedirect()
            return
          }
        } else {
          clearTokenAndRedirect()
          return
        }
      }
      
      console.log('Token validated successfully')
    }

    // Get user ID with validated token
    await fetchUserProfile(token)
  } catch (error) {
    console.error('Authentication error:', error)
    clearTokenAndRedirect()
  }
  
  async function fetchUserProfile(token) {
    try {
      const userResponse = await fetch('/api/user/verify/', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (userResponse.ok) {
        const userData = await userResponse.json()
        store.commit('setUserId', userData.id)
        localStorage.setItem('userId', userData.id)
        console.log('User ID set in store:', userData.id)
        
        // Now also fetch the complete profile to get language preference
        const profileResponse = await fetch('/api/user/profile/', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })
        
        if (profileResponse.ok) {
          const profileData = await profileResponse.json()
          store.commit('updateProfile', profileData)
          
          // Update locale based on profile language
          if (profileData.language) {
            locale.value = profileData.language
            console.log('Language set from profile:', profileData.language)
          }
        }
      } else {
        console.error('Failed to verify user:', userResponse.status)
      }
    } catch (error) {
      console.error('Error fetching user profile:', error)
    }
  }
})

// Replace your second onMounted with this version
onMounted(() => {

  if (isAuthenticated.value) {
    locale.value = store.state.profile?.language || 'en'
  }
  else 
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

// Watch for authentication state changes
watch(() => isAuthenticated.value, async (newIsAuthenticated) => {
  if (newIsAuthenticated) {
    // User just logged in, fetch their profile to get language preference
    try {
      const token = localStorage.getItem('token')
      if (!token) return
      
      const profileResponse = await fetch('/api/user/profile/', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (profileResponse.ok) {
        const profileData = await profileResponse.json()
        
        // Update locale based on profile language
        if (profileData.language) {
          locale.value = profileData.language
          console.log('Language set after login:', profileData.language)
        }
      }
    } catch (error) {
      console.error('Error fetching language preference after login:', error)
    }
  } else {
    // User logged out, reset to default language
    locale.value = 'en'
  }
}, { immediate: true })

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
// provide the globalGame reference
provide('globalGame', globalGame);

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
      <select v-model="userLocale">
        <option v-for="lang in languages" :key="lang.code" :value="lang.code">
          {{ lang.name }}
        </option>
      </select>
    </div>
  </header>

  <RouterView />
  <GlobalGame ref="globalGame" />
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