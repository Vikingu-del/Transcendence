<script setup>
import { RouterLink, RouterView, useRouter } from 'vue-router'
import HelloWorld from './components/HelloWorld.vue'
import { computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useI18n } from 'vue-i18n'


const { t, locale } = useI18n()
const store = useStore()
const router = useRouter()
const isAbleToPlay = computed(() => store.state.isAbleToPlay)
const isAuthenticated = computed(() => store.state.isAuthenticated)

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

onMounted(() => {
  locale.value = 'en'
})

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
</template>

<style scoped>

.language-selector {
  position: fixed;
  top: 20px;
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
}
</style>