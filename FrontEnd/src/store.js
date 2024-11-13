// store.js
import { createStore } from 'vuex';
import router from './router'; // Import the router

const store = createStore({
  state: {
    isAuthenticated: false, // This should be updated based on actual authentication status
    user: null, // Store the user data if needed
  },
  mutations: {
    setAuthentication(state, status) {
      console.log('Setting authentication status to:', status);
      state.isAuthenticated = status;
    },
    setUser(state, user) {
      state.user = user;
    },
    clearUserData(state) {
      state.user = null;
    }
  },
  actions: {
    async loginAction({ commit }, { username, password, csrftoken }) {
      try {
        // Perform the login API request
        const response = await fetch('/login/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken, // Add CSRF token to headers
          },
          body: JSON.stringify({
            username,
            password,
          })
        });

        if (response.ok) {
          const data = await response.json();
          commit('setAuthentication', true);
          commit('setUser', data.user); // Assuming the response contains user data
          router.push({ name: 'Profile' }); // Redirect to the profile page after successful login
        } else {
          console.error('Login failed:', response.status);
          throw new Error('Invalid credentials');
        }
      } catch (error) {
        console.error('Login error:', error);
        throw error;
      }
    },
    logout({ commit }) {
      commit('setAuthentication', false);
      commit('clearUserData');
      router.push({ name: 'Home' });
    }
  },
});

export default store;
