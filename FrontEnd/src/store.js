import { createStore } from 'vuex';
import router from './router';
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000'
});

const store = createStore({
  state: {
    token: localStorage.getItem('authToken') || null,
    isAuthenticated: false,
    user: null,
  },

  mutations: {
    setToken(state, token) {
      state.token = token;
      state.isAuthenticated = !!token;
      if (token) {
        localStorage.setItem('authToken', token);
        api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      } else {
        localStorage.removeItem('authToken');
        delete api.defaults.headers.common['Authorization'];
      }
    },

    setUser(state, user) {
      state.user = user;
    },

    clearAuth(state) {
      state.token = null;
      state.user = null;
      state.isAuthenticated = false;
      localStorage.removeItem('authToken');
      delete api.defaults.headers.common['Authorization'];
    }
  },

  actions: {
    async loginAction({ commit }, { username, password }) {
      try {
        console.log('Attempting login with username:', username);
        const response = await api.post('/api/login/', {
          username,
          password
        });
        
        const { token, user } = response.data;
        commit('setToken', token);
        commit('setUser', user);
        
        await router.push({ name: 'Profile' });
        return response.data;
      } catch (error) {
        console.error('Login error:', error.response?.status);
        console.error('Error details:', error.response?.data);
        commit('clearAuth');
        throw error.response?.data || { message: 'Login failed' };
      }
    },

    async logoutAction({ commit }) {
      try {
        await api.post('/api/logout/');
      } catch (error) {
        console.error('Logout failed:', error);
      } finally {
        commit('clearAuth');
        await router.push({ name: 'Login' });
      }
    },

    
    async initializeAuth({ commit }) {
      const token = localStorage.getItem('authToken');
      if (!token) {
        commit('clearAuth');
        return false;
      }
      
      try {
        api.defaults.headers.common['Authorization'] = `Token ${token}`;
        commit('setToken', token);
        return true;
      } catch (error) {
        commit('clearAuth');
        return false;
      }
    }
    
  },

  getters: {
    isAuthenticated: state => state.isAuthenticated,
    currentUser: state => state.user,
    getToken: state => state.token
  }
});

api.interceptors.request.use(config => {
  const token = store.state.token;
  if (token) {
    config.headers.Authorization = `Token ${token}`; // Change here too
  }
  return config;
});

api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      store.commit('clearAuth');
      router.push({ name: 'Login' });
    }
    return Promise.reject(error);
  }
);

export default store;