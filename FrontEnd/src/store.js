import { createStore } from 'vuex';
import { getBaseUrl, getAuthEndpoints } from '@/services/ApiService';
import router from './router';
import axios from 'axios';

const baseUrl = getBaseUrl();
const authEndpoints = getAuthEndpoints(baseUrl);

const api = axios.create({
  baseURL: getBaseUrl(),
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  },
  withCredentials: true
});

const store = createStore({
  state: {
    token: localStorage.getItem('authToken') || null,
    isAuthenticated: false,
    user: null,
    api: api,
    errorMessage: null
  },

  mutations: {
    setToken(state, token) {
      state.token = token;
      state.isAuthenticated = !!token;
      if (token) {
        localStorage.setItem('authToken', token);
        api.defaults.headers.common['Authorization'] = `Token ${token}`;
      } else {
        localStorage.removeItem('authToken');
        delete api.defaults.headers.common['Authorization'];
      }
    },

    setUser(state, user) {
      state.user = user;
    },

    setAuthentication(state, token) {
      state.token = token;
      state.isAuthenticated = !!token;
    },
    
    setError(state, message) {
      state.errorMessage = message;
    },

    clearError(state) {
      state.errorMessage = null;
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
    async loginAction({ commit }, credentials) {
      commit('clearError');
      try {
        const response = await api.post(authEndpoints.login, credentials);
        
        if (response.data && response.data.token) {
          commit('setToken', response.data.token);
          commit('setUser', response.data.user);
          await router.push('/');
          return response.data;
        } else {
          throw new Error('Invalid response format');
        }
      } catch (error) {
        const errorMessage = error.response?.data?.message || error.message || 'Login failed';
        commit('setError', errorMessage);
        console.error('Login error:', errorMessage);
        throw new Error(errorMessage);
      }
    },

    async logoutAction({ commit }) {
      try {
        await api.post(authEndpoints.logout);
      } catch (error) {
        console.error('Logout error:', error);
      } finally {
        commit('clearAuth');
        await router.push('/login');
      }
    },

    async registerAction({ commit }, userData) {
      commit('clearError');
      try {
        const response = await api.post(authEndpoints.register, userData);
        
        if (response.status === 201 || response.status === 200) {
          await router.push('/login');
          return response.data;
        }
      } catch (error) {
        const errorMessage = error.response?.data?.message || error.message || 'Registration failed';
        commit('setError', errorMessage);
        throw new Error(errorMessage);
      }
    },

    async checkAuthAction({ commit }) {
      const token = localStorage.getItem('authToken');
      if (!token) {
        commit('clearAuth');
        return false;
      }

      try {
        const response = await api.get('/api/user/profile/');
        commit('setUser', response.data);
        commit('setToken', token);
        return true;
      } catch (error) {
        commit('clearAuth');
        return false;
      }
    },

    async updateProfileAction({ commit }, profileData) {
      try {
        const response = await api.put('/api/user/profile/', profileData);
        commit('setUser', response.data);
        return response.data;
      } catch (error) {
        const errorMessage = error.response?.data?.message || 'Profile update failed';
        commit('setError', errorMessage);
        throw new Error(errorMessage);
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
    getToken: state => state.token,
    getError: state => state.errorMessage,
    getApi: state => state.api
  }
});

// Request interceptor
api.interceptors.request.use(
  config => {
    config.baseURL = getBaseUrl();
    const token = store.state.token;
    if (token) {
      config.headers.Authorization = `Token ${token}`;
    }
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      store.commit('clearAuth');
      router.push('/login');
    }
    return Promise.reject(error);
  }
);

export default store;