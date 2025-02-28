import { createStore } from 'vuex';
import { SERVICE_URLS } from '@/config/services';
import router from './router';
import axios from 'axios';

const axiosInstance = axios.create();

const store = createStore({
  state: {
    token: localStorage.getItem('token') || null,
    user: null,
    isAuthenticated: false,
    isAbleToPlay: true,
    profile: null
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

    setProfile(state, profile) {
      state.profile = profile;
    },

    setPlayerMode(state, isAbleToPlay) {
      state.isAbleToPlay = isAbleToPlay;
    },
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
    
    async logoutAction({ commit }) {
      commit('setToken', null)
      commit('setAuthenticated', false)
      localStorage.removeItem('token')
    }
    
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