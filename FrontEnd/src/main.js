import './assets/main.css'

import { createApp } from 'vue'
import { createStore } from 'vuex'
import App from './App.vue'
import router from './router'
import axios from 'axios'

const app = createApp(App)

// Configure Axios to use the base URL of your Nginx gateway
axios.defaults.baseURL = 'https://localhost/api'; // This tells Axios to send all requests to Nginx, which will proxy them to the backend

// You can also add any global configuration here, such as headers, if needed.
axios.defaults.headers['Content-Type'] = 'application/json';

// Add Axios to the global app instance so you can use it throughout your components
app.config.globalProperties.$axios = axios;

const store = createStore({
  state: {
    user: null
  },
  mutations: {
    clearUserData(state) {
      state.user = null
    }
  },
})

app.use(router)
app.use(store) // Use the store

app.mount('#app')