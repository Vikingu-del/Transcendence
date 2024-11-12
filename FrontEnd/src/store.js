import { createStore } from 'vuex';
import router from './router'; // Import the router

const store = createStore({
  state: {
    isAuthenticated: false, // This should be updated based on actual authentication status
  },
  mutations: {
    setAuthentication(state, status) {
      state.isAuthenticated = status;
    }
  },
  actions: {
    loginAction({ commit }) {
      // Perform login logic, then set authentication status
      commit('setAuthentication', true);
      console.log('User authenticated, redirecting to profile...');
      // Redirect to profile page after successful login
      router.push({ name: 'Profile' });
    },
    logout({ commit }) {
      // Perform logout logic, then set authentication status
      commit('setAuthentication', false);
      // Redirect to home page after logout
      router.push({ name: 'Home' });
    }
  }
});

export default store;