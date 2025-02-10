<script setup>
import { RouterLink, RouterView, useRouter } from 'vue-router'
import HelloWorld from './components/HelloWorld.vue'
import { computed, onMounted } from 'vue'
import { useStore } from 'vuex'

const store = useStore()
const router = useRouter()
const isAuthenticated = computed(() => store.state.isAuthenticated)

function logout() {
  store.dispatch('logoutAction')
}

// Check authentication state on app load
onMounted(() => {
  let authToken = localStorage.getItem('authToken')
  console.log('Auth Token:', authToken) // Debugging log

  // Clear invalid tokens
  if (!authToken || authToken === 'undefined' || authToken === 'null') {
    localStorage.removeItem('authToken')
    authToken = null
  }

  const isAuthenticated = Boolean(authToken)
  store.commit('setAuthentication', isAuthenticated)
  console.log('Is Authenticated:', isAuthenticated) // Debugging log
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