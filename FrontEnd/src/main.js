// main.js
import './assets/main.css'
import { createApp } from 'vue'
import router from './router'
import App from './App.vue'
import store from './store' // Import the correct store.js
import axios from 'axios'

const app = createApp(App)

// Configure Axios to use the base URL of your Nginx gateway
axios.defaults.baseURL = 'https://localhost/'; // This tells Axios to send all requests to Nginx, which will proxy them to the backend
axios.defaults.headers['Content-Type'] = 'application/json';

// Add Axios to the global app instance so you can use it throughout your components
app.config.globalProperties.$axios = axios;

app.use(router)
app.use(store) // Use the correct store

app.mount('#app')
