<script setup>
import { RouterLink, RouterView, useRouter } from 'vue-router'
import HelloWorld from './components/HelloWorld.vue'
import { computed, onMounted } from 'vue'
import { useStore } from 'vuex'

const store = useStore()
const router = useRouter()
const isAbleToPlay = computed(() => store.state.isAbleToPlay)
const isAuthenticated = computed(() => store.state.isAuthenticated)

async function logout() {
  try {
    await store.dispatch('logoutAction')
    router.push('/login')
  } catch (error) {
    console.error('Logout error:', error)
  }
}

// Check authentication state on app load
onMounted(async () => {
  let token = localStorage.getItem('token')
  console.log('Token status:', token ? 'Present' : 'Not found')

  const clearTokenAndRedirect = () => {
    localStorage.removeItem('token')
    store.commit('setToken', null)
    store.commit('setIsAuthenticated', false)
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
    store.commit('setIsAuthenticated', true)
  } catch (error) {
    console.error('Token validation error:', error)
    clearTokenAndRedirect()
  }
})
</script>

<template>
  <header>
    <img alt="Vue logo" class="logo" src="@/assets/logo.svg" width="125" height="125" />

    <div class="wrapper">
      <HelloWorld msg="Transcendence" />
      <nav>
        <RouterLink to="/">Home</RouterLink>
        <RouterLink v-if="!isAuthenticated" to="/login">Login</RouterLink>
        <RouterLink v-if="!isAuthenticated" to="/register">Register</RouterLink>
        <RouterLink v-if="isAuthenticated" to="/profile">Profile</RouterLink>
        <RouterLink v-if="isAuthenticated" to="/friends">Friends</RouterLink>
        <RouterLink v-if="isAuthenticated" to="/Play">Play</RouterLink>
      </nav>
    </div>
  </header>

  <RouterView />
</template>

<style scoped>
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
}
</style>