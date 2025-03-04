import { createStore } from 'vuex';
import { SERVICE_URLS } from '@/config/services';
import router from './router';
import axios from 'axios';

const axiosInstance = axios.create();

const store = createStore({
  state: {
    token: localStorage.getItem('token') || null,
    isAuthenticated: !!(localStorage.getItem('token') || localStorage.getItem('refreshToken')),
    user: null,
    userId: localStorage.getItem('userId') || null,
    isAbleToPlay: true,
    profile: null,
    showGameWindow: false,
    gameData: null,
    isRefreshing: false,
  },

  mutations: {
    setToken(state, token) {
      state.token = token;
      // Update this line to check for refresh token too
      state.isAuthenticated = !!(token || localStorage.getItem('refreshToken'));
      if (token) {
        localStorage.setItem('token', token);
        axiosInstance.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      } else {
        localStorage.removeItem('token');
        delete axiosInstance.defaults.headers.common['Authorization'];
        // Don't set isAuthenticated to false here if refresh token exists
      }
    },

    setUser(state, user) {
      state.user = user;
    },

    setUserId(state, userId) {
      state.userId = userId
      // Also store in localStorage for persistence
      if (userId) {
        localStorage.setItem('userId', userId)
      } else {
        localStorage.removeItem('userId')
      }
    },

    setIsAuthenticated(state, value) {
      state.isAuthenticated = value;
    },

    setProfile(state, profile) {
      state.profile = profile;
    },

    setPlayerMode(state, isAbleToPlay) {
      state.isAbleToPlay = isAbleToPlay;
    },
    setGameWindow(state, status) {
      console.log('Store mutation: Setting game window to', status);
      state.showGameWindow = status;
    },
    setGameData(state, data) {
      state.gameData = data;
    },
    setIsRefreshing(state, isRefreshing) {
      state.isRefreshing = isRefreshing
    }
  },

  actions: {
    
    async initializeAuth({ commit, dispatch }) {
      const token = localStorage.getItem('token');
      if (token) {
        try {
          commit('setToken', token);
          return true;
        } catch (error) {
          commit('setToken', null);
          return false;
        }
      }
      return false;
    },

    async refreshToken({ commit }) {
      // Set refreshing state to true at the start
      commit('setIsRefreshing', true);
      
      const refreshToken = localStorage.getItem('refreshToken');
      
      if (!refreshToken) {
        // Set refreshing state to false on failure
        commit('setIsRefreshing', false);
        return Promise.reject('No refresh token available');
      }
      
      try {
        console.log('Attempting to refresh token with:', refreshToken.substring(0, 10) + '...');
        
        const response = await fetch('/api/auth/token/refresh/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            refresh: refreshToken
          })
        });
        
        if (!response.ok) {
          const errorText = await response.text();
          console.error('Refresh token response error:', response.status, errorText);
          // Set refreshing state to false on failure
          commit('setIsRefreshing', false);
          throw new Error(`Token refresh failed: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Token refresh successful, received new token');
        
        if (data.token || data.access) {
          const newToken = data.token || data.access;
          localStorage.setItem('token', newToken);
          commit('setToken', newToken);
          // Keep isRefreshing true - we'll clear it after navigation completes
          return newToken;
        } else {
          console.error('Invalid token refresh response format:', data);
          // Set refreshing state to false on failure
          commit('setIsRefreshing', false);
          throw new Error('Invalid token response format');
        }
      } catch (error) {
        console.error('Token refresh failed:', error);
        // Set refreshing state to false on any error
        commit('setIsRefreshing', false);
        return Promise.reject(error);
      }
    },
    
    // Add this new action to reset the refreshing state
    resetRefreshing({ commit }) {
      // Only reset isRefreshing, don't touch isAuthenticated
      commit('setIsRefreshing', false);
      
      // Make sure we're still authenticated if token was refreshed
      const token = localStorage.getItem('token');
      const refreshToken = localStorage.getItem('refreshToken');
      
      if (token || refreshToken) {
        // Make sure isAuthenticated is still true
        commit('setIsAuthenticated', true);
      }
    },
    
    async loginAction({ commit }, { accessToken, refreshToken }) {
      commit('setToken', accessToken);
      localStorage.setItem('refreshToken', refreshToken);
    },
    
    logoutAction({ commit }) {
      localStorage.removeItem('token')
      localStorage.removeItem('refreshToken')
      localStorage.removeItem('userId') // Also clear userId
      commit('setToken', null)
      commit('setUserId', null)
      return Promise.resolve()
    },
    
    startGame({ commit }, gameData) {
      commit('setGameData', gameData);
      commit('setGameWindow', true);
    },
    closeGame({ commit }) {
      console.log('Store action: Closing game window');
      commit('setGameWindow', false);
      commit('setGameData', null);
    },
  },

  getters: {
    getToken: state => state.token,
    isAuthenticated: state => {
      return !!(state.token || localStorage.getItem('refreshToken'));
    },
    currentUser: state => state.user,
    userProfile: state => state.profile,
    isAbleToPlay: state => state.isAbleToPlay,
    isRefreshing: state => state.isRefreshing,
  }
});

export default store;