import './assets/main.css'
import { createApp } from 'vue'
import router from './router'
import App from './App.vue'
import store from './store'
import axios from 'axios'

// Create app instance
const app = createApp(App)

// Configure Axios
axios.defaults.baseURL = 'https://10.12.12.5' // Used to be 'http://localhost:8000' but updated to the schools IP address
axios.defaults.headers['Content-Type'] = 'application/json'
app.config.globalProperties.$axios = axios

// Setup app with plugins
app.use(router)
app.use(store)

// Initialize auth before mounting
store.dispatch('initializeAuth').then(() => {
  app.mount('#app')
}).catch(error => {
  console.error('Auth initialization failed:', error)
  app.mount('#app')
})