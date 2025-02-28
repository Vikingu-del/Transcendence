import { createStore } from 'vuex';
import { SERVICE_URLS } from '@/config/services';
import router from './router';
import axios from 'axios';

const axiosInstance = axios.create();

const store = createStore({
  state: {
    token: localStorage.getItem('token') || null,
    isAuthenticated: !!localStorage.getItem('token'),
    user: null,
    isAuthenticated: false,
    userId: localStorage.getItem('userId') || null,
    isAbleToPlay: true,
    profile: null,
    showGameWindow: false,
    gameData: null,
  },

  mutations: {
    setToken(state, token) {
      state.token = token;
      state.isAuthenticated = !!token;
      if (token) {
        localStorage.setItem('token', token);
        axiosInstance.defaults.headers.common['Authorization'] = `Token ${token}`;
      } else {
        localStorage.removeItem('token');
        delete axiosInstance.defaults.headers.common['Authorization'];
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

    setProfile(state, profile) {
      state.profile = profile;
    },

    setPlayerMode(state, isAbleToPlay) {
      state.isAbleToPlay = isAbleToPlay;
    },
    setGameWindow(state, status) {
      state.showGameWindow = status;
    },
    setGameData(state, data) {
      state.gameData = data;
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
    
    async loginAction({ commit }, { accessToken, refreshToken }) {
      commit('setToken', accessToken);
      localStorage.setItem('refreshToken', refreshToken);
    },
    
    logoutAction({ commit }) {
      localStorage.removeItem('token')
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
      commit('setGameWindow', false);
      commit('setGameData', null);
    },
  },

  getters: {
    getToken: state => state.token,
    isAuthenticated: state => state.isAuthenticated,
    currentUser: state => state.user,
    userProfile: state => state.profile,
    isAbleToPlay: state => state.isAbleToPlay
  }
});

// Axios interceptors
axiosInstance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Token ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

axiosInstance.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      store.commit('setToken', null);
      store.commit('setUser', null);
      store.commit('setProfile', null);
      router.push('/login');
    }
    return Promise.reject(error);
  }
);

export default store;