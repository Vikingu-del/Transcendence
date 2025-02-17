import './assets/main.css'
import { createApp } from 'vue'
import router from './router'
import App from './App.vue'
import store from './store'
import axios from 'axios'

// Create app instance
const app = createApp(App)

// Configure Axios
axios.defaults.baseURL = 'https://localhost/'  // Change this to our server's URL
axios.defaults.headers['Content-Type'] = 'application/json'
app.config.globalProperties.$axios = axios // Make axios available globally through all components

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

// Execution Flow
// 1. Imports are processed
// 2. Vue app is created
// 3. Global configurations are set
// 4. Plugins are installed
// 5. Auth is initialized
// 6. App is mounted to DOM