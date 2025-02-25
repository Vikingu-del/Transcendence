import './assets/main.css'
import { createApp } from 'vue'
import router from './router'
import App from './App.vue'
import store from './store'
import axios from 'axios'
import i18n from './i18n'


// Create app instance
const app = createApp(App)


// Configure Axios
axios.defaults.baseURL = 'https://localhost/'
axios.defaults.headers['Content-Type'] = 'application/json'
app.config.globalProperties.$axios = axios

// Setup app with plugins
app.use(router)
app.use(store)
app.use(i18n)

// Initialize auth before mounting
store.dispatch('initializeAuth').then(() => {
  app.mount('#app')
}).catch(error => {
  console.error('Auth initialization failed:', error)
  app.mount('#app')
})